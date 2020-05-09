from __future__ import absolute_import

from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import reverse
import time
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django.template import loader
from django.conf import settings
import os


@shared_task
def add_test(num1, num2):
    print(num1+num2)


@shared_task
def create_static_index_html(request):
    print('执行生成静态页面的任务')
    goods_type_list = GoodsType.objects.all()
    goods_banner_list = IndexGoodsBanner.objects.all().order_by('index')
    goods_promotion_list = IndexPromotionBanner.objects.all().order_by('-index')

    for goods_type in goods_type_list:
        type_title_list = IndexTypeGoodsBanner.objects.filter(type=goods_type, display_type=0).order_by('index')
        type_image_list = IndexTypeGoodsBanner.objects.filter(type=goods_type, display_type=1).order_by('index')
        goods_type.type_title_list = type_title_list
        goods_type.type_image_list = type_image_list

    template = loader.get_template('goods/index.html')
    context = {'goods_type_list': goods_type_list,
               'goods_banner_list': goods_banner_list,
               'goods_promotion_list': goods_promotion_list,
               'cart_count': 0,
               'static_html': True}
    index_content = template.render(context, request)

    with open(os.path.join(settings.BASE_DIR, 'templates/static_index.html'), 'w') as f:
        f.write(index_content)
    print('生成完毕')


@shared_task
def send_register_active_mail(receiver_list, user_name, token, host):
    print('延时前')
    time.sleep(5)
    print('延时后')
    subject = '欢迎注册快客金服'
    message = '12345'
    sender = settings.EMAIL_FROM
    receiver = receiver_list
    html_message = '''<h1>%s, 欢迎您成为快客金服的注册会员</h1><p>请点击下面的链接激活您的账户</p>
                            <p><a href="http://%s%s">http://%s%s</a></p>''' % (
        user_name,
        host,
        reverse('user:active_account', args=[token]),
        host,
        reverse('user:active_account', args=[token]))

    print(sender)
    print(receiver)
    try:
        send_mail(
            subject,
            message,
            sender,
            receiver,
            fail_silently=False,
            html_message=html_message)
    except Exception as e:
        print('=======>', e)
