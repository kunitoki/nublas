import os
import re
import random
import datetime
import hashlib
from cStringIO import StringIO
from django import forms
from django import http
from django.db import transaction
from django.db.models import Q
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse, Resolver404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.models import Site
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt

from ...conf import settings
#from ...db.fields import currency, captcha
#from ...signals import user_registered, user_activated, user_profile_changed
#from ...tasks import GearmanClient
from ..forms import BaseForm, BaseAuthValidatingForm
from ..skins import get_skin_relative_path

import logging
logger = logging.getLogger(__name__)

__all__ = [ "LoginView", "LogoutView", "RegisterView", "ActivateView",
            "LostPasswordView", "LostPasswordChangeView", "LostUsernameView",
            "ProfileView", "SuperuserView" ]


#==============================================================================
class LoginForm(BaseForm):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    redirect_to = forms.CharField(initial='', required=False)
    remember = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(LoginForm, self).__init__(*args, **kwargs)

class LoginFormCaptcha(BaseForm):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    redirect_to = forms.CharField(initial='', required=False)
    remember = forms.BooleanField(initial=False, required=False)
    #captcha = captcha.ReCaptchaField()

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(LoginFormCaptcha, self).__init__(*args, **kwargs)
        #self.fields['captcha'] = captcha.ReCaptchaField(remoteip=request.META['REMOTE_ADDR'])

def _login_retries_exceeded(session):
    return session.get('login_retry', 0) > 3

def _update_login_retries(session):
    session['login_retry'] = session.get('login_retry', 0) + 1

def _reset_login_retries(session):
    session['login_retry'] = 0

class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        form_class = LoginFormCaptcha if _login_retries_exceeded(request.session) else LoginForm

        if request.method == 'POST':
            form = form_class(request.POST, request=request)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                redirect_to = form.cleaned_data['redirect_to']
                remember = form.cleaned_data['remember']
                print remember
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        # login
                        login(request, user)
                        # message user
                        messages.success(request, _('User logged in, welcome %s !' % user.get_full_name()))
                        # remember button
                        if not remember:
                            request.session.set_expiry(0)
                        # redirect processing
                        if not redirect_to:
                            redirect_to = settings.LOGIN_REDIRECT_URL
                        ## if user already selected the default language, set it now
                        #lang_code = user.preferred_language
                        #if lang_code:
                        #    translation.activate(lang_code)
                        #    request.LANGUAGE_CODE = translation.get_language()
                        #    request.session['django_language'] = lang_code
                        _reset_login_retries(request.session)
                        return HttpResponseRedirect(redirect_to)
                    else:
                        _update_login_retries(request.session)
                        messages.error(request, _('Account has been disabled.'))
                else:
                    form.has_errors = True
                    _update_login_retries(request.session)
                    messages.error(request, _('Invalid username or password.'))
            else:
                # TODO - make this better
                logger.debug(form.errors)
                _update_login_retries(request.session)
                messages.error(request, _('Invalid login data provided.'))
        else:
            form = form_class(initial=request.GET, request=request)

        return render_to_response(get_skin_relative_path('views/auth/login.html'),
                                  RequestContext(request, { 'form': form }))


#==============================================================================
class LogoutView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        # logout
        logout(request)
        # reset login retries
        _update_login_retries(request.session)
        # message the user
        messages.success(request, _('User logout successfully.'))
        # Redirect to a success
        return HttpResponseRedirect(settings.INDEX_URL)


#==============================================================================
class RegisterForm(BaseAuthValidatingForm):
    username = forms.CharField(max_length=30, required=True)
    password1 = forms.CharField(max_length=60, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=60, required=True, widget=forms.PasswordInput())
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    #captcha = captcha.ReCaptchaField()

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(RegisterForm, self).__init__(*args, **kwargs)
        #self.fields['captcha'] = captcha.ReCaptchaField(remoteip=request.META['REMOTE_ADDR'])

    def clean_username(self):
        return self.validate_new_username(self.cleaned_data['username'])

    def clean_password1(self):
        return self.validate_password(self.cleaned_data['password1'])

    def clean_password2(self):
        return self.validate_password(self.cleaned_data['password2'])

    def clean_email(self):
        return self.validate_new_email(self.cleaned_data['email'])

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if not self.validate_passwords(password1, password2):
            msg = _('Passwords do not match')
            self._errors['password1'] = self.error_class([msg])
            self._errors['password2'] = self.error_class([msg])
            if cleaned_data.has_key('password1'):
                del cleaned_data['password1']
            if cleaned_data.has_key('password2'):
                del cleaned_data['password2']
        return cleaned_data

