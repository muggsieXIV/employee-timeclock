import csv
from django.http.response import HttpResponse
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
        'all_employees': Employee.objects.all(),
        'res': [],
    }

    now = datetime.datetime.now()

    # Get Employee -> Get Employee Clockins filtered by start/end dates...
    all_employees = context['all_employees']
    for employee in all_employees:
        qued_clock_ins = []
        days_worked = ""
        # getting all clock-ins for set dates
        # print(str(employee.id) + " employeeID")
        qued_clock_ins = ClockSystem.objects.filter(employee=employee.id)

        # Get Time Worked for Employee
        time_list = []
        for data in qued_clock_ins:
            if not data.date_out:
                time_out = now.strftime("%H:%M:%S")

                dt_1 = str(data.date_in) + ' ' + str(data.clocked_in_at)
                dt_2 = str(now.strftime("%Y-%m-%d")) + ' ' + str(now.strftime("%H:%M:%S"))
                datetimeFormat = '%Y-%m-%d %H:%M:%S'
                diff = datetime.datetime.strptime(dt_2, datetimeFormat) - datetime.datetime.strptime(dt_1, datetimeFormat)
                time_list.append(str(diff))
            else:
                time_list.append(data.time_worked)

        totalSecs = 0
        for tm in time_list:
            timeParts = [int(s) for s in tm.split(':')]
            totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
        totalSecs, sec = divmod(totalSecs, 60)
        hr, min = divmod(totalSecs, 60)
        total_time_worked = "%d:%02d:%02d" % (hr, min, sec)

        # Get Days Worked for Employee
        days_worked = len(qued_clock_ins)

        # Exporting Employee data to frontend
        employee_data = {
            'id': employee.id, 
            'last_name': employee.last_name, 
            'first_name': employee.first_name, 
            'days_worked': days_worked, 
            'total_time_worked': total_time_worked,
            'all_clock_ins': qued_clock_ins,
        }
        context['res'].append(employee_data)

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
    now = datetime.datetime.now()
    datetimeFormat = '%H:%M:%S'
    # Getting time_worked for employee
    timeList = []


    for data in context['all_clockins']:

        if not data.date_out:
            time_out = now.strftime("%H:%M:%S")
            dt_1 = str(data.date_in) + ' ' + str(data.clocked_in_at)
            dt_2 = str(now.strftime("%Y-%m-%d")) + ' ' + str(now.strftime("%H:%M:%S"))
            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            diff = datetime.datetime.strptime(dt_2, datetimeFormat) - datetime.datetime.strptime(dt_1, datetimeFormat)
            timeList.append(str(diff))
        else:
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
    print(all_clockins)
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
    now = datetime.datetime.now()
    datetimeFormat = '%H:%M:%S'
    # Getting time_worked for employee
    time_list = []
    for data in res:
        if not data.date_out:
            time_out = now.strftime("%H:%M:%S")
            dt_1 = str(data.date_in) + ' ' + str(data.clocked_in_at)
            dt_2 = str(now.strftime("%Y-%m-%d")) + ' ' + str(now.strftime("%H:%M:%S"))
            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            diff = datetime.datetime.strptime(dt_2, datetimeFormat) - datetime.datetime.strptime(dt_1, datetimeFormat)
            time_list.append(str(diff))
            data.date_out = now.strftime("%Y-%m-%d")
            data.clocked_out_at = str(time_out)
            data.time_worked = str(diff)
        else:
            time_list.append(data.time_worked)
    # Adding time worked for employee
    totalSecs = 0
    for tm in time_list:
        timeParts = [int(s) for s in tm.split(':')]
        totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
    totalSecs, sec = divmod(totalSecs, 60)
    hr, min = divmod(totalSecs, 60)
    total_time_worked = "%d:%02d:%02d" % (hr, min, sec)
    context['total_time_worked'] = total_time_worked

    return render(request, 'ind-report.html', context)


def process_all_report(request):
    if 'user_id' not in request.session:
        return redirect('/')

    context = {
        'all_employees': Employee.objects.all(),
        'start_date': request.POST['start_date'],
        'end_date': request.POST['end_date'],
        'res': [],
    }

    # Get the set start/end dates for date
    start_date = str(context['start_date'])
    end_date = str(context['end_date'])

    # Get Employee -> Get Employee Clockins filtered by start/end dates...
    all_employees = context['all_employees']
    for employee in all_employees:
        qued_clock_ins = []
        days_worked = ""
        time_worked = ""
        # getting all clock-ins for set dates
        # print(str(employee.id) + " employeeID")
        qued_clock_ins = ClockSystem.objects.filter(employee=employee.id)
        clock_ins = []
        for data in qued_clock_ins:
            # setting string dates to datetime for evaluation
            s = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            e = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            d_in = str(data.date_in)
            eval = datetime.datetime.strptime(d_in, "%Y-%m-%d")

            # evaluating our dates - if in range add to clock_ins
            if s <= eval:
                if eval <= e:
                    clock_ins.append(data)

        days_worked = str(len(clock_ins))

        now = datetime.datetime.now()
        datetimeFormat = '%H:%M:%S'
        time_list = []
        # getting time_worked
        for data in clock_ins:
            if not data.date_out:
                time_out = now.strftime("%H:%M:%S")
                dt_1 = str(data.date_in) + ' ' + str(data.clocked_in_at)
                dt_2 = str(now.strftime("%Y-%m-%d")) + ' ' + str(now.strftime("%H:%M:%S"))
                dtf = '%Y-%m-%d %H:%M:%S'
                diff = datetime.datetime.strptime(dt_2, dtf) - datetime.datetime.strptime(dt_1, dtf)
                time_list.append(str(diff))
            else:
                time_list.append(data.time_worked)
        totalSecs = 0
        for tm in time_list:
            timeParts = [int(s) for s in tm.split(':')]
            totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
        totalSecs, sec = divmod(totalSecs, 60)
        hr, min = divmod(totalSecs, 60)
        total_time_worked = "%d:%02d:%02d" % (hr, min, sec)


        employee_data = {
            'id': employee.id, 
            'last_name': employee.last_name, 
            'first_name': employee.first_name, 
            'days_worked': days_worked, 
            'total_time_worked': total_time_worked
        }

        context['res'].append(employee_data)


    return render(request, 'all-report.html', context)


def process_all_pdf(request):
    # Create PDF document
    # Populate document with form data -> all clockins for all employees inside date range
    # display all Clock in Data for the range, order by employee's last naem
    pass

def process_employee_pdf(request):
    # Create PDF document
    # Populate document with form data -> all clockins for all employees inside date range
    # Only generate report for one employee
    pass