from django.contrib import admin
from .models import Update
from .models import ResourceLog
from .models import SensorData
from .models import Diagnostic_Issue
from .models import AccountActivity

# Register your models here.

class UpdateAdmin(admin.ModelAdmin):
    list_display = ('version', 'dateandtime', 'details')
admin.site.register(Update, UpdateAdmin)

class ResourceLogAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'cpu', 'memory', 'storage')
admin.site.register(ResourceLog, ResourceLogAdmin)

class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'enviro_temprature', 'humidity', 'longitude', 'latitude', 'barometer_pressure', 'msvhr')
admin.site.register(SensorData, SensorDataAdmin)

class IssueAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'severity', 'issue')
admin.site.register(Diagnostic_Issue, IssueAdmin)

class AccountActivityAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'activity')
admin.site.register(AccountActivity, AccountActivityAdmin)