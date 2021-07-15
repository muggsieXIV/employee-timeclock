from . import views
from django.urls import path


urlpatterns = [
    path('', views.reports),
    path(f'<int:employee_id>', views.employee_report)
]
