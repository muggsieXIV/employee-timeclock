from django.db import models
import re  # in order to use the regex module
from datetime import date, datetime, timedelta  # to use the current date


# Create your models here.
class UserManager(models.Manager):
    # create validations - one for registration, one for login
    def user_validator(self, post_data):
        errors = {}

        # regex imported above
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        # test whether a field matches the pattern
        # The EMAIL_REGEX object has a method called .match() that will return None if no match can be found. If the argument matches the regular expression, a match object instance is returned.
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Invalid email address!"

        # First Name - required; at least 2 characters; letters only
        if len(post_data['first_name']) == 0:
            errors['first_name'] = "First name required"

        if len(post_data['first_name']) < 2:
            errors['first_name'] = "First name must be at least 2 characters"

        # returns a boolean that shows whether a string contains only alphabetic characters
        if not str.isalpha(post_data['first_name']):
            errors['first_name'] = "First name must be letters only"

        # Last Name - required; at least 2 characters; letters only
        if len(post_data['last_name']) == 0:
            errors['last_name'] = "Last name required"

        if len(post_data['last_name']) < 2:
            errors['last_name'] = "Last name must be at least 2 characters"

        # returns a boolean that shows whether a string contains only alphabetic characters
        if not str.isalpha(post_data['last_name']):
            errors['last_name'] = "Last name must be letters only"

            # Password - required; at least 8 characters; matches password confirmation
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters"

        if post_data['password'] != post_data['password_confirm']:
            errors['password_confirm'] = "Passwords must match"


        return errors

    def login_validator(self, post_data):
        errors = {}

        # regex imported above
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        # test whether a field matches the pattern
        # The EMAIL_REGEX object has a method called .match() that will return None if no match can be found. If the argument matches the regular expression, a match object instance is returned.
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Invalid email address or password!"

        # Password - required; at least 8 characters; matches password confirmation
        if (len(post_data['password']) < 8):
            errors['password'] = "Invalid email address or password!"

        return errors

class User(models.Model):
    # user information
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # add for manager validator
    objects = UserManager()



class EmployeeManager(models.Manager):
    def employee_validator(self, form_data):
        errors = {}
        if len(form_data['first_name']) < 2:
            errors['first_name'] = "First Name is not long enough. Try again!"
        if len(form_data['last_name']) < 2:
            errors['last_name'] = "Last Name is not long enough. Try again!"
        return errors

class Employee(models.Model):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    is_active=models.BooleanField(default=False)
    objects=EmployeeManager()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            'last_name',
            'first_name',
            'is_active',
        )

    def __str__(self):
        return(self.last_name + ', ' + self.first_name)


class ClockSystemManager(models.Manager):
    def clockSystem_validator(self, form_data):
        errors = {}
        if len(form_data['employee']) <= 0:
            errors['employee'] = "No employee was selected, try again"
        return errors
    def clockin_validator(self, form_data):
        errors = {}
        if len(form_data['comment']) == 1:
            errors['comment'] = "Please be descriptive if there is an issue."
        return errors
    def clockout_validator(self, form_data):
        errors = {}
        if len(form_data['comment']) == 1:
            errors['comment'] = "Please be descriptive if there is an issue."
        return errors

class ClockSystem(models.Model):
    employee=models.ForeignKey(Employee, related_name="clockSystem", on_delete=models.CASCADE)
    location=models.CharField(max_length=60, null=True)
    role=models.CharField(max_length=80, null=True)
    time_worked=models.CharField(max_length=255, null=True)
    in_comment=models.TextField(null=True)
    out_comment=models.TextField(null=True)
    date_in=models.DateField(null=True)
    date_out=models.DateField(null=True)
    clocked_in_at=models.TimeField()
    clocked_out_at=models.TimeField(null=True)
    objects=ClockSystemManager()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            'date_in',
            'date_out',
            'clocked_in_at',
            'clocked_out_at',
            'employee',
            'location',
            'role',
            'time_worked',
            'in_comment',
            'out_comment',
        )

