from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Employee, ClockSystem
import datetime
import bcrypt
import pytz


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
    #### TODO: Set system to User.id via MTM -> Employee
    ##########TODO: if user.id not request.session[user_id] checks
    return render(request, 'clockin-clockout.html', context)


# Clock in and Clock out function
def process_clock(request):
    if 'employee' not in request.POST:
            print("No employee was selected, try again")
            return redirect('/dashboard')


    # if User is not in request.session -> redirect to login
    if 'user_id' not in request.session:
        return redirect('/')

    # Get errors
    errors = ClockSystem.objects.clockin_validator(request.POST)
    if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)  # value is the error message string created in models.py
                # extra_tags is optional and used if we want the error messages by key so we
                # can position them in the HTML is specific locations
            return redirect('/dashboard')
    
    # Get the employee
    e = Employee.objects.get(id=request.POST['employee'])

    now = datetime.datetime.now(pytz.timezone('US/Central'))

    ############
    # if clocking in
    if request.POST['clocksys'] == "clockin":
        if e.is_active == True:
            err_msg = 'failed: ' + e.last_name + ', ' + e.first_name  + ' is already clocked in'
            messages.error(request, err_msg, extra_tags='already_clockedin')
            return redirect('/dashboard')

        ClockSystem.objects.create(
            employee=e,
            in_comment=request.POST['comment'], 
            date_in=now.strftime("%Y-%m-%d"),
            clocked_in_at=now.strftime("%H:%M:%S")
        )
        
        # Set Employee to active
        e.is_active = True
        if e.is_active == False:
            err_msg = 'Employee status update failure, please contact Amy with ErrorCode:EL-172'
            messages.error(request, err_msg, extra_tags='not_clockedin')
            return redirect('/dashboard')
        
        # Save Employee
        e.save()

        success_msg = e.last_name + ', ' + e.first_name + ' was succesfully signed in at ' + str(now.strftime("%I:%M:%S%p"))
        messages.error(request, success_msg, extra_tags='success')

        return redirect('/dashboard')

    ##############  
    # if clocking out
    if request.POST['clocksys'] == 'clockout':
        # Check to make sure the employee is clocked in, and has not clocked out
        if e.is_active != True:
            err_msg = 'failed: ' + e.last_name + ', ' + e.first_name  + ' is not already active'
            messages.error(request, err_msg, extra_tags='not_clockedin')
            return redirect('/dashboard')

        # If employee was clocked in: 
        if e.is_active == True:
            # Get the employee's last clockin
            cs = ClockSystem.objects.all()
            e_cs = cs.filter(employee=request.POST['employee'])
            last_login = e_cs[0]
            for clockins in e_cs:
                if clockins.id > last_login.id:
                    last_login = clockins
            
            # Calculate hours_worked and update clock information. 
            last_login.clocked_out_at = now.strftime("%H:%M:%S")
            c_in = last_login.clocked_in_at
            c_out = last_login.clocked_out_at
            d_in = last_login.date_in
            d_out = now.strftime("%Y-%m-%d")
            
            datetime1_str = str(d_in) + ' ' + str(c_in)
            datetime2_str = str(d_out) + ' ' + str(c_out)

            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            diff = datetime.datetime.strptime(datetime2_str, datetimeFormat) - datetime.datetime.strptime(datetime1_str, datetimeFormat)

            last_login.time_worked = str(diff)
            last_login.out_comment = request.POST['comment']
            last_login.date_out = d_out
            
            # Set employe to inactive
            e.is_active = False

            last_login.save()
            e.save()
            
            success_msg = e.last_name + ', ' + e.first_name + ' successfully signed out at ' + str(now.strftime("%I:%M:%S%p"))
            messages.error(request, success_msg, extra_tags='already_clockedin')

            return redirect('/dashboard')
            
    else:
        print('Something went wrong. Please contact your admninistrator with code:303-B_FAILED/EL-231')
        total_failure = 'Something went wrong. Please contact your admninistrator with code:303-B_FAIL'
        messages.error(request, total_failure, extra_tags='total_failure')

        return redirect('/dashboard')
