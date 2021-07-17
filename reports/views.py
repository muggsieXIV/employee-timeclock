from django.shortcuts import render, redirect
from django.contrib import messages
from frontend.models import User, Employee, ClockSystem
import datetime


# Create your views here.
def reports(request):
    if 'user_id' not in request.session:
        return redirect('/')
    
    context = {
            'all_employees': Employee.objects.all()
        }
    return render(request, 'reports.html', context)


def employee_report(request, employee_id):
    if 'user_id' not in request.session:
        return redirect('/')

    context = {
        'e': Employee.objects.get(id=employee_id),
        'all_clockins': ClockSystem.objects.filter(employee=employee_id),
        'total_time_worked': "",
    }

    datetimeFormat = '%H:%M:%S'

    # Getting time_worked for employee
    timeList = []
    for data in context['all_clockins']:
        timeList.append(data.time_worked)

    # Adding time worked for employee
    totalSecs = 0
    for tm in timeList:
        timeParts = [int(s) for s in tm.split(':')]
        totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
    totalSecs, sec = divmod(totalSecs, 60)
    hr, min = divmod(totalSecs, 60)
    total_time_worked = "%d:%02d:%02d" % (hr, min, sec)
    # Testing this worked
    print('Employee: ' + context['e'].last_name + ', ' + context['e'].first_name + ' - Total hours worked: ' + total_time_worked )
    context['total_time_worked'] = total_time_worked


    return render(request, 'employee-report.html', context)



def process_report(request, employee_id):
    if 'user_id' not in request.session:
        return redirect('/')

    context = {
        'e': Employee.objects.get(id=employee_id),
        'all_clockins': ClockSystem.objects.filter(employee=employee_id),
    }

    # Get clockins for date range
    data = context['all_clockins'].objects.filter(date__range=[request.POST['start_date'], request.POST['end_date']])

    for d in data:
        print(d)





    # Get all clock ins from start to end date

    
    return redirect('/reports/{{employee_id}}/process_report/generated', context)



def report_generated(request, employee_id):

    return render(request, 'report.html')

def process_all_report(request, employee_id):
    pass

def process_all_report_generated(request):
    pass
