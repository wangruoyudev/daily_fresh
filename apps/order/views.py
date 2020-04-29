from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from apps.goods.models import GoodsSKU
from apps.user.models import Address, User
from apps.order.models import OrderInfo, OrderGoods
from django_redis import get_redis_connection
from django.http import JsonResponse
from django_redis import get_redis_connection
from datetime import datetime
from django.db import transaction
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
        print('====>SubmitOrderView-post: ', request.POST)
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
                cart_goods_count = int(conn.hget(cart_key, cart_goods_id))
                # goods_sku = GoodsSKU.objects.get(id=cart_goods_id)
                # todo 悲观锁，这里会阻塞， 事务结束后会解阻塞
                # goods_sku = GoodsSKU.objects.select_for_update().get(id=cart_goods_id)
                # todo  尝试一下乐观锁，正常读取
                goods_sku = GoodsSKU.objects.get(id=cart_goods_id)
                import time
                time.sleep(10)
                #  todo # 比较一下要买的数量和库存
                if cart_goods_count > goods_sku.stock:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse(create_fail_msg('操作失败-商品库存不足'))

                cart_goods_price = cart_goods_count * goods_sku.price
                print(cart_goods_count, cart_goods_price)
                order_goods = OrderGoods.objects.create(
                    order=new_order,
                    sku=goods_sku,
                    count=cart_goods_count,
                    price=cart_goods_price,
                    comment='')
                order_goods.save()

                #  更新商品的库存和销量
                # goods_sku.stock -= cart_goods_count
                # goods_sku.sales += cart_goods_count
                # goods_sku.save()

                #  todo 只有当刚刚查到的库存跟现在的存库相等的时候才更新
                row = GoodsSKU.objects.filter(id=goods_sku.id, stock=goods_sku.stock)\
                    .update(stock=goods_sku.stock-1, sales=goods_sku.sales+1)
                if row == 0:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse(create_fail_msg('操作失败-库存已经发生了变化'))

                total_count += cart_goods_count
                tatal_price += cart_goods_price

            print(total_count, '%.2f' % tatal_price)

            new_order.total_count = total_count
            new_order.total_price = tatal_price
            new_order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            print(e)
            return JsonResponse(create_fail_msg('操作失败-提交订单失败'))

        transaction.savepoint_commit(save_id)

        conn.hdel(cart_key, *goods_list)

        return JsonResponse({'ret': 'success', 'msg': '提交成功'})
