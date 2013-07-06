from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, resolve_url
from django.utils.http import is_safe_url
from django.contrib.auth import login, get_user_model
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View
from django.contrib.sites.models import get_current_site
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required

from accounts.forms import UserCreationForm, CustomAuthForm, ActivationForm
from accounts.models import Activation
from accounts.helpers import account_activation

class Login(TemplateView):
    template_name = 'accounts/login.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(Login, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Login, self).get_context_data(**kwargs)
        context['next'] = self.request.REQUEST.get('next')
        context['form'] = CustomAuthForm()
        return context

    def post(self, request, *args, **kwargs):
        next = request.REQUEST.get('next', '')

        form = CustomAuthForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                return redirect('accounts:activate', user=user.pk)

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=next, host=request.get_host()):
                next = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            login(request, user)

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return redirect(next)

        request.session.set_test_cookie()

        site = get_current_site(request)
        context = {
            'form': form,
            'next': next,
            'site': site,
        }
        return self.render_to_response(context)

class Activate(TemplateView):
    template_name = 'accounts/activation.html'

    def get_context_data(self, **kwargs):
        context = super(Activate, self).get_context_data(**kwargs)

        User = get_user_model()

        pk = self.kwargs.pop('user')
        try:
            context['newuser'] = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

        context['form'] = ActivationForm()

        return context

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(pk=kwargs.pop('user'))
        except User.DoesNotExist:
            raise Http404

        form = ActivationForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                activation = Activation.objects.get(user=user, code=code)
            except Activation.DoesNotExist:
                return self.render_to_response({
                    'form': form,
                    'error': _('Invalid activation code'),
                    'newuser': user,
                })

            user.is_active = True
            user.save()

            activation.used = True
            activation.save()

            messages.info(request, _(
                'Your new account has been activated. '
                'You can now login with your email and password.'
            ))
            
            return redirect('accounts:login')

        return self.render_to_response({ 'form': form, 'newuser': user })

class NewActivationCode(View):
    
    def get(self, request, *args, **kwargs):
        User = get_user_model()

        pk = self.kwargs.pop('user')
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

        # Generate a new activation code
        # and email it to the user.
        account_activation(user)

        messages.info(request, _(
            'A new activation code was sent to your email. '
            'Please copy the code from your email and '
            'paste it to the input box below.'
        ))

        return redirect('accounts:activate', user=user.pk)

class Registration(TemplateView):
    template_name = 'accounts/register.html'
    
    def get_context_data(self, **kwargs):
        context = super(Registration, self).get_context_data(**kwargs)
        context['form'] = UserCreationForm()
        return context
        
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()

            # Generate an activation code
            # and email it to the user.
            account_activation(user)
            
            messages.info(request, _(
                'Your new account has been created. '
                'You should receive an email soon with '
                'instructions on how to activate your account.'
            ))
            
            return redirect('accounts:login')
        else:
            return self.render_to_response({ 'form': form })

class Profile(TemplateView):
    template_name = 'accounts/profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Profile, self).dispatch(*args, **kwargs)