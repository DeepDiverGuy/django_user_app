''' 
user_app.decorators 
'''

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy




Email_Verification_Required = user_passes_test(lambda u: u.email_verified, login_url=reverse_lazy('user_app:email_verify'))