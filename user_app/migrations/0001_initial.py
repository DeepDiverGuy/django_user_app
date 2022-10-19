# Generated by Django 4.1.2 on 2022-10-17 11:19

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('uuid_value', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(help_text='Please provide a valid phone number in international format.', max_length=128, region=None, unique=True, verbose_name='phone number')),
                ('phone_temp', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='temporary phone number')),
                ('email', models.EmailField(help_text='An email address is required', max_length=254, unique=True, verbose_name='email')),
                ('email_temp', models.EmailField(blank=True, max_length=254, null=True, verbose_name='temporary email address')),
                ('email_verified', models.BooleanField(default=False)),
                ('username', models.CharField(blank=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, null=True, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('None', 'None')], help_text='Please select your gender', max_length=6, verbose_name='gender')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CustomizedEmailDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('token', models.CharField(blank=True, max_length=16, null=True)),
                ('valid_until', models.DateTimeField(default=django.utils.timezone.now, help_text='The timestamp of the moment of expiry of the saved token.')),
                ('throttling_failure_timestamp', models.DateTimeField(blank=True, default=None, help_text='A timestamp of the last failed verification attempt. Null if last attempt succeeded.', null=True)),
                ('throttling_failure_count', models.PositiveIntegerField(default=0, help_text='Number of successive failed attempts.')),
                ('email', models.EmailField(blank=True, help_text='Optional alternative email address to send tokens to', max_length=254, null=True)),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]