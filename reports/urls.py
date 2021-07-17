from . import views
from django.urls import path


urlpatterns = [
    path('', views.reports),
    path(f'<int:employee_id>', views.employee_report),
    path(f'<int:employee_id>/process_report', views.process_report),
    path(f'<int:employee_id/process_report/generated', views.report_generated),
    path('all/process_reports', views.process_all_report),
    path('all/process/report-generated', views.process_all_report_generated)
]
