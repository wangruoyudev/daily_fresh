from __future__ import absolute_import

from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import reverse
import time


@shared_task
def send_register_active_mail(receiver_list, user_name, token):
    print('延时前')
    time.sleep(5)
    print('延时后')
    subject = '欢迎注册快客金服'
    message = '12345'
    sender = settings.EMAIL_FROM
    receiver = receiver_list
    html_message = '''<h1>%s, 欢迎您成为快客金服的注册会员</h1><p>请点击下面的链接激活您的账户</p>
                            <p><a href="http://118.31.66.190:8083%s">http://118.31.66.190:8083%s</a></p>''' % (
        user_name,
        reverse('user:active_account', args=[token]),
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
