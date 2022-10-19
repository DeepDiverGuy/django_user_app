'''
user_app.models
'''

import uuid

from django.db import models
from django.core.mail import send_mail
from django.template import Context, Template
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser

from django_otp.plugins.otp_email.conf import settings
from django_otp.models import SideChannelDevice, ThrottlingMixin

from phonenumber_field.modelfields import PhoneNumberField




# import re
# from django.core.exceptions import ValidationError
# def validate_gmail(value):
#     # GMAIL validation logic; 
#     if re.split('@', value)[-1] != 'gmail.com':
#         raise ValidationError(
#             _('%(value)s is NOT a valid GMAIL account. Only Gmail address is allowed'),
#             params={'value': value},
#         )



class user(AbstractUser):

    """
    A fully featured Customized User Model with admin-compliant permissions. 'phone' field is treated as username field.
    """

    uuid_value = models.UUIDField(
        primary_key=False,
        default=uuid.uuid4,
        editable=False,
        null=False)

    phone = PhoneNumberField(
        _('Phone Number'),
        unique=True,
        blank=False, 
        null=False,
        help_text= _('Please provide a valid phone number in international format.'),)
    phone_temp = PhoneNumberField(
        _('temporary phone number'),
        blank=True, 
        null=True,)

    email = models.EmailField(
        _('Email Address'),
        unique=True, 
        blank=False, 
        null=False,
        help_text= _('Please provide a valid email address'),)
    email_temp = models.EmailField(
        _('temporary email address'), 
        blank=True, 
        null=True, )
    email_verified = models.BooleanField(default=False)

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'), 
        max_length=150, 
        unique=True, 
        blank=True, 
        null=True, 
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'), 
        validators=[username_validator], 
        error_messages={'unique': _("A user with that username already exists.")})

    gender = models.CharField(
        _('Gender'),
        max_length=6,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('None', 'None'),],
        help_text=_('Please select your gender'),)

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ))


    PHONE_FIELD = 'phone'
    USERNAME_FIELD = PHONE_FIELD
    REQUIRED_FIELDS = ['username', 'email', ]  # Used while creating admins in terminal

    def get_absolute_url(self):
        return reverse('user_app:profile', kwargs={'uuid_value': self.uuid_value})

    def __str__(self):
        return str(self.phone)

    class Meta:
        abstract = False



class CustomizedEmailDevice(ThrottlingMixin, SideChannelDevice):

    """
    This device is almost identical to django_otp's EmailDevice. Just customized a little and added some extra functionalities. 
    """

    email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        help_text='Optional alternative email address to send tokens to'
    )

    def get_throttle_factor(self):
        return settings.OTP_EMAIL_THROTTLE_FACTOR

    def generate_challenge(self, extra_context=None):
        """
        Generates a random token and emails it to the user.

        :param extra_context: Additional context variables for rendering the
            email template.
        :type extra_context: dict

        """
        self.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)

        context = {'token': self.token, **(extra_context or {})}
        if settings.OTP_EMAIL_BODY_TEMPLATE:
            body = Template(settings.OTP_EMAIL_BODY_TEMPLATE).render(Context(context))
        else:
            body = get_template(settings.OTP_EMAIL_BODY_TEMPLATE_PATH).render(context)

        send_mail(settings.OTP_EMAIL_SUBJECT,
                  body,
                  settings.OTP_EMAIL_SENDER,
                  [self.email or self.user.email])

        message = f"sent to {self.email or self.user.email}"

        return message

    def verify_token(self, token):
        verify_allowed, _ = self.verify_is_allowed()
        if verify_allowed:
            verified = super().verify_token(token)

            if verified:
                self.throttle_reset()
                if not self.user.email_verified:
                    self.user.email_verified = True
                    self.user.save()
            else:
                self.throttle_increment()
        else:
            verified = False

        return verified


