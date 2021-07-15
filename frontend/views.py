from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Employee, ClockSystem
import datetime
import bcrypt


# Create User View
def create_user(request):
    return render(request, 'create-user.html')


# Create User Method
def process_register(request):
    # will process a new registration
    # first check if receiving a POST request
    # if not a POST request:
    if request.method != "POST":
        return redirect('/create-user')

    # if a valid POST request, continues with checking for errors
    else:
        # check if registration object is valid
        # import list of errors found
        errors = User.objects.user_validator(request.POST)
        # if len(errors) > 0:
        #     for message in errors.values():
        #         message.errors(request, message)
        #     return redirect('/')
        
        # add the error messages to each error if any errors found in the
        # errors list - checks if list is empty or not - uses python message
        # library - need to import at the top
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)  # value is the error message string created in models.py
                # extra_tags is optional and used if we want the error messages by key so we
                # can position them in the HTML is specific locations
            return redirect('/create-user')

        # check if email is already in the database
        user = User.objects.filter(email=request.POST['email'])

        if user:  # if user does exist
            messages.error(request, "Email already exists", extra_tags='email')
            return redirect('/create-user')

        # at this point, all checks pass and we can store the user's data into the database:
        # hash password with Bcrypt - need to import above
        raw_pw = request.POST['password']
        hashed_pw = bcrypt.hashpw(raw_pw.encode(), bcrypt.gensalt()).decode()

        # add user to database:
        User.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            password=hashed_pw,
        )

        return redirect('/')


# Sign in View
def sign_in(request):
    if 'user_id' in request.session:
        return redirect('/dashboard')
    return render(request, 'signin.html')


# Login User Method
def process_login(request):
    # will log in the user
    # first check if receiving a POST request
    # if not a POST request:
    if request.method != "POST":
        return redirect('/')

    # if a valid POST request, check for errors
    else:
        # check if login object is valid
        # import list of errors found
        errors = User.objects.login_validator(request.POST)

        # add the error messages to each error if any errors found in the
        # errors list - checks if list is empty or not - uses python message
        # library - need to import at the top
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)  # value is the error message string created in models.py
            return redirect('/')

        # check if email is already in the database
        user = User.objects.filter(email=request.POST['email'])

        if len(user) == 0:  # if user does NOT exist
            messages.error(request, "Invalid email address or password!", extra_tags='login')
            return redirect('/')

        # at this point, all checks pass and we can now unhash the password
        # unhash password with Bcrypt - need to import above
        login_raw_pw = request.POST['password']

        # checks if the entered password does not match the one in the database
        if not bcrypt.checkpw(login_raw_pw.encode(), user[0].password.encode()):
            messages.error(request, "Invalid email address or password!", extra_tags='login')
            return redirect('/')

        # place the user ID into session - set to the last user created:
        request.session['user_id'] = User.objects.get(email=request.POST['email']).id

        return redirect('/dashboard')


# Logout User
def logout(request):
    request.session.clear()
    return redirect('/')


# Dashboard or clockin/clockout view
def dashboard(request):
    # If user not logged in
    if 'user_id' not in request.session:
        return redirect('/')

    # check active_employees in session is current
    context = {
        'all_employees': Employee.objects.all(),
    }
    #### TODO: Add active employees to the request.session
    return render(request, 'clockin-clockout.html', context)
        


