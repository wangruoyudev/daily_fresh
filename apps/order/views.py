from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from apps.goods.models import GoodsSKU
from apps.user.models import Address, User
from apps.order.models import OrderInfo, OrderGoods
from django_redis import get_redis_connection
from django.http import JsonResponse, HttpResponse
from django_redis import get_redis_connection
from datetime import datetime
from django.db import transaction
from alipay import AliPay
import os
from django.conf import settings
import time
# Create your views here.


class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        print('====>CreateOrderView-post:', request.POST)
        # goods_id_list = request.POST.get('sku_id', None)
        goods_id_list = request.POST.getlist('sku_id', [])
        print('===>goods_id_list:', goods_id_list)
        if goods_id_list is not None:
            conn = get_redis_connection('default')
            cart_key = 'cart_id%s' % request.user.id
            goods_sku_list = list()
            for goods_id in goods_id_list:
                try:
                    goods_sku = GoodsSKU.objects.get(id=goods_id)
                    goods_count = conn.hget(cart_key, goods_id)
                    goods_sku.cart_goods_count = goods_count.decode()
                    goods_sku_list.append(goods_sku)
                except GoodsSKU.DoesNotExist:
                    continue
        print('====>goods_sku_list:', goods_sku_list)
        try:
            address_user = User.objects.get(id=request.user.id)
            address = address_user.address_set.get(is_default=True)
        except Address.DoesNotExist:
            address = None
        context = {'goods_sku_list': enumerate(goods_sku_list, start=1),
                   'address': address}
        return render(request, 'order/place_order.html', context)


def create_fail_msg(msg):
    return {'ret': 'failed', 'msg': msg}


class SubmitOrderView(View):
    @transaction.atomic
    def post(self, request):
        print('====>SubmitOrderView-post: ', request.POST, datetime.now())
        # context = {'ret': 'failed'}
        if not request.user.is_authenticated:
            return JsonResponse(create_fail_msg('操作失败-用户没登陆'))
        address_id = request.POST.get('address_id', None)
        pay_style = request.POST.get('pay_style', None)
        goods_list = request.POST.getlist('goods_list', [])
        print(address_id, pay_style, goods_list)

        if not all([address_id, pay_style, goods_list]):
            return JsonResponse(create_fail_msg('操作失败-提交的数据有误'))

        #  todo 找到外键user和address
        try:
            order_user = User.objects.get(id=request.user.id)
            order_address = order_user.address_set.get(id=address_id)
        except User.DoesNotExist:
            return JsonResponse(create_fail_msg('操作失败-登录的用户找不到'))
        except Address.DoesNotExist:
            return JsonResponse(create_fail_msg('操作失败-提交的地址无效'))

        #  todo 判断支付方式
        try:
            pay_style = int(pay_style)
        except ValueError:
            return JsonResponse(create_fail_msg('操作失败-提交的支付方式非法'))

        if dict(OrderInfo.PAY_METHOD_CHOICES).get(pay_style, None) is None:
            return JsonResponse(create_fail_msg('操作失败-找不到该支付方式'))

        save_id = transaction.savepoint()

        try:
            #  todo 先生成个订单，方便下面商品模型数据外键使用
            order_id = '%s%s' % (datetime.now().strftime('%Y%m%d%H%M%S'), request.user.id)
            new_order = OrderInfo.objects.create(
                order_id=order_id,
                user=order_user,
                addr=order_address,
                pay_method=pay_style,
                total_count=0,
                total_price=0,
                transit_price=0.00,
                order_status=1,
                trade_no='')
            new_order.save()

            #  todo 处理购物车生成总价和数量,同时生成订单的商品模型数据
            conn = get_redis_connection('default')
            cart_key = 'cart_id%s' % request.user.id
            total_count = 0
            tatal_price = 0

            for cart_goods_id in goods_list:
                for i in range(3):
                    cart_goods_count = int(conn.hget(cart_key, cart_goods_id))
                    # goods_sku = GoodsSKU.objects.get(id=cart_goods_id)
                    # todo 悲观锁，这里会阻塞， 事务结束后会解阻塞
                    # goods_sku = GoodsSKU.objects.select_for_update().get(id=cart_goods_id)
                    # todo  尝试一下乐观锁，正常读取
                    goods_sku = GoodsSKU.objects.get(id=cart_goods_id)
                    # import time
                    # time.sleep(5)
                    #  todo # 比较一下要买的数量和库存
                    if cart_goods_count > goods_sku.stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse(create_fail_msg('操作失败-商品库存不足'))

                    #  更新商品的库存和销量
                    # goods_sku.stock -= cart_goods_count
                    # goods_sku.sales += cart_goods_count
                    # goods_sku.save()

                    #  todo 只有当刚刚查到的库存跟现在的存库相等的时候才更新
                    print('开始实行乐观查询', datetime.now())
                    row = GoodsSKU.objects.filter(id=goods_sku.id, stock=goods_sku.stock)\
                        .update(stock=goods_sku.stock-1, sales=goods_sku.sales+1)
                    print('乐观查询结束', datetime.now())
                    print('第%d次,结果为%s' % (i, row), datetime.now())
                    if row == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse(create_fail_msg('操作失败-库存问题导致失败'))
                        continue

                    cart_goods_price = cart_goods_count * goods_sku.price
                    print(cart_goods_count, cart_goods_price)
                    order_goods = OrderGoods.objects.create(
                        order=new_order,
                        sku=goods_sku,
                        count=cart_goods_count,
                        price=cart_goods_price,
                        comment='')
                    order_goods.save()

                    total_count += cart_goods_count
                    tatal_price += cart_goods_price

                    break
            print('购物车总数量和价格', total_count, '%.2f' % tatal_price, datetime.now())

            new_order.total_count = total_count
            new_order.total_price = tatal_price
            new_order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            print(e)
            return JsonResponse(create_fail_msg('操作失败-提交订单失败'))

        transaction.savepoint_commit(save_id)

        conn.hdel(cart_key, *goods_list)

        # print('视图结束前延迟5S', datetime.now())
        # time.sleep(5)

        return JsonResponse({'ret': 'success', 'msg': '提交成功'})


