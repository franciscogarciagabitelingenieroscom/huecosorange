from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Actuacion, Finca
# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Actuacion)
admin.site.register(Finca)
