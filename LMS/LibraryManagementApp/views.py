from django.http import JsonResponse
from .models import *  # Import your custom user model
from django.core.files.storage import default_storage
from django.shortcuts import render

# Create your views here.
def Login(request):
    return render(request, 'LogInPage/login.html', {})

def Forgotpassword(request):
    return render(request, 'ForgotpasswordPage/ForgotpasswordPage.html', {})

def ResetPassAuth(request):
    return render(request, 'ForgotpasswordPage/ResetPassAuthPage/ResetPassAuth.html', {})

def ResetPassword(request):
    return render(request, 'ForgotpasswordPage/ResetPassAuthPage/ResetPasswordPage/ResetPassword.html', {})

def ResetPassSucc(request):
    return render(request, 'ForgotpasswordPage/ResetPassAuthPage/ResetPasswordPage/ResetPassSuccPage/ResetPassSucc.html', {})

# Registration Page Functions
def Registration(request):
    return render(request, 'RegistrationPage/registration.html', {})

def RegisterUser(request):
    if request.method == 'POST':
        profile_picture = request.FILES.get('profilePicture')
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        student_number = request.POST.get('studentNumber')
        email = request.POST.get('email')
        phone_number = request.POST.get('phoneNumber')
        password = request.POST.get('password')

        # Create user profile
        user_profile = CustomUser.objects.create(
            image=profile_picture,
            first_name=first_name,
            last_name=last_name,
            id_number=student_number,
            email=email,
            username = email,
            cellphone_number=phone_number,
        )
        user_profile.set_password(password)
        user_profile.save()

        # Send JSON response for AJAX success
        return JsonResponse({'isSuccess':'true', 'message': 'User registered successfully!'})

    return JsonResponse({'isSuccess':'false', 'message': 'User registered failed!'})
def Dashboard(request):
    return render(request, 'DashboardPage/dashboard.html', {})

def BookCollection(request):
    return render(request, 'BookCollectionPage/book-collection.html', {})

def BorrowReturn(request):
    return render(request, 'BorrowReturnPage/borrow-return.html', {})

def AccountManagement(request):
    return render(request, 'AccountManagementPage/account-management.html', {})

def Bag(request):
    return render(request, 'BagPage/bag.html', {})

def Logbook(request):
    return render(request, 'LogbookPage/logbook.html', {})

def Profile(request):
    return render(request, 'ProfilePage/profile.html', {})

def BookRegistration(request):
    return render(request, 'BookRegistrationPage/book-registration.html', {})

def BookManagement(request):
    return render(request, 'BookManagementPage/book-management.html', {})

def TransactionHistory(request):
    return render(request, 'TransactionHistoryPage/transaction-history.html', {})
