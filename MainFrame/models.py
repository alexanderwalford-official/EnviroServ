from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Update(models.Model):
    version = models.CharField(max_length=10)
    details = models.CharField(max_length=500)
    dateandtime = models.DateField()
    
class ResourceLog(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, null=True) 
    cpu = models.CharField(max_length=100, default="", unique=False)
    memory = models.CharField(max_length=100, default="", unique=False)
    storage = models.CharField(max_length=100, default="", unique=False)
    
class SensorData(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, null=True) 
    dustlevel = models.FloatField()
    enviro_temprature = models.FloatField()
    sys_temprature = models.FloatField()
    brightness = models.IntegerField()
    humidity = models.FloatField()
    barometer_temperature = models.FloatField()
    barometer_pressure = models.IntegerField()
    human_detection = models.CharField(max_length=100, default="", unique=False)
    batterylevel = models.IntegerField(null=True)
    
class Diagnostic_Issue(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, null=True) 
    issue = models.CharField(max_length=500, default="", unique=False)
    severity = models.CharField(max_length=100, default="", unique=False)
    
class AccountActivity(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, null=True) 
    activity = models.CharField(max_length=200, default="", unique=False)
    user = models.ForeignKey(User,on_delete=models.PROTECT, null=True)