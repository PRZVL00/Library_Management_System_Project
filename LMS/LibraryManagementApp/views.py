from django.http import JsonResponse
from .models import *  # Import your custom user model
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError


# Create your views here.
def Login(request):
    return render(request, 'LogInPage/login.html', {})

def VerifyLogin(request):
    print("Verifying")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({'isAuthenticated': False,'message': 'Username and password is required'})
        
        user = authenticate(request, username=username, password=password)

        if user is None:
            return JsonResponse({'isAuthenticated': False,'message': 'Invalid credentials'})
        else:
            login(request, user)

            if user.is_staff: 
               print("Redirecting to dashboard")
               return JsonResponse({'isAuthenticated': True,'message': 'Logged in successfully','url': 'dashboard'})
            else:
               print("Redirecting to book-collection")
               return JsonResponse({'isAuthenticated': True,'message': 'Logged in successfully', 'url': 'book-collection'})


def Forgotpassword(request):
    return render(request, 'ForgotpasswordPage/ForgotpasswordPage.html', {})

def ResetPassAuth(request):
    return render(request, 'ForgotpasswordPage/ResetPassAuthPage/ResetPassAuth.html', {})

def ResetPassword(request):
    return render(request, 'ForgotpasswordPage/ResetPassAuthPage/ResetPasswordPage/ResetPassword.html', {})

def ResetPassSucc(request):
    return render(request, 'ForgotpasswordPage/ResetPassAuthPage/ResetPasswordPage/ResetPassSuccPage/ResetPassSucc.html', {})

# Registration Page Functions
@login_required(login_url='login')
def Registration(request):
    return render(request, 'RegistrationPage/registration.html', {})

@login_required(login_url='login')
def RegisterUser(request):
    if request.method == 'POST':
        profile_picture = request.FILES.get('profilePicture')
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        student_number = request.POST.get('studentNumber')
        email = request.POST.get('email')
        phone_number = request.POST.get('phoneNumber')
        password = request.POST.get('password')

        # Validate that all fields are provided
        if (
            not profile_picture or
            not first_name or
            not last_name or
            not student_number or
            not email or
            not phone_number or
            not password
        ):
            return JsonResponse({'isSuccess': 'false', 'message': 'All fields must be provided'})

        # Check if the email (username) already exists
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'isSuccess': 'false', 'message': 'Email already in use'})

        try:
            # Create the user profile
            user_profile = CustomUser.objects.create(
                image=profile_picture,
                first_name=first_name,
                last_name=last_name,
                id_number=student_number,
                email=email,
                username=email,  # Email used as username
                cellphone_number=phone_number,
            )
            user_profile.set_password(password)
            user_profile.save()

            # Send JSON response for AJAX success
            return JsonResponse({'isSuccess': 'true', 'message': 'User registered successfully!'})

        except ValidationError as e:
            # Return any validation errors
            return JsonResponse({'isSuccess': 'false', 'message': str(e)})

        except Exception as e:
            # Catch any other exceptions
            return JsonResponse({'isSuccess': 'false', 'message': 'An error occurred: ' + str(e)})

    return JsonResponse({'isSuccess': 'false', 'message': 'Invalid request method'})
@login_required(login_url='login')
def Dashboard(request):
    return render(request, 'DashboardPage/dashboard.html', {})

@login_required(login_url='login')
def BookCollection(request):
    return render(request, 'BookCollectionPage/book-collection.html', {})

@login_required(login_url='login')
def BorrowReturn(request):
    return render(request, 'BorrowReturnPage/borrow-return.html', {})

@login_required(login_url='login')
def AccountManagement(request):
    return render(request, 'AccountManagementPage/account-management.html', {})

@login_required(login_url='login')
def Bag(request):
    return render(request, 'BagPage/bag.html', {})

@login_required(login_url='login')
def Logbook(request):
    return render(request, 'LogbookPage/logbook.html', {})

@login_required(login_url='login')
def Profile(request):
    return render(request, 'ProfilePage/profile.html', {})

@login_required(login_url='login')
def BookRegistration(request):
    return render(request, 'BookRegistrationPage/book-registration.html', {})

@login_required(login_url='login')
def BookManagement(request):
    return render(request, 'BookManagementPage/book-management.html', {})

@login_required(login_url='login')
def TransactionHistory(request):
    return render(request, 'TransactionHistoryPage/transaction-history.html', {})
