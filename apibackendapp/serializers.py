from rest_framework import serializers
from .models import Department,Employee,Project,UserDetails
from datetime import date
import re
from django.contrib.auth.models import User,Group
from django.contrib.auth.hashers import make_password


#validation1: dateofJoining must be current date
#validation2: employee name should be characters, no special character

#validation of dateofJoining
def date_of_joining_restriction(dateofJoining):
    today=date.today()
    if dateofJoining!=today:
        raise serializers.ValidationError("The date of joining must be today!")
    return dateofJoining

#validation for emloyeeName
def name_validation(employeeName):
    if len(employeeName)<3 or not re.match("^[A-Za-z]+$",employeeName):
        raise serializers.ValidationError("Name must be atleast 3 letters and contain only alphabetical characters")
    return employeeName

#validation for designation
def designation_validaton(designation):
    if not re.match('^[A-Za-z]+$',designation):
        raise serializers.ValidationError("Designation must contain only alphabetical character!")
    return designation

def contact_validation(contact):
    if not re.match('^[0-9]+$',contact):
        raise serializers.ValidationError("Contact must contain only digits!")
    if len(contact)!=10:
        raise serializers.ValidationError("Contact must be exactly 10 digits!")
    return contact

#Department serializer
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Department
        fields='__all__'

#Employee serializer
class EmployeeSerializer(serializers.ModelSerializer):
    Department=DepartmentSerializer(source='DepartmentId',read_only=True)
    DateOfJoining=serializers.DateField(validators=[date_of_joining_restriction])
    EmployeeName=serializers.CharField(max_length=200,validators=[name_validation])
    Designation=serializers.CharField(max_length=200,validators=[designation_validaton])
    Contact=serializers.CharField(max_length=15,validators=[contact_validation])

    #show project details
    project_details=serializers.StringRelatedField(source='projects',many=True,read_only=True)
    class Meta:
        model=Employee 
        fields=('EmployeeId','EmployeeName','Designation','DateOfJoining','Contact','IsActive','DepartmentId','Department','project_details')

class ProjectSerializer(serializers.ModelSerializer):
    #employees--->get the data for employee_Details from employees field of project model
    employee_details=EmployeeSerializer(source='employees',required=False,many=True,read_only=True)
    #read_only=True because only for veiwing
    class Meta:
        model=Project
        fields=('id','name','employees','employee_details')

class UserDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model=UserDetails 
        fields='__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User 
        fields=('id','username')

#Receives the registration data, validates it and hashes the password, creates the user and assigns the user to a
#group and finally returns the created user

class SignUpSerializer(serializers.ModelSerializer):
    group_name=serializers.CharField(write_only=True,required=False)

    def create(self,validated_data):
        group_name=validated_data.pop("group_name",None)

        #Hash the password
        validated_data["password"]=make_password(validated_data.get("password"))

        #creates the user
        user=super(SignUpSerializer,self).create(validated_data)

        if group_name:
            group,created=Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        return user

    class Meta:
        model=User
        fields=['username','password','group_name']

class LoginSerializer(serializers.ModelSerializer):
    #field to get the username from the user
    username=serializers.CharField()
    #field to get password from the user
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['username','password']