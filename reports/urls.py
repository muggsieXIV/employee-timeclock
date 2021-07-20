from . import views
from django.urls import path


urlpatterns = [
    path('', views.reports),
    path(f'<int:employee_id>', views.employee_report),
    path(f'<int:employee_id>/process_report', views.process_report),
    path(f'<int:employee_id>/process-report/pdf-print', views.process_employee_pdf),
    path('all/process-report', views.process_all_report),
    path('all/process-report/pdf-print', views.process_all_pdf)
]
