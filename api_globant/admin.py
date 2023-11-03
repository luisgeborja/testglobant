from django.contrib import admin
from .models import Departments, Jobs, HiredEmployees
# Register your models here.
admin.site.register(Departments)
admin.site.register(Jobs)
admin.site.register(HiredEmployees)