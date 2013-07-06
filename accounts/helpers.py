from django.conf import settings
from django.template import loader
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _

from utils.funcs import random_string
from accounts.models import Activation

def account_activation(user):
    if not user.is_active:
        # Generate activation code
        code = random_string(32)

        # Save activation code to database
        Activation.objects.create(
            user=user,
            code=code,
        )

        # Email activation code to the user
        subject = _('Chigitalk Activation Code')

        message = loader.render_to_string('accounts/activation_text.html', {
            'user': user,
            'code': code,
        })

        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER,
            [user.email], [settings.EMAIL_HOST_USER, 'peith.vergil@gmail.com'])

        email.send()