class RegisterView(View):
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        created = False
        if request.method == 'POST':
            form = RegisterForm(request.POST, request=request)
            if form.is_valid():
                UserModel = get_user_model()
                with transaction.commit_on_success():
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password1']
                    first_name = form.cleaned_data['first_name']
                    last_name = form.cleaned_data['last_name']
                    email = form.cleaned_data['email']

                    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                    activation_key = hashlib.sha1(salt + username).hexdigest()
                    key_expires = timezone.now() + datetime.timedelta(2)

                    # Create and save the user
                    u = UserModel.objects.create_user(username,
                                                      email,
                                                      password)
                    u.first_name = first_name
                    u.last_name = last_name
                    u.is_active = False
                    u.activation_key = activation_key
                    u.key_expires = key_expires
                    u.save()

                    ## Send an email with the confirmation
                    #site_name = Site.objects.get_current().name
                    #site_url = settings.SITE_URL # TODO - think a better way
                    #email_subject = _('Your %s account confirmation') % (site_name)
                    #email_body = render_to_string('base/user/emails/register.txt', { 'first_name': u.first_name,
                    #                                                                 'last_name': u.last_name,
                    #                                                                 'activation_key': activation_key,
                    #                                                                 'site_name': site_name,
                    #                                                                 'site_url': site_url })
                    #
                    ## Send it user gearman tasks
                    #client = GearmanClient()
                    #client.dispatch_background_task('nublas-sendmail',
                    #                                kwargs={ 'subject': email_subject,
                    #                                         'body': email_body,
                    #                                         'to': [ u.email ],
                    #                                         'headers': { 'Reply-To': settings.REPLY_TO }})

                    created = True

                    # Send registration signal
                    #user_registered.send_robust(sender=get_user_model(), user=u, request=request)

                    messages.success(request, _('Registration done successfully. Please check your mail for confirmation.'))
                    return HttpResponseRedirect(settings.INDEX_URL)
            else:
                # TODO - make this better
                print(form.errors)
                messages.error(request, _('Error processing the registration form.'))
        else:
            form = RegisterForm(initial=request.GET, request=request)

        return render_to_response(get_skin_relative_path('views/auth/register.html'),
                                  RequestContext(request, { 'form': form,
                                                            'created': created }))


#==============================================================================
class ActivateView(View):
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        UserModel = get_user_model()

        activation_key = kwargs.get('activation_key')
        u = get_object_or_404(UserModel, activation_key=activation_key)

        # TODO - handle gracefully does not exists

        if u.is_active:
            if request.user.is_authenticated():
                messages.info(request, _('User is already active and authenticated.'))
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.info(request, _('User is already active. Please login.'))
                return HttpResponseRedirect(settings.LOGIN_URL)

        if u.key_expires < timezone.now():
            return render_to_response(get_skin_relative_path('views/auth/activate.html'),
                                      RequestContext(request, { 'expired': True }))

        with transaction.commit_on_success():
            # Set user active
            u.is_active = True
            u.activation_key = None
            u.key_expires = None
            u.save()

            # Send activation signal
            #user_activated.send_robust(sender=get_user_model(), user=u, request=request)

        return render_to_response('base/user/activate.html', RequestContext(request, {}))


#==============================================================================
class LostPasswordForm(BaseAuthValidatingForm):
    email = forms.EmailField(required=True)
    #captcha = captcha.ReCaptchaField()

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(LostPasswordForm, self).__init__(*args, **kwargs)
        #self.fields['captcha'] = captcha.ReCaptchaField(remoteip=request.META['REMOTE_ADDR'])
        self.user = None

    def clean_email(self):
        email = self.validate_existing_email(self.cleaned_data['email'])
        self.user = get_user_model().objects.get(email=email)
        return email

