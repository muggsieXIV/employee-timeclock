from django.shortcuts import render, redirect
from django.contrib import messages
from frontend.models import Employee, ClockSystem
import datetime
from django.utils.dateparse import parse_date


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
        'days_worked': ""
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
    context['total_time_worked'] = total_time_worked

    days_worked = str(len(context['all_clockins']))
    context['days_worked'] = days_worked

    return render(request, 'employee-report.html', context)



def process_report(request, employee_id):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'e': Employee.objects.get(id=employee_id),
        'all_clockins': ClockSystem.objects.filter(employee=employee_id),
        'start_date': request.POST['start_date'],
        'end_date': request.POST['end_date'], 
        'res': [],
        'days_worked': "",
        'total_time_worked': ""
    }
    # getting data from context
    all_clockins = context['all_clockins']
    start_date = context['start_date']
    end_date = context['end_date']
    # setting all the filtered clockins to an array for use in report
    res = []
    # evaluating employee's clockins based on filtered dates
    for data in all_clockins:
        # setting string dates to datetime for evaluation
        s = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        e = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        eval = datetime.datetime.strptime(str(data.date_in), "%Y-%m-%d")
        # evaluating our dates
        if s <= eval:
            if eval <= e:
                res.append(data)
    # Set data for report use
    context['res'] = res

    # Get Total Days Worked
    days_worked = str(len(res))
    context['days_worked'] = days_worked

    # Get Total Time worked
    datetimeFormat = '%H:%M:%S'
    # Getting time_worked for employee
    timeList = []
    for data in res:
        timeList.append(data.time_worked)
    # Adding time worked for employee
    totalSecs = 0
    for tm in timeList:
        timeParts = [int(s) for s in tm.split(':')]
        totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
    totalSecs, sec = divmod(totalSecs, 60)
    hr, min = divmod(totalSecs, 60)
    total_time_worked = "%d:%02d:%02d" % (hr, min, sec)
    context['total_time_worked'] = total_time_worked

    return render(request, 'ind-report.html', context)



def report_generated(request, employee_id):
    pass

def process_all_report(request, employee_id):
    pass

def process_all_report_generated(request):
    pass
