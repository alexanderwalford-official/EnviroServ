from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/',views.dashboardView, name="DASHBOARD VIEW"),
    path('performance/',views.performanceView, name="DASHBOARD PERFORMANCE"),
    path('data/',views.dataView, name="DASHBOARD DATA"),
    path('diagnostics/',views.daiagnosticView, name="DASHBOARD DIAGNOSTICS")
]