class LostPasswordChangeForm(BaseAuthValidatingForm):
    password1 = forms.CharField(max_length=60, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=60, required=True, widget=forms.PasswordInput())

    def clean_password1(self):
        return self.validate_password(self.cleaned_data['password1'])

    def clean_password2(self):
        return self.validate_password(self.cleaned_data['password2'])

    def clean(self):
        cleaned_data = super(LostPasswordChangeForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if not self.validate_passwords(password1, password2):
            msg = _('Passwords do not match')
            self._errors['password1'] = self.error_class([msg])
            self._errors['password2'] = self.error_class([msg])
            if cleaned_data.has_key('password1'):
                del cleaned_data['password1']
            if cleaned_data.has_key('password2'):
                del cleaned_data['password2']
        return cleaned_data

class LostPasswordView(View):
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        sent = False
        if request.method == 'POST':
            form = LostPasswordForm(request.POST, request=request)
            if form.is_valid() and form.user:
                email = form.cleaned_data['email']

                salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                lost_password_key = hashlib.sha1(salt + email).hexdigest()
                key_expires = timezone.now() + datetime.timedelta(2)

                # Create and save their profile
                if form.user:
                    u = form.user
                    u.lost_password_key = lost_password_key
                    u.lost_password_key_expires = key_expires
                    u.save()

                    ## Send an email with the confirmation
                    #site_name = Site.objects.get_current().name
                    #site_url = settings.SITE_URL
                    #email_subject = _('Your %s lost password recovery') % (site_name)
                    #email_body = render_to_string('base/user/emails/lost_password.txt', { 'first_name': u.first_name,
                    #                                                                      'last_name': u.last_name,
                    #                                                                      'lost_password_key': lost_password_key,
                    #                                                                      'site_name': site_name,
                    #                                                                      'site_url': site_url })
                    ## Send it with gearman
                    #client = GearmanClient()
                    #client.dispatch_background_task('nublas-sendmail',
                    #                                kwargs={ 'subject': email_subject,
                    #                                         'body': email_body,
                    #                                         'to': [ u.email ],
                    #                                         'headers': { 'Reply-To': settings.REPLY_TO }})
                    #sent = True

                    messages.success(request, _('Recovery done successfully. Please check your mail for completing the request.'))
                else:
                    messages.error(request, _('Something went wrong processing the recovery. Please contact the administrators.'))

                return HttpResponseRedirect(settings.INDEX_URL)
            else:
                # TODO - make this better
                print(form.errors)
                messages.error(request, _('Error processing the password recovery form.'))
        else:
            form = LostPasswordForm(initial=request.GET, request=request)

        return render_to_response(get_skin_relative_path('views/auth/password_lost.html'),
                                  RequestContext(request, { 'form': form,
                                                            'sent': sent }))


class LostPasswordChangeView(View):
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        UserModel = get_user_model()

        lost_password_key = kwargs.get('lost_password_key')
        u = get_object_or_404(UserModel, lost_password_key=lost_password_key)

        # TODO - handle gracefully does not exists

        if not u.is_active:
            messages.warning(request, _('User has been deactivated. Please contact the administrator.'))
            return HttpResponseRedirect(settings.INDEX_URL)
        else:
            if request.user.is_authenticated():
                messages.warning(request, _('User is already active and authenticated.'))
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        if u.lost_password_key_expires < timezone.now():
            return render_to_response(get_skin_relative_path('views/auth/password_change.html'),
                                      RequestContext(request, { 'expired': True }))

        if request.method == 'POST':
            form = LostPasswordChangeForm(request.POST)
            if form.is_valid():
                with transaction.commit_on_success():
                    password = form.cleaned_data['password1']

                    # change user password
                    u.set_password(password)
                    # reset change password keys
                    u.lost_password_key = None
                    u.lost_password_key_expires = None
                    u.save()

                    # signal of a profile change
                    #user_profile_changed.send_robust(sender=get_user_model(), user=u, request=request)

                    messages.success(request, _('Password changed successfully.'))
                    return HttpResponseRedirect(settings.LOGIN_URL)
            else:
                # TODO - make this better
                print(form.errors)
                messages.error(request, _('Error changing password.'))
        else:
            form = LostPasswordChangeForm(initial=request.GET)

        return render_to_response(get_skin_relative_path('views/auth/password_change.html'),
                                  RequestContext(request, { 'form': form }))


#==============================================================================
class LostUsernameForm(BaseAuthValidatingForm):
    email = forms.EmailField(required=True)
    #captcha = captcha.ReCaptchaField()

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(LostUsernameForm, self).__init__(*args, **kwargs)
        #self.fields['captcha'] = captcha.ReCaptchaField(remoteip=request.META['REMOTE_ADDR'])
        self.user = None

    def clean_email(self):
        email = self.validate_existing_email(self.cleaned_data['email'])
        self.user = get_user_model().objects.get(email=email)
        return email


class LostUsernameView(View):
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        sent = False
        if request.method == 'POST':
            form = LostUsernameForm(request.POST, request=request)
            if form.is_valid() and form.user:
                # TODO - mark the user that he selected to recover the username

                ## Send an email with the username
                #site_name = Site.objects.get_current().name
                #site_url = settings.SITE_URL # TODO - think a better way
                #email_subject = _('Your %s lost username recovery') % (site_name)
                #email_body = render_to_string('base/user/emails/lost_username.txt', { 'first_name': form.user.first_name,
                #                                                                      'last_name': form.user.last_name,
                #                                                                      'lost_username': form.user.username,
                #                                                                      'site_name': site_name,
                #                                                                      'site_url': site_url })
                #
                ## Send it with gearman
                #client = GearmanClient()
                #client.dispatch_background_task('nublas-sendmail',
                #                                kwargs={ 'subject': email_subject,
                #                                         'body': email_body,
                #                                         'to': [ form.user.email ],
                #                                         'headers': { 'Reply-To': settings.REPLY_TO }})
                #
                #sent = True

                messages.success(request, _('Recovery done successfully. Please check your mail for completing the request.'))
                return HttpResponseRedirect(settings.INDEX_URL)
            else:
                # TODO - make this better
                print(form.errors)
                messages.error(request, _('Error processing the username recovery form.'))
        else:
            form = LostUsernameForm(initial=request.GET, request=request)

        return render_to_response(get_skin_relative_path('views/auth/username_lost.html'),
                                  RequestContext(request, { 'form': form,
                                                            'sent': sent }))


#==============================================================================
class ProfileForm(BaseAuthValidatingForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(max_length=60, required=False, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=60, required=False, widget=forms.PasswordInput())

    if settings.LANGUAGES:
        preferred_language = forms.TypedChoiceField(label=_('Preferred language:'),
                                                    required=False,
                                                    empty_value=settings.LANGUAGES[0][0],
                                                    choices=settings.LANGUAGES)

    ## TODO - this creates problems in demo
    #preferred_currency = forms.TypedChoiceField(label=_('Preferred currency:'),
    #                                            required=True,
    #                                            empty_value=currency.PAYPAL_CURRENCIES[0][0],
    #                                            choices=currency.PAYPAL_CURRENCIES)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.UserModel = get_user_model()
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        return self.validate_new_email(self.cleaned_data['email'], ~Q(pk__exact=self.request.user.pk))

    def clean_password1(self):
        return self.validate_password(self.cleaned_data['password1'], strict=False)

    def clean_password2(self):
        return self.validate_password(self.cleaned_data['password2'], strict=False)

    def clean_preferred_language(self):
        data = self.cleaned_data['preferred_language']
        if data == settings.LANGUAGES[0][0]:
            data = None
        return data

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and not self.validate_passwords(password1, password2):
            msg = _('Passwords do not match')
            self._errors['password1'] = self.error_class([msg])
            self._errors['password2'] = self.error_class([msg])
            if cleaned_data.has_key('password1'):
                del cleaned_data['password1']
            if cleaned_data.has_key('password2'):
                del cleaned_data['password2']
        return cleaned_data


#==============================================================================
class ProfileView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        u = request.user

        initial = {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            #'preferred_language': u.preferred_language,
            #'preferred_currency': u.preferred_currency,
        }

        if request.method == 'POST':
            user_form = ProfileForm(request.POST, initial=initial, request=request)
            if user_form.is_valid():
                with transaction.commit_on_success():
                    first_name = user_form.cleaned_data['first_name']
                    last_name = user_form.cleaned_data['last_name']
                    email = user_form.cleaned_data['email']
                    password = user_form.cleaned_data['password1']
                    #preferred_language = user_form.cleaned_data['preferred_language']
                    #preferred_currency = user_form.cleaned_data['preferred_currency']

                    # update profile
                    u.first_name = first_name
                    u.last_name = last_name
                    u.email = email
                    if len(password) > 0:
                        u.set_password(password)
                    #u.preferred_language = preferred_language
                    #u.preferred_currency = preferred_currency
                    u.save()

                    # signal of a profile change
                    #user_profile_changed.send_robust(sender=get_user_model(), user=u, request=request)

                    messages.success(request, _('Profile updated correctly.'))
            else:
                # TODO - make this better
                print(user_form.errors)
                messages.error(request, _('Cannot update profile.'))
        else:
            user_form = ProfileForm(initial=initial, request=request)

        return render_to_response(get_skin_relative_path('views/auth/profile.html'),
                                  RequestContext(request, { 'user_form': user_form }))


#==============================================================================
@user_passes_test(lambda u: u.is_superuser)
def SuperuserView(request, username, redirect_url=settings.INDEX_URL):
    su_user = get_object_or_404(get_user_model(), username=username, is_active=True)
    request.session[SESSION_KEY] = su_user.id
    return http.HttpResponseRedirect(redirect_url)
