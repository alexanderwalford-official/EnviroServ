from django.urls import path,include
from . import views
from django.contrib.auth.views import LoginView,LogoutView
from django.conf.urls import url


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/',views.dashboardView, name="DASHBOARD VIEW"),
    path('performance/',views.performanceView, name="DASHBOARD PERFORMANCE"),
    path('data/',views.dataView, name="DASHBOARD DATA"),
    path('data/export-CSV/',views.exportSCV, name="EXPORT DATA"),
    path('diagnostics/',views.daiagnosticView, name="DASHBOARD DIAGNOSTICS"),
    path('logout/',LogoutView.as_view(),name="logout"),
    path('login/',LoginView.as_view(),name="login"),
]