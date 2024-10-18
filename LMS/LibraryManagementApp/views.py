from django.shortcuts import render
import os
import qrcode
from django.core.files import File
from django.core.files.base import ContentFile
from io import BytesIO
from django.conf import settings
from django.http import JsonResponse
from .models import *  # Import your custom user model
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.template.loader import render_to_string

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

            user_profile.qr_value = f"QR-{user_profile.id}-{last_name}-{email}"
            user_profile.save()

            # Generate QR code
            qr_img = qrcode.make(user_profile.qr_value)

            # Save the QR code to a BytesIO object
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)

            # Save the QR code to the user's qr_image field
            user_profile.qr_image.save(f'qr_{user_profile.id}.png', ContentFile(qr_buffer.read()), save=True)

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
def LoadBooks(request):
    # Get all books, or filter based on user input if needed
    books = Book.objects.all()
    
    # Pagination
    page_number = request.GET.get('page', 1)  # Get page number from request
    paginator = Paginator(books, 12)  # Show 12 books per page
    page_obj = paginator.get_page(page_number)  # Get the page object
    
    # Render only the book cards HTML
    html = render_to_string('BookCollectionPage/_by-cards.html', {'page_obj': page_obj})
    return JsonResponse({'html': html, 'has_next': page_obj.has_next()})

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
def RegisterBook(request):
    if request.method == 'POST':
        book_title = request.POST.get('bookTitle')
        publisher = request.POST.get('publisher')
        year = request.POST.get('year')
        isbn = request.POST.get('isbn')  # Ensure to include the ISBN field
        authors = request.POST.getlist('author[]')  # Handles multiple authors
        location = request.POST.get('location')
        status_id = request.POST.get('status')  # Get the status ID directly
        duration = request.POST.get('duration')
        late_fee = request.POST.get('fine')
        summary = request.POST.get('summary')
        categories = request.POST.getlist('categories')  # Handles multiple categories
        
        # Handle file uploads
        book_pic = request.FILES.get('bookPic')
        soft_copy = request.FILES.get('softcopy')
        
        try:
            # Create and save the book instance
            book = Book(
                title=book_title,
                publisher=publisher,
                year=year,
                isbn=isbn,
                status_id=status_id,  # Use status_id to set ForeignKey
                late_fee=late_fee,
                duration=duration,
                location=location,
                qr_value='',  # Generate or calculate the QR value as needed
                qr_image='',  # Handle QR image generation/upload separately
                image=book_pic,
                soft_copy=soft_copy,
                summary=summary
            )
            book.save()

            book.qr_value = f"QR-{book.book_id}-{book_title}-{year}-{isbn}"
            book.save()

            # Generate QR code
            qr_img = qrcode.make(book.qr_value)

            # Save the QR code to a BytesIO object
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)

            # Save the QR code to the user's qr_image field
            book.qr_image.save(f'qr_{book.book_id}.png', ContentFile(qr_buffer.read()), save=True)

            # Save authors
            for author_name in authors:
                if author_name:  # Ensure the author name is not empty
                    # Create and save the author relationship
                    book_author = BookAuthor(author=author_name, book=book)  # Use the Book instance
                    book_author.save()  # Save each author related to the book

            # Save categories
            for category_id in categories:
                if category_id:  # Ensure the category ID is not empty
                    # Create and save the book-category relationship
                    category = DimCategory.objects.get(category_id=category_id)
                    book_category = BookCategory(book=book, category=category)  # Use the Book instance
                    book_category.save()  # Save each category related to the book

            # Return a JSON response indicating success
            return JsonResponse({'isSuccess': 'true'})

        except DimCategory.DoesNotExist:
            return JsonResponse({'isSuccess': 'false', 'message': 'Category does not exist.'})

        except ValidationError as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'Validation error: ' + str(e)})

        except Exception as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'An error occurred: ' + str(e)})

    # If not POST, redirect or return an error
    return JsonResponse({'isSuccess': 'false', 'message': 'Invalid request method.'})

@login_required(login_url='login')
def AddCategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('categoryName')

        try:
            if not DimCategory.objects.filter(category_name = category_name).exists():
                newCategory = DimCategory(
                    category_name=category_name)
                newCategory.save()

                return JsonResponse({'isSuccess': 'true', 'message': 'Category added successfuly.'})            
            else:
                 return JsonResponse({'isSuccess': 'false', 'message': 'Category already exists.'})

        except ValidationError as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'Validation error: ' + str(e)})

        except Exception as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'An error occurred: ' + str(e)})

    # If not POST, redirect or return an error
    return JsonResponse({'isSuccess': 'false', 'message': 'Invalid request method.'})

@login_required(login_url='login')
def GetCategories(request):
    if request.method == 'GET':
        categoryList = list(DimCategory.objects.values())
        return JsonResponse({'categories': categoryList})


@login_required(login_url='login')
def BookManagement(request):
    return render(request, 'BookManagementPage/book-management.html', {})

@login_required(login_url='login')
def GetBooks(request):
    if request.method == 'GET':
        bookList = list(Book.objects.select_related('status').values(
            'book_id',
            'title', 
            'publisher', 
            'year', 
            'status__status_name'  # Fetching status name directly
        ))
        return JsonResponse({'books': bookList})

def GetBookInfo(request):
    book_id = request.GET.get('id')
    try:
        book = Book.objects.get(book_id=book_id)
        # Fetch authors related to the book
        authors = BookAuthor.objects.filter(book=book).values_list('author', flat=True)
        data = {
            'title': book.title,
            'year': book.year,
            'isbn': book.isbn,
            'location': book.location,
            'late_fee': book.late_fee,
            'authors': list(authors),
            'image_url': book.image.url, 
            'summary': book.summary
        }
        return JsonResponse(data)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

@login_required(login_url='login')
def TransactionHistory(request):
    return render(request, 'TransactionHistoryPage/transaction-history.html', {})
