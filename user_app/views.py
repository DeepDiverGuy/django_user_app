'''
user_app.views
'''

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import resolve_url, get_object_or_404
from django.urls import reverse_lazy
from django.db import IntegrityError

from .models import user as customized_user_model
from .forms import CustomizedUserCreationForm, CustomizededAuthenticationForm, EmailChangeForm, CustomizedUserDeletionForm, CustomizedOTPTokenForm, EmailVerificationForm, PhoneVerificationForm, PhoneChangeForm
from .decorators import Email_Verification_Required
from . import twilio_verify

from django_otp.decorators import otp_required




class UserCreate(FormView):
    template_name = 'user_app/user_create_form.html'
    form_class = CustomizedUserCreationForm
    success_url = None

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False # Setting it to False; because the phone number hasn't been verified yet
        token_send = twilio_verify.token_send(user.phone)
        if token_send=='pending':
            user = form.save()
            messages.success(self.request, 'Your account has been created. Please Enter the code we\'ve sent to your number to ACTIVATE your account. Once activated, you can log into your account.')
            self.success_url = reverse_lazy("user_app:phone_verify", args = [user.uuid_value])
            return super(UserCreate, self).form_valid(form)
        else:
            messages.error(self.request, 'Unfortunately, there has been an error sending a confirmation code to your number. So, your account couldn\'t be created. we\'re extremely sorry. Please try again after some time')
            return super(UserCreate, self).form_invalid(form)



class TwilioTokenSendAgain(View):

    def get(self, request, uuid_value):
        user = customized_user_model.objects.get(uuid_value=uuid_value)
        token_send = twilio_verify.token_send(user.phone_temp or user.phone)
        if token_send=='pending':
            messages.success(self.request, f'We\'ve sent another confirmation code to {user.phone_temp or user.phone}. Please enter it')
        else:
            messages.error(self.request, f'Unfortunately, there has been an error sending a confirmation code to {user.phone_temp or user.phone}. Please try again.')
        return HttpResponseRedirect(reverse_lazy("user_app:phone_verify", args = [self.kwargs['uuid_value']]))



