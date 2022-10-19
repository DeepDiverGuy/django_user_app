from django.contrib import admin
from .models import user, CustomizedEmailDevice


# REGISTER your MODELS here.


admin.site.register(user)
admin.site.register(CustomizedEmailDevice)
