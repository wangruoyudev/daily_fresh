from django.shortcuts import render, reverse, redirect
from django.views.generic import View
from apps.user.models import User
from apps.goods.models import GoodsType
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import SignatureExpired
from django.http import HttpResponse, HttpRequest
from .tasks import send_register_active_mail
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(View):

    def get(self, request):
        if 'username' in request.COOKIES:
            user_name = request.COOKIES.get('username')
            checked = 'checked'
        else:
            user_name = ''
            checked = ''

        return render(request, 'user/login.html',
                      {'username': user_name, 'checked': checked})

    def post(self, request):
        print(request.POST)
        user_name = request.POST['username']
        password = request.POST['pwd']
        print('===>username:', user_name)
        print('===>passphrase:', password, ' and type is: ', type(password))
        data_error = None
        if not all([user_name, password]):
            data_error = {'error_msg': '请填写完整信息'}

        each_user = User.objects.filter(username=user_name)
        print('=>each_user:', each_user)
        is_active = 1
        if each_user.count() == 1:
            is_active = each_user.first().is_active

        user = authenticate(request, username=user_name, password=password)
        print('----->', user)
        if user is not None:
            login(request, user)
            print('get:',request.GET)

            redirect_url = request.GET.get('next', reverse('user:index'))
            response = redirect(redirect_url)

            if request.POST.get('remember') == 'on':
                response.set_cookie('username', user_name, 14 * 24 * 3600)
            else:
                response.delete_cookie('username')
            return response
        else:
            if is_active == 1:
                data_error = {'error_msg': '用户名和密码错误'}
            else:
                data_error = {'error_msg': '该用户还未激活'}
        return render(request, 'user/login.html', data_error)
        # return HttpResponse(data_error.values())


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('user:index'))


class RegisterView(LoginRequiredMixin, View):
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

        print(
            '====>pwd:',
            reg_data['pwd'],
            ' and type is: ',
            type(
                reg_data['pwd']))

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
        send_register_active_mail.delay(
            [reg_data['email']], reg_user.username, token, host)

        return render(request, 'user/reg_success.html')


class ActiveAccount(LoginRequiredMixin, View):
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


class IndexView(View):
    def get(self, request):
        return render(request, 'user/index.html')


@login_required(login_url='/user/register')
def userinfo(request):
    print('====>session time:', cache.ttl('django.contrib.sessions.cachequmpbccpxasfweqeh6zb6c8q7nejbtfh'))
    return render(request, 'user/user_center_info.html', {'page': 'info'})


class UserInfo(LoginRequiredMixin, View):
    # login_url = '/user/register'
    # redirect_field_name = 'redirect_to' # 改变参数的默认key值，默认是next
    def get(self, request):
        print('==>user:', request.user, type(request.user))
        return render(request, 'user/user_center_info.html', {'page': 'info'})


class UserOrder(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user/user_center_order.html', {'page': 'order'})


class UserAddress(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user/user_center_site.html', {'page': 'address'})


class TestView(View):
    def get(self, request):
        pic = GoodsType.objects.get(name='云图片测试')
        print('===>pic-type:', type(pic))
        print('===>pic:', pic)
        print('===>pic-image-type:', type(pic.image))
        return render(request, 'user/test.html', {'pic': pic})