class UserPhoneVerify(FormView):
    template_name = 'user_app/user_phone_verify_form.html'
    form_class = PhoneVerificationForm
    success_url = reverse_lazy("user_app:login")

    def form_valid(self, form):
        user = customized_user_model.objects.get(uuid_value = self.kwargs['uuid_value'])
        token_verify = twilio_verify.token_verify(user.phone_temp or user.phone, form.cleaned_data['code'])
        if token_verify == 'approved':
            if user.phone_temp:
                user.phone = user.phone_temp
                user.phone_temp = None
                user.save()
                messages.success(self.request, 'Your phone number is changed!')
                self.success_url = reverse_lazy('user_app:profile', args = [user.uuid_value])
            else:
                user.is_active = True
                user.customizedemaildevice_set.create(user=user, name=user.email)
                user.save()
                messages.success(self.request, 'Congratulations! Your account is now active. You can log into your account.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'There has been an error verifying your code. Please try again')
            return super().form_invalid(form)



class UserPhoneChange(LoginRequiredMixin, FormView):
    template_name = 'user_app/user_phone_change_form.html'
    form_class = PhoneChangeForm
    success_url = None

    def form_valid(self, form):
        user = self.request.user
        new_phone = form.cleaned_data['new_phone']

        if user.phone == new_phone:
            messages.error(self.request, 'You are already using this number!')
            return super().form_invalid(form)

        try:
            real_phone = user.phone
            user.phone = new_phone
            user.save()
            user.phone = real_phone
            user.save()
        except IntegrityError:
            messages.error(self.request, 'A user with this number already exists!')
            return super().form_invalid(form)

        token_send = twilio_verify.token_send(new_phone)
        if token_send=='pending':
            user.phone_temp = new_phone
            user.save()
            messages.success(self.request, 'We\'ve sent a confirmation code to your new number. Please enter it')
            self.success_url = reverse_lazy("user_app:phone_verify", args = [user.uuid_value])
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Unfortunately, there has been an error sending a confirmation code to your new number. Please try again.')
            return super().form_invalid(form)
        


class UserLogin(LoginView):
    template_name = 'user_app/login.html'
    form_class = CustomizededAuthenticationForm # The built-in AuthenticationForm doesn't show inactive-account errors

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # if a user is already authenticated, we shouldn't show the login form
            messages.info(self.request, "You are already logged in")
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
            
    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        LOGIN_REDIRECT_URL = reverse_lazy('user_app:profile', args = [self.request.user.uuid_value])
        return resolve_url(self.next_page or LOGIN_REDIRECT_URL)



class UserProfile(LoginRequiredMixin, DetailView):
    model = customized_user_model
    template_name = 'user_app/user_profile.html'

    def get_object(self, queryset=None):
        return get_object_or_404(customized_user_model, uuid_value=self.kwargs.get('uuid_value'))



class UserUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = customized_user_model
    fields = ['first_name', 'last_name', 'gender', ]
    template_name_suffix = '_update_form'

    def get_object(self, queryset=None):
        return get_object_or_404(customized_user_model, uuid_value=self.kwargs.get('uuid_value'))

    def test_func(self):
        if self.request.user == customized_user_model.objects.get(uuid_value = self.kwargs['uuid_value']):
            return True
        return False

    def form_valid(self, form):
        messages.success(self.request, "Your Profile is updated!")
        return super().form_valid(form)



@method_decorator(Email_Verification_Required, name='dispatch')
class UserPasswordChange(PasswordChangeView):
    template_name = 'user_app/password_change_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Your password hass been changed!")
        return reverse_lazy('user_app:profile', args = [self.request.user.uuid_value])



@method_decorator(Email_Verification_Required, name='dispatch')
class UserPasswordReset(PasswordResetView):
    template_name = 'user_app/password_reset_form.html'
    email_template_name = 'user_app/password_reset_email.html'
    subject_template_name = 'user_app/password_reset_subject.txt'
    success_url = reverse_lazy('user_app:password_reset_done')

    def form_valid(self, form):
        if not customized_user_model.objects.filter(email=form.cleaned_data.get("email")):
            messages.error(self.request, 'No account found with that email! Please check the email address and try again.')
            return HttpResponseRedirect(reverse_lazy('user_app:password_reset'))
        return super().form_valid(form)



@method_decorator(Email_Verification_Required, name='dispatch')
class UserPasswordResetDone(PasswordResetDoneView):
    template_name = 'user_app/password_reset_done.html'



@method_decorator(Email_Verification_Required, name='dispatch')
class UserPasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'user_app/password_reset_confirm.html'
    
    def get_success_url(self):
        messages.success(self.request, "Your password has been reset. Please login again with the new password.")
        return reverse_lazy('user_app:login')



class UserEmailVerify(LoginRequiredMixin, LoginView):
    template_name = 'user_app/user_email_verify_form.html'
    authentication_form = EmailVerificationForm

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        messages.success(self.request, "Your Email has been verified!")
        LOGIN_REDIRECT_URL = reverse_lazy('user_app:profile', args = [self.request.user.uuid_value])
        return resolve_url(self.next_page or LOGIN_REDIRECT_URL)



@method_decorator(Email_Verification_Required, name='dispatch')
class UserEmailChange(LoginRequiredMixin, LoginView):
    template_name = 'user_app/user_email_change_form.html'
    authentication_form = EmailChangeForm
    
    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        messages.success(self.request, "Your Email has been changed!")
        LOGIN_REDIRECT_URL = reverse_lazy('user_app:profile', args = [self.request.user.uuid_value])
        return resolve_url(self.next_page or LOGIN_REDIRECT_URL)



class UserOTPVerify(LoginRequiredMixin, LoginView):
    template_name = 'user_app/user_otp_verify_form.html'
    authentication_form = CustomizedOTPTokenForm

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        PROFILE_REDIRECT_URL = reverse_lazy('user_app:profile', args = [self.request.user.uuid_value])
        messages.success(self.request, "Email Verification Successful!")
        return resolve_url(self.next_page or PROFILE_REDIRECT_URL)



class UserLogout(LogoutView):
    template_name = 'user_app/logout.html'



@method_decorator(Email_Verification_Required, name='dispatch')
@method_decorator(otp_required(redirect_field_name='next', login_url=reverse_lazy('user_app:otp_verify'), if_configured=False), name='dispatch')
class UserDelete(FormView):
    template_name = 'user_app/user_delete_form.html'
    form_class = CustomizedUserDeletionForm
    success_url = reverse_lazy('user_app:logout')

    def form_valid(self, form):
        SadUser = self.request.user
        if SadUser.check_password(form.cleaned_data['password']):
            # It's not recommended to delete the user altogether; rather you can set SadUser.is_active = False
            SadUser.delete()
            messages.info(self.request, "Your Account has been deleted!")
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Incorrect Password!')
            return HttpResponseRedirect(reverse_lazy('user_app:delete'))


