from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Update
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from .models import ResourceLog
from .models import SensorData
from .models import Diagnostic_Issue
from .models import AccountActivity


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    AccountActivity_instance = AccountActivity.objects.create(activity="User Signed In",user = request.user)  
    
@receiver(user_logged_out)
def on_logout(sender, user, request, **kwargs):
    AccountActivity_instance = AccountActivity.objects.create(activity="User Signed Out",user = request.user)  

# Create your views here.
def index(request):
    return render (request, 'index.html')

@login_required
def dashboardView(request):
    errorcount = Diagnostic_Issue.objects.order_by('-datetime')[:10].count()
    recentupdates = Update.objects.order_by('dateandtime')[:3]
    min10report = ResourceLog.objects.order_by('-datetime')[:1]
    recentactivity = AccountActivity.objects.order_by('-datetime')[:5]
    return render (request, 'dashboard.html',{'recentupdates':recentupdates,'errorcount':errorcount,'min10report':min10report,'recentactivity':recentactivity})
    
@login_required
def performanceView(request):
    min10report = ResourceLog.objects.order_by('-datetime')[:20]
    return render (request, 'dashboard_performance.html',{'min10report':min10report})
 
@login_required 
def dataView(request):
    data = SensorData.objects.order_by('-datetime')[:20]
    datacount = SensorData.objects.order_by('-datetime')[:20].count()
    return render (request, 'dashboard_data.html',{'data':data,'datacount':datacount})
    
@login_required 
def daiagnosticView(request):
    resources = ResourceLog.objects.order_by('-datetime')[:1]
    sensordata = SensorData.objects.order_by('-datetime')[:1]
    errors = Diagnostic_Issue.objects.order_by('-datetime')[:10]
    errorcount = Diagnostic_Issue.objects.order_by('-datetime')[:10].count()
    return render (request, 'dashboard_diagnostics.html',{'errors':errors,'errorcount':errorcount,'resources':resources,'sensordata':sensordata})