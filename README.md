# "USER APP" for django projects



# Description:

A robust User app for django-powered sites that has Email & Phone-Number Verification functionalities. 

Key functionalities are:

- "Phone Number Verification" functionality using TWILIO (for user-registration)
- "Email verification Required" functionality (as a decorator)
- "OTP Verification Required" functionality (as a decorator)
- A fully customizable & more secure user model

All functionalities:

- used 'uuid' field to identify users, rather than an insecure 'id' field.
- used "django-phonenumber-field" for saving a user's phone number.

- User-registration & activation upon successful phone-number verification using TWILIO (Easily customizable).
- Sending confirmation code again using Twilio.
- Changing phone number upon successfully verifying the new number using TWILIO.

- Email verification using "django-otp" framework.
- Changing email upon successfully verifying the new email address.
- Usable "Email Verification" decorator.
- Usable "OTP verification" decorator.

- Login & logout.
- Updating user profile.
- Changing & resetting password using email.
- Deleting own profile after a successful OTP verification and password-check.
- Phone-Number field is used as username field.



# Dependencies:
- pip install django (>=4.1.2)
- pip install django-otp (>=1.1.3)
- pip install "django-phonenumber-field[phonenumbers]" (>=7.0.0)
- pip install python-dotenv (>=0.21.0) # Only required if you're using this framework for your environment variables
- pip install twilio (>=7.14.2)



# Installation:
- After cloning this repo, just copy-paste the "user_app" app (directory) inside your django project.
- Then proceed to the configurations described below



# Configurations:

(i) In your project's settings.py, include the followings:

	- Pointing to the Customized User Model:
		AUTH_USER_MODEL = 'user_app.user'

	- In the INSTALLED_APPS list, add these:
		INSTALLED_APPS = [
		...
		...
		'django_otp',
	    	'django_otp.plugins.otp_email', # Although we're not using this app's "EmailDevice" model; instead using our own one. But there is some dependency issues. So, we need this app.
		'phonenumber_field',
		'user_app.apps.UserAppConfig',
		]

	- In the MIDDLEWARE list, add 'django_otp.middleware.OTPMiddleware' just after the 'django.contrib.auth.middleware.AuthenticationMiddleware'. The sequence is necessary as the author of "django_otp" framework mentioned.
		MIDDLEWARE = [
		...
		'django.contrib.auth.middleware.AuthenticationMiddleware',
		'django_otp.middleware.OTPMiddleware', # django_otp middleware
		...
		]

	- Specify the default LOGIN_URL:	
		from django.urls import reverse_lazy
		LOGIN_URL = reverse_lazy('user_app:login')
		
	- You can optionally specify django's own email attributes as per your needs.
		''' Django's Email Settings'''
		EMAIL_USE_TLS = False # Should be True in production
		EMAIL_HOST = '' # ex:'smtp.gmail.com'
		EMAIL_PORT = 1025 # ex: 587
		EMAIL_HOST_USER = 'me@gmail.com'
		EMAIL_HOST_PASSWORD = 'password'
		DEFAULT_FROM_EMAIL = 'abc@domain.com'
	
	- You can optionally specify "django-phonenumber-field" settings as per your needs. Documentation: https://django-phonenumber-field.readthedocs.io/en/latest
	
	- You can optionally specify "django_otp" settings as per your needs. Documentation: https://django-otp-official.readthedocs.io/en/stable
	
	
(ii) Twilio configuration: Set these environment variables as per your Twilio account:
		
		TWILIO_ACCOUNT_SID
		TWILIO_AUTH_TOKEN
		TWILIO_SERVICE_SID
	
			
(iii) In urls.py (root), include the followings:

	from django.urls import path, include
	urlpatterns = [
	    ...
	    path('user/', include('user_app.urls')),
	]
	

(iv) Lastly, all we have left to do is migration. Go to your projects root directory and enter the followings into your terminal:

	python3 manage.py makemigrations
	python3 manage.py migrate
	
	

# Using the App:

After we've configured the app successfully, we can start the development server from our project's root directory:

	python3 manage.py runserver
	
and start playing around. Also, if you're not using the "django.core.mail.backends.console.EmailBackend" for your email backend, you should start a debugging server in another terminal to catch all the emails that are being sent from your localhost:
	
	python3 -m smtpd -n -c DebuggingServer localhost:1025
	


# Further Works: 
Now, everything should work perfectly. We can Edit and Customize the app as suits best for our projects!



# Extending the project:
- We can integrate 'django-otp-twilio' (https://django-otp-twilio.readthedocs.io/en/latest/) so that our "OTP Verification" functionality can also use phone numbers for OTP verification (in the form of two-factor authentication). Currently, it only uses Email addresses.
- We can integrate 'django-two-factor-auth' (https://django-two-factor-auth.readthedocs.io/en/stable/) so that a user can have the flexibility of using two-factor authentication.
- We can integrate django-celery (https://pypi.org/project/django-celery/) for offloading some outgoing operations like sending sms, emails etc.
- We can integrate 'django-allauth' (https://django-allauth.readthedocs.io/en/latest/installation.html) so our users can authenticate themselves via other social media sites as they prefer.



# Issues: 
If you find any issues, please feel free to open one.



# Pull Requests: 
PRs are welcome; especially, if new functionalities are added.
	
	
	