# Clock in and Clock out function
def process_clock(request):

    # if User is not in request.session -> redirect to login
    if 'user_id' not in request.session:
        return redirect('/')

    # Get errors
    errors = ClockSystem.objects.clockin_validator(request.POST)
    if len(errors) > 0:
        for message in errors.values():
            message.errors(request, message)
            print('errors: ' + message.errors(request, message))
        return redirect('/dashboard')
    
    # Define the employee
    e = Employee.objects.get(id=request.POST['employee'])

    # Get the employee 
    print('Clock system initiated by: ' + e.last_name + ', ' + e.first_name)
    now = datetime.datetime.now()
    print('Current Time: ' + str(now))
    print('Clock system requested: ' + request.POST['clocksys'])

    ############
    # if clocking in
    if request.POST['clocksys'] == "clockin":

        print("Clock in initiated for: " + e.last_name + ', ' + e.first_name)

        if e.is_active == True:
            # message.error(request, 'failed: ' + e.last_name + ', ' + e.first_name  + ' is already clocked in')
            print('failed: ' + e.last_name + ', ' + e.first_name  + ' is already active')
            return redirect('/dashboard')

        ClockSystem.objects.create(
            employee=e,
            in_comment=request.POST['comment'], 
            date_in=now.strftime("%Y-%m-%d"),
            clocked_in_at=now.strftime("%H:%M:%S")
        )
        
        print('Updating Employee Status...')
        e.is_active = True

        print('Checking Employee Status...')
        if e.is_active == False:
            print('Failed to update Employee active status')
        if e.is_active == True:
            print('Employee: ' + e.last_name + ', ' + e.first_name + ' updated active status: ' + str(e.is_active))

        e.save()
        if e.is_active == True:
            print('Employee active status successfully updated')
        
        print('Employee: ' + e.last_name + ', ' + e.first_name + ' active:' + str(e.is_active) + ' updated at:' + str(now))
        print(e)
        success = e.last_name + ', ' + e.first_name + ' was succesfully signed in'
        print(success)
        return redirect('/dashboard')

    ##############  
    # if clocking out
    if request.POST['clocksys'] == 'clockout':
        # Check to make sure the employee is clocked in, and has not clocked out
        if e.is_active != True:
            print('*** Failed: Employee ' + e.last_name + ', ' + e.first_name + ' is not clocked in. ***')
            return redirect('/dashboard')
        # If employee was clocked in: 
        if e.is_active == True:
            print('Employee current is_active status: ' + str(e.is_active))
            print('Fetching last login for employee: ' + e.last_name + ', ' + e.first_name + ' ...')
            # Get the employee's last clockin
            cs = ClockSystem.objects.all()
            e_cs = cs.filter(employee=request.POST['employee'])
            last_login = e_cs[len(e_cs) - 1]
            if last_login:
                print("Last login for: " + e.last_name + ', ' + e.first_name + ' successfully loaded: True')
                print("Employee: " + e.last_name + ', ' + e.first_name + ' clocked in at: ' + str(last_login.clocked_in_at))
            
            # Calculate hours_worked and update clock information. 
            last_login.clocked_out_at = now.strftime("%H:%M:%S")
            print("Employee: " + e.last_name + ", " + e.first_name + ", clocking out at: " + str(last_login.clocked_out_at))
            
            c_in = last_login.clocked_in_at
            c_out = last_login.clocked_out_at
            d_in = last_login.date_in
            d_out = now.strftime("%Y-%m-%d")

            print('*** Finding hours worked...')
            print('In time: ' + str(c_in))
            print('Out Time: ' + str(c_out))
            print("Date in: " + str(d_in))
            print("Date out: " + str(d_out))

            print(c_in)
            print(c_out)
            print(d_in)
            print(d_out)
            
            datetime1_str = str(d_in) + ' ' + str(c_in)
            print(datetime1_str)
            datetime2_str = str(d_out) + ' ' + str(c_out)
            print(datetime2_str)

            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            diff = datetime.datetime.strptime(datetime2_str, datetimeFormat) - datetime.datetime.strptime(datetime1_str, datetimeFormat)

            # print("Difference:", diff)
            # print("Days:", diff.days)
            # print("Microseconds:", diff.microseconds)
            # print("Seconds:", diff.seconds)

            last_login.time_worked = str(diff)
            print("Clock-In / Clock-Out Time Difference: " + last_login.time_worked)

            last_login.out_comment = request.POST['comment']
            print("Employee: " + e.last_name + ', ' + e.first_name + ', Logging out comment: ' + last_login.out_comment)

            last_login.date_out = d_out
            print("Date logged out: " + str(last_login.date_out))
            
            # last_login.save()
            print(e.last_name + ', ' + e.first_name + ' ' + last_login.time_worked + ' ' + last_login.in_comment + ' ' + last_login.out_comment)
            # Set employe to inactive
            e.is_active = False
            # e.save()
            print("Employee active status set: " + str(e.is_active))

            last_login.save()
            e.save()

            return redirect('/dashboard')
            
    else:
        print('Something went wrong. Please contact your admninistrator with code:303-B_FAIL')
        return(redirect('/'))


# Deletng clockSystem Data
def process_remove_clocksys(request, clockSys_id):
    if 'user_id' not in request.session:
        return redirect('/')
    clocksys_to_delete = ClockSystem.objects.get(id=clockSys_id)
    clocksys_to_delete.delete()
    return redirect('/dashboard')

# def process_remove_employee(request, employee_id):
#     if 'user_id' not in request.session:
#         return redirect('/')
#     emp_to_del = Employee.objects.get(id=employee_id)
#     emp_to_del.delete()
#     return redirect('/dashboard')
