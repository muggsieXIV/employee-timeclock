from . import views
from django.urls import path


urlpatterns = [
    path('', views.sign_in),
    path('process-register', views.process_register),
    path('login', views.process_login),
    path('logout', views.logout),
    path('process-clock-system', views.process_clock_system),
    path('process-clock', views.process_clock),
    path('create-user', views.create_user),
    path('dashboard', views.dashboard),
]
