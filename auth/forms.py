# -*- coding:utf-8 -*-
import json
import re

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
import django.contrib.auth.forms as auth_forms
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import int_to_base36

from crispy_forms.layout import HTML, Layout

from auth.models import ActivationProfile
from grakon.utils import clean_html, form_helper
from users.models import Profile

password_digit_re = re.compile(r'\d')
password_letter_re = re.compile(r'[a-zA-Z]')

# TODO: do we need next hidden field?
layout = Layout(
    HTML(r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'),
)

class BaseRegistrationForm(forms.ModelForm):
    username = forms.RegexField(label=u'Имя пользователя (логин)', max_length=20, min_length=4, regex=r'^[\w\.]+$',
            help_text=u'Имя пользователя может содержать от 4 до 20 символов (латинские буквы, цифры, подчеркивания и точки).<br/>' \
                    u'<b>Под этим именем вас будут видеть другие пользователи.</b>')

    email = forms.EmailField(label=u'Электронная почта',
            help_text=u'<b>На ваш электронный адрес будет выслано письмо со ссылкой для активации аккаунта</b>')
    email1 = forms.EmailField(label=u'Электронная почта еще раз',
            help_text=u"<b>Внимание! Проверьте что правильность написания email'а. В случае ошибки ваш аккаунт не будет активирован.</b>")

    class Meta:
        model = Profile
        fields = ('username', 'last_name', 'first_name')

    def clean(self):
        if self.cleaned_data.get('email1') != self.cleaned_data.get('email'):
            raise forms.ValidationError(u'Введенные электронные адреса не совпадают!')

        return self.cleaned_data

    def save(self):
        username, email, password = self.cleaned_data['username'], \
                self.cleaned_data['email'], self.cleaned_data.get('password1', '')

        # TODO: make sure email is still unique (use transaction)
        user = User.objects.create_user(username, email, password)

        profile = user.get_profile()
        for field in self.Meta.fields:
            setattr(profile, field, self.cleaned_data[field])
        profile.save()

        user.is_active = False
        user.save()
        ActivationProfile.objects.init_activation(user)

        return user

class RegistrationForm(BaseRegistrationForm):
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(render_value=False),
            help_text=u'Пароль должен быть не короче <b>8 знаков</b> и содержать по крайней мере одну латинскую букву и одну цифру')
    password2 = forms.CharField(label=u'Подтвердите пароль', widget=forms.PasswordInput(render_value=False))

    helper = form_helper('register', u'Зарегистрироваться')
    helper.form_id = 'registration_form'
    helper.layout = layout

    #if CaptchaField:
    #    captcha = CaptchaField(label=u'Код проверки', error_messages = {'invalid': u'Неверный код проверки'},
    #            help_text=u'Пожалуйста, введите цифры и буквы с картинки слева, чтобы мы могли отличить вас от робота')

    def clean_password1(self):
        password = self.cleaned_data['password1']

        if password != '':
            if len(password) < 8:
                raise forms.ValidationError(u'Пароль должен содержать не менее 8 символов')

            if password_letter_re.search(password) is None or password_digit_re.search(password) is None:
                raise forms.ValidationError(u'Пароль должен содержать по крайней мере одну латинскую букву и одну цифру')

        return password

    def clean_password2(self):
        password2 = self.cleaned_data['password2']
        if self.cleaned_data.get('password1', '') != self.cleaned_data['password2']:
            raise forms.ValidationError(u'Введенные вами пароли не совпадают')
        return password2

class LoginForm(auth_forms.AuthenticationForm):
    helper = form_helper('login', u'Войти')
    helper.layout = Layout(HTML(
            r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = u'Имя пользователя или электронная почта'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(u'Пожалуйста, введите корретное имя пользователя или адрес электронной почты и пароль.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(u'Эта учётная запись неактивна')
        self.check_for_test_cookie()
        return self.cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'username')

    helper = form_helper('edit_profile', u'Сохранить')

    def clean_about(self):
        return clean_html(self.cleaned_data['about'])

# TODO: set minimum password complexity
class SetPasswordForm(auth_forms.SetPasswordForm):
    helper = form_helper('', u'Установить пароль')

# TODO: set minimum password complexity
class PasswordChangeForm(auth_forms.PasswordChangeForm):
    helper = form_helper('password_change', u'Сменить пароль')

class PasswordResetForm(auth_forms.PasswordResetForm):
    helper = form_helper('password_reset', u'Восстановить пароль')

    def save(self, **kwargs):
        for user in self.users_cache:
            subject = u'Смена пароля на grakon.org'
            message = render_to_string('letters/password_reset_email.html', {
                'uid': int_to_base36(user.id),
                'user': user,
                'token': kwargs['token_generator'].make_token(user),
                'URL_PREFIX': settings.URL_PREFIX,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
