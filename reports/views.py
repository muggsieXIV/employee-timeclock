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
        'all_clockins': ClockSystem.objects.filter(employee=employee_id)
    }

    datetimeFormat = '%H:%M:%S'
    sum = datetime.datetime.strptime('00:00:00', datetimeFormat)

    for data in context['all_clockins']:
        print(data.time_worked)
        
        


        



    return render(request, 'employee-report.html', context)



#  c_in = last_login.clocked_in_at
#             c_out = last_login.clocked_out_at
#             d_in = last_login.date_in
#             d_out = now.strftime("%Y-%m-%d")

#             print('*** Finding hours worked...')
#             print('In time: ' + str(c_in))
#             print('Out Time: ' + str(c_out))
#             print("Date in: " + str(d_in))
#             print("Date out: " + str(d_out))

#             print(c_in)
#             print(c_out)
#             print(d_in)
#             print(d_out)
            
#             datetime1_str = str(d_in) + ' ' + str(c_in)
#             print(datetime1_str)
#             datetime2_str = str(d_out) + ' ' + str(c_out)
#             print(datetime2_str)

#             datetimeFormat = '%Y-%m-%d %H:%M:%S'
#             diff = datetime.datetime.strptime(datetime2_str, datetimeFormat) - datetime.datetime.strptime(datetime1_str, datetimeFormat)