app_private_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')).read()
alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/ali_public_key.pem')).read()


class AliPayView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(create_fail_msg('用户未登录'))

        order_id = request.POST.get('order_id', None)
        if order_id is None:
            return JsonResponse(create_fail_msg('订单无效'))

        print('======>order_id:', order_id)

        try:
            pay_order = OrderInfo.objects.get(order_id=order_id, order_status=1)  # pay_method=3
        except OrderInfo.DoesNotExist:
            return JsonResponse(create_fail_msg('该订单不存在或无法支付'))

        print('====>pay_order', pay_order)

        alipay = AliPay(
            appid="2016102300743845",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True,  # 默认False
        )
        alipay_ret = alipay.api_alipay_trade_page_pay(
            subject="测试订单",
            out_trade_no=pay_order.order_id,
            total_amount=str(pay_order.total_price),
        )

        print('===>alipay_ret:', alipay_ret)

        ali_url = 'https://openapi.alipaydev.com/gateway.do?%s' % alipay_ret

        context = {'ret': 'success', 'msg': '提交成功', 'ali_url': ali_url}
        return JsonResponse(context)


def create_return_ajax(status, code, msg):
    return {
        'ret': status,
        'code': code,
        'msg': msg,
    }


class QueryTradeStatus(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(create_fail_msg('用户未登录'))

        order_id = request.GET.get('order_id', None)
        if order_id is None:
            return JsonResponse(create_fail_msg('订单无效'))

        print('======>order_id:', order_id)

        try:
            pay_order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return JsonResponse(create_fail_msg('该订单不存在'))
        alipay = AliPay(
            appid="2016102300743845",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True,  # 默认False
        )
        for i in range(12):
            ret = alipay.api_alipay_trade_query(out_trade_no=pay_order.order_id)
            print('===>query-alipay-ret:', ret)
            if ret['code'] == '10000' and ret['msg'] == 'Success' and ret['trade_status'] == 'TRADE_SUCCESS':
                pay_order.order_status = 4
                pay_order.trade_no = ret['trade_no']
                pay_order.save()
                return JsonResponse(create_return_ajax('success', '0', '付款成功'))
            else:
                time.sleep(10)
                continue

        return JsonResponse(create_return_ajax('failed', '3', '付款失败'))


class OrderEvaluate(View):
    def get(self, request, order_id):
        print('====>order_id:', order_id)
        try:
            evaluate_order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return HttpResponse('出错了-订单不存在')
        evaluate_order.payment_status = OrderInfo.ORDER_STATUS[evaluate_order.order_status]
        context = {
            'evaluate_order': evaluate_order,
        }
        return render(request, 'user/user_order_comment.html', context)

    def post(self, request, order_id):
        print('====>OrderEvaluate-post:', request.POST)
        if order_id is None:
            return HttpResponse('出错了-订单号为空')

        total_count = request.POST['total_count']
        total_count = int(total_count)

        for i in range(1, total_count+1):
            order_goods_id = request.POST.get('order_goods_id_%s' % i)
            try:
                order_goods = OrderGoods.objects.get(id=order_goods_id)
            except OrderGoods.DoesNotExist:
                continue
            order_goods.comment = request.POST.get('content_%s' % i)
            order_goods.save()

        try:
            evaluate_order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return HttpResponse('出错了-订单不存在')

        evaluate_order.order_status = 5
        evaluate_order.save()
        return redirect(reverse('user:order', kwargs={'page_name': 1}))


