'''
user_app.forms
'''

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import ngettext_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from django_otp.forms import OTPTokenForm

from phonenumber_field.formfields import PhoneNumberField

from .models import user as customized_user_model




class CustomizedUserCreationForm(UserCreationForm):
    '''
    A Custom User-Creation-form is needed since we're using a customized user model
    '''
    
    class Meta:
        model = customized_user_model
        fields = ('first_name', 'last_name', 'phone', 'email', 'gender')



class CustomizededAuthenticationForm(AuthenticationForm):
    '''
    Django's built-in AuthenticationForm doesn't show any "inactive" error when the user trying to Login is inactive. So, I had to modify the "clean()" method accordingly.
    '''

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both fields may be case-sensitive."
        ),
        'inactive': _(
            "Your account is inactive. Please activate it first."
        ),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:
                try:
                    unauthenticated_user = customized_user_model.objects.get(phone=username) 
                    # because "authenticate()" method returns None if the user is inactive or not authenticated.                   
                except:
                    unauthenticated_user = None
                finally:
                    if unauthenticated_user and not unauthenticated_user.is_active:
                        # Instead of calling the "confirm_login_allowed(unauthenticated_user)"; I'm 
                        # directly raising a ValidationError. You can call the method if it's needed for your project.
                        raise ValidationError(self.error_messages['inactive'], code='inactive',)
                    else:
                        raise self.get_invalid_login_error()
                        
        return self.cleaned_data



class CustomizedUserDeletionForm(forms.Form):
    '''
    This form is used while deleting a user
    '''

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'Your-password'})
        )



class CustomizedOTPTokenForm(OTPTokenForm):
    '''
    The built-in "OTPTokenForm" requires the current user object to be passed to it as an argument, which can be done in the views.py. Instead, I inherited the form class itself and customized it for ease. This CustomOTPTokenForm is fully compatible with any LoginView.
    '''

    otp_error_messages = {
        'token_required': _('Please enter your OTP token.'),
        'challenge_exception': _('Error generating OTP Token: {0}'),
        'not_interactive': _('The selected OTP device is not interactive'),
        'challenge_message': _('OTP Token: {0}'),
        'invalid_token': _('Invalid token. Please make sure you have entered it correctly.'),
        'n_failed_attempts': ngettext_lazy(
            "Verification temporarily disabled because of %(failure_count)d failed attempt, please try again soon.",
            "Verification temporarily disabled because of %(failure_count)d failed attempts, please try again soon.",
            "failure_count"),
        'verification_not_allowed': _("Verification of the token is currently disabled"),
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request.user, *args, **kwargs)

        self.user = request.user
        self.fields['otp_device'].choices = self.device_choices(request.user)



class EmailVerificationForm(CustomizedOTPTokenForm):
    
    @staticmethod
    def device_choices(user):
        # We want to specify the email devices only.
        return list((d.persistent_id, d.name) for d in user.customizedemaildevice_set.all())



class EmailChangeForm(CustomizedOTPTokenForm):
    """
    This form is built on top of the "django_otp.forms.OTPTokenForm" and modified to 
    serve the purpose of changing a "user.email" field upon a successful token-verification.

    How it works: 
    First of, when called with 'Send OTP (Get Challenge)', the "CustomizedEmailDevice.email" field 
    is filled with "form.cleaned_data['new_email']", and thus an OTP Token is delivered to 
    this email address. If the token-delivery is successful, the email address where the token 
    has been sent is saved to "user.email_temp" field (in DATABASE level). After that, when 
    a user submits a token; "clean_otp()" first checks if the current 
    "form.cleaned_data['new_email']" and "user.temp_email" match; if matched, then 
    the token is given to the "verify_token()" method for further processing; if they don't, then 
    "user.email_temp" is assigned the new value of the "form.cleaned_data['new_email']" and 
    "_handle_challenge()" is called to start the process again. Once the "verify_token()" method 
    successfully verifies a token, "user.email" is set to the value of "user.temp_email", 
    "user.temp_email" is set to None and the "user" object is saved in the database. "EmailDevice.name" 
    is also changed to the "user.email" and saved.
    """

    new_email = forms.EmailField()

    @staticmethod
    def device_choices(user):
        # We want to specify the email devices only.
        return list((d.persistent_id, d.name) for d in user.customizedemaildevice_set.all())

    def _handle_challenge(self, device):
        if customized_user_model.objects.filter(email = self.cleaned_data['new_email']).exists():
            raise forms.ValidationError(
                self.otp_error_messages['challenge_exception'].format("This email address already exists to an account"), code='challenge_exception'
            )
        try:
            device.email = self.cleaned_data['new_email'] # The value of device.email is used to deliver the token
            challenge = device.generate_challenge() if (device is not None) else None
            if challenge:
                # if the token is successfully delivered to the new email address, then save it to user.email_temp field
                self.user.email_temp = device.email
                device.email = None
                device.save()
                self.user.save()
        except Exception as e:
            raise forms.ValidationError(
                self.otp_error_messages['challenge_exception'].format(e), code='challenge_exception'
            )
        else:
            if challenge is None:
                raise forms.ValidationError(self.otp_error_messages['not_interactive'], code='not_interactive')
            else:
                raise forms.ValidationError(
                    self.otp_error_messages['challenge_message'].format(challenge), code='challenge_message'
                )

    def clean_otp(self, user):
        """
        Processes the ``otp_*`` fields.
        :param user: A user that has been authenticated by the first factor
            (such as a password).
        :type user: :class:`~django.contrib.auth.models.User`
        :raises: :exc:`~django.core.exceptions.ValidationError` if the user is
            not fully authenticated by an OTP token.
        """
        if user is None:
            return

        validation_error = None

        with transaction.atomic():
            try:
                device = self._chosen_device(user)
                token = self.cleaned_data.get('otp_token')

                user.otp_device = None

                try:
                    if self.cleaned_data.get('otp_challenge'):
                        self._handle_challenge(device)
                    elif token:                       
                        if self.cleaned_data['new_email'] == user.email_temp: # check if the email address given previously (when clicking 'send token') and the current one (when clicking 'verify') match
                            user.otp_device = self._verify_token(user, token, device)
                        else:
                            # if they don't match, start the process again with the newly given email address
                            self._handle_challenge(device)
                    else:
                        raise forms.ValidationError(self.otp_error_messages['token_required'], code='token_required')
                finally:
                    if user.otp_device is None:
                        self._update_form(user)
                    if user.otp_device:
                        # OTP verification is successful
                        # Some cleaning up at the end; and most importantly, the assignment of the newly verified email address to "user.email"
                        user.email = user.email_temp
                        user.email_temp = None
                        user.save()
                        device.name = user.email
                        device.save()
                        

                    
            except forms.ValidationError as e:
                # Validation errors shouldn't abort the transaction, so we have
                # to carefully transport them out.
                validation_error = e

        if validation_error:
            raise validation_error



class PhoneVerificationForm(forms.Form):
    code = forms.CharField(required=True, help_text=_('Enter the confirmation code here'))


class PhoneChangeForm(forms.Form):
    new_phone = PhoneNumberField(required=True, help_text= _('Please provide a valid phone number in international format.'))


   