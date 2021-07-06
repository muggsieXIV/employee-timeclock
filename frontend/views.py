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
        if len(errors) > 0:
            for message in errors.values():
                message.errors(request, message)
            return redirect('/')
        
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
        'active_employees': []
    }
    for employee in context['all_employees']:
        if employee.is_active == True:
            context['active_employees'] += employee.id
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

    # Get the employee 
    employee = request.POST['employee']
    print('employee clocking in: ' + employee)

    e = Employee.objects.get(id=request.POST['employee'])
    print(e)
    # print(e.firstname + ' is now active: ' + e.is_active)

    ############
    # if clocking in
    if request.POST['clocksys'] == "clockin":
        print("Clock in initiated for: " + e.last_name + ', ' + e.first_name)
        # if e.id in request.session['active_employees']:
        #     message.error(request, e.last_name + ", " + e.first_name + " is already clocked in")
        #     return redirect('/dashboard')
        if e.is_active == True:
            message.error(request, 'failed: ' + e.last_name + ', ' + e.first_name  + ' is already clocked in')
            print('failed: ' + e.last_name + ', ' + e.first_name  + ' is already clocked in')
            return redirect('/dashboard')

        now = datetime.datetime.now()

        ClockSystem.objects.create(
            employee=e,
            comment=request.POST['comment'],
            date_worked=now.strftime("%Y-%m-%d"),
            clocked_in_at=now.strftime("%H:%M:%S")
        )
        e.is_active = True
        print('Employee: ' + e.last_name + ', ' + e.first_name + ' active status: ' + str(e.is_active))
        message.error(request, e.last_name + ', ' + e.first_name + " was successfully signed in!")
        e.save()
        print(str(e))
        print(e)
        print(e.last_name + ', ' + e.first_name + ' was succesfully signed in')
        return redirect('/dashboard')

    ##############  
    # if clocking out
    if request.POST['clocksys'] == 'clockout':
        # check if employee object is valid
        if len(e) == 0:
            message.error(request, "Employee not found, try again")
            return redirect('/dashboard')
        
        # Check to make sure the employee is clocked in, and has not clocked out
        if e.id not in request.session['active_employees']:
            message.error(request, e.last_name + ", " + e.first_name + " is not signed in.")
            redirect('/dashboard')

        # Get clockin from earlier
        data = ClockSystem.objects.last()
        
        # set employee to inactive
        e.is_active = False
        # remove employee from session
        request.session['active_employees'].pop(e.id)

        now = datetime.datetime.now()

        data.clocked_out_at = now.strftime("%H:%M:%S")
        # get hours
        
        # get minutes
        
        data.comment += request.POST['comment']
        
        message.error(request, e.last_name + ", " + e.first_name + " was successfully clocked out!")
        return redirect('/dashboard')



