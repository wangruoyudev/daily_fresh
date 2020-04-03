from django.shortcuts import render, reverse, redirect
from django.views.generic import View
from .models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import SignatureExpired
from django.http import HttpResponse
from .tasks import send_register_active_mail



class LoginView(View):

    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        pass


class RegisterView(View):
    def get(self, request):
        # print(request.scheme)
        # print('request.META-HTTP_HOST------->')
        # print(request.META['HTTP_HOST'])
        return render(request, 'user/register.html')

    def post(self, request):
        print(request.POST)
        reg_data = request.POST
        data_error = None
        if not all([reg_data['user_name'], reg_data['email'],
                    reg_data['pwd'], reg_data['cpwd']]):
            data_error = {'error_msg': '请填写完整信息'}
        allow = reg_data.get('allow')
        if allow != 'on':
            data_error = {'error_msg': '请勾选使用协议'}

        try:
            reg_user = User.objects.get(username=reg_data['user_name'])
        except User.DoesNotExist:
            reg_user = None

        if reg_user:
            data_error = {'error_msg': '用户名已存在'}

        if data_error:
            return render(request, 'user/register.html', data_error)

        reg_user = User.objects.create_user(username=reg_data['user_name'],
                                            email=reg_data['email'],
                                            password=reg_data['pwd'])
        reg_user.is_active = 0
        reg_user.save()

        serializer = Serializer(settings.SECRET_KEY)
        info = {'confirm': reg_user.id}
        token = serializer.dumps(info)
        token = token.decode()
        host = request.META['HTTP_HOST']

        # send_register_active_mail([reg_data['email']], reg_user.username, token)
        send_register_active_mail.delay([reg_data['email']], reg_user.username, token, host)

        return render(request, 'user/reg_success.html')


class ActiveAccount(View):
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY)
        try:
            ob = serializer.loads(token)
            user = User.objects.get(id=ob['confirm'])
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired:
            return HttpResponse('<h1>激活链接已过期</h1>')

