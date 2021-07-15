from django.contrib import admin
from .models import Employee, ClockSystem, User


# Register your models here.
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'is_active', 'created_at', 'updated_at']

@admin.register(ClockSystem)
class ClockSystemAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_in', 'date_out', 'clocked_in_at', 'clocked_out_at', 'employee', 'location', 'role', 'time_worked', 'in_comment', 'out_comment', 'created_at', 'updated_at']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'password', 'created_at', 'updated_at']
