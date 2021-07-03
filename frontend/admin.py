from django.contrib import admin
from .models import Employee, ClockSystem, User


# Register your models here.
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'is_active']

@admin.register(ClockSystem)
class ClockSystemAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'location', 'role', 'hours_worked', 'clocked_in_at', 'clocked_out_at', 'created_at', 'updated_at']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'password']
