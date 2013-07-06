from django.conf.urls import patterns, url

from accounts.forms import CustomAuthForm, CustomPasswordResetForm
from accounts.views import Registration, Activate, NewActivationCode, Login, Profile

logoutparams = {
    'template_name': 'accounts/logout.html'
}

resetparams1 = {
    'template_name'      : 'accounts/password_reset.html',
    'email_template_name': 'accounts/password_email.html',
    'post_reset_redirect': '/password/reset/done/',
    'password_reset_form': CustomPasswordResetForm,
}

resetparams2 = {
    'post_reset_redirect': '/password/reset/complete/'
}

urlpatterns = patterns('',
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', logoutparams, name='logout'),
    url(r'^(?P<user>\d+)/activate/$', Activate.as_view(), name='activate'),
    url(r'^(?P<user>\d+)/activation/new/$', NewActivationCode.as_view(), name='new_activation'),

    # Password reset
    url(r'^password/reset/$',
        'django.contrib.auth.views.password_reset', resetparams1, name='password_reset'),
    url(r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', resetparams2, name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),

    url(r'^register/$', Registration.as_view(), name='register'),

    url(r'^profile/$', Profile.as_view(), name='profile'),
)