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
from datetime import datetime
from django.db.models import Q, Exists, OuterRef
from django.templatetags.static import static



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
# @login_required(login_url='login')
def Registration(request):
    return render(request, 'RegistrationPage/registration.html', {})

# @login_required(login_url='login')
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
    ## Filter BookMaster objects that have at least one associated Book with status=1 and is_archived=False
    bookmasters = BookMaster.objects.annotate(
        has_available_book=Exists(
            Book.objects.filter(
                book_master=OuterRef('pk'),
                status=1  # Only Books with status 1 (available)
            )
        )
    ).filter(
        Q(is_archived=False) & Q(has_available_book=True)  # Ensure is_archived=False and the availability condition
    )
    
    current_datetime = datetime.now()
    print("Current datetime (no timezone):", current_datetime)
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(bookmasters, 12)  # Show 12 bookmasters per page
    page_obj = paginator.get_page(page_number)
    
    # Render only the bookmaster cards HTML
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
        authors = [author for author in request.POST.getlist('author[]') if author]  # Filters out empty or null authors
        location = request.POST.get('location')
        status_id = request.POST.get('status')  # Get the status ID directly
        duration = (lambda x: -1 if not x else x)(request.POST.get('duration'))
        late_fee = (lambda x: -1 if not x else x)(request.POST.get('fine'))
        summary = request.POST.get('summary')
        categories = request.POST.getlist('categories')  # Handles multiple categories
        
        # Handle file uploads
        book_pic = request.FILES.get('bookPic')
        soft_copy = request.FILES.get('softcopy')

        print("Book Title:", book_title)
        print("Publisher:", publisher)
        print("Year:", year)
        print("ISBN:", isbn)
        print("Authors:", authors)
        print("Location:", location)
        print("Status ID:", status_id)
        print("Duration:", duration)
        print("Late Fee:", late_fee)
        print("Summary:", summary)
        print("Categories:", categories)
        print("Book Picture:", book_pic)
        print("Soft Copy:", soft_copy)

        
        try:
            # Check if the ISBN already exists
            existing_book = BookMaster.objects.filter(Q(isbn=isbn) & Q(is_archived = True)).first()

            book_master_reference = None

            if existing_book:
                # If ISBN exists, create a new Book instance referencing it
                book = Book(
                    book_master=existing_book,
                    status_id=status_id,
                    qr_value='',  
                    qr_image=''
                )
                book.save()

                book_master_reference = existing_book

            else:
                # If ISBN doesn't exist, create a new BookMaster and Book instance
                book_master = BookMaster(
                    title=book_title,
                    publisher=publisher,
                    year=year,
                    isbn=isbn,
                    late_fee=late_fee,
                    location=location,
                    duration=duration,
                    image=book_pic,
                    summary=summary,
                    soft_copy=soft_copy
                )
                book_master.save()

                book = Book(
                    book_master=book_master,
                    status_id=status_id,
                    qr_value='',  
                    qr_image=''
                )
                book.save()

                book_master_reference = book_master

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

            print('QR Code saved')

            # Save authors
            for author_name in authors:
                if author_name:  # Ensure the author name is not empty
                    # Create and save the author relationship
                    book_author = BookAuthor(author=author_name, book_master=book_master_reference)  # Use the Book instance
                    book_author.save()  # Save each author related to the book

            # Save categories
            for category_id in categories:
                if category_id:  # Ensure the category ID is not empty
                    # Create and save the book-category relationship
                    category = DimCategory.objects.get(category_id=category_id)
                    book_category = BookCategory(book_master=book_master_reference, category=category)  # Use the Book instance
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
def CheckISBN(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn')

        try:
            if BookMaster.objects.filter(isbn = isbn).exists():
                return JsonResponse({'isExist': 'true', 'message': 'This isbn is already exist. Do you wish to add another copy?'})
            else:
                return JsonResponse({'isExist': 'false'})

        except:
            pass


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


# NOTE: FIX THIS
from django.db.models import Prefetch

@login_required(login_url='login')
def GetBooks(request):
    if request.method == 'GET':
        caller = request.GET.get('caller', '')  # Get the caller parameter

        # If the caller is 'Management', get all books regardless of status
        if caller == 'Management':
            bookList = list(
                BookMaster.objects.filter(is_archived = False).values(
                    'book_master_id',
                    'title',
                    'publisher',
                    'year',
                    'isbn',
                    'location',
                    'late_fee',
                )
            )
        else:
            # Get only books with at least one related Book with status 1
            bookList = list(
                BookMaster.objects.filter(
                     Q(is_archived=False) & Q(book__status=1)
                ).distinct().values(
                    'book_master_id',
                    'title',
                    'publisher',
                    'year',
                    'isbn',
                    'location',
                    'late_fee',
                )
            )
        
        formatted_books = [
            {
                'book_master_id': book['book_master_id'],
                'title': book['title'],
                'publisher': book['publisher'],
                'year': book['year'],
                'isbn': book['isbn'],
                'location': book['location'],
                'late_fee': book['late_fee'],
            }
            for book in bookList
        ]

        return JsonResponse({'books': formatted_books})
    
def GetBookMasterBooks(request):
    if request.method == 'GET':
        book_master_id = request.GET.get('BookMasterID')
        print(book_master_id)
        try:
            # Filter books associated with the given book_master_id
            books = Book.objects.filter(book_master=book_master_id)

            # Prepare data list to hold each book's data
            data = []

            for book in books:
                data.append({
                    'book_id': book.book_id,
                    'book_qr_value': book.qr_value,
                    'title': book.book_master.title, 
                    'isbn': book.book_master.isbn,
                    'status' : book.status_id,
                })

            # Return the list of books with their details
            return JsonResponse({'books': data}, status=200)

        except Book.DoesNotExist:
            return JsonResponse({'error': 'BookMaster or Books not found'}, status=404)

def GetBookInfo(request):
    book_master_id = request.GET.get('id')
    try:
        # Check if a BookMaster with the given ID has an associated Book with status 1
        book_master = BookMaster.objects.filter(
            book_master_id=book_master_id
        ).distinct().first()

        if not book_master:
            return JsonResponse({'error': 'Book not found or does not have a book with status 1'}, status=404)

        authors = BookAuthor.objects.filter(book_master=book_master_id).values_list('author', flat=True)
        categories = BookCategory.objects.filter(book_master=book_master_id).values_list('category_id', flat=True)

        data = {
            'book_master_id': book_master.book_master_id,
            'image_url': book_master.image.url if book_master.image and hasattr(book_master.image, 'url') else None,
            'title': book_master.title,
            'isbn': book_master.isbn,
            'publisher': book_master.publisher,
            'year': book_master.year,
            'authors': list(authors),
            'location': book_master.location,
            'duration': book_master.duration,
            'late_fee': book_master.late_fee,
            'categories': list(categories),  # Now just returning the category IDs
            'soft_copy': book_master.soft_copy.url if book_master.soft_copy and hasattr(book_master.soft_copy, 'url') else None,
            'summary': book_master.summary
        }

        return JsonResponse(data)
    except BookMaster.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

    
@login_required(login_url='login')
def GetAccounts(request):
    if request.method == 'GET':
        accountList = list(CustomUser.objects.select_related('status').values(
            
            'first_name',
            'last_name', 
            'id_number', 
            'cellphone_number', 
            'email',
            'is_active'
        ))
        return JsonResponse({'accounts': accountList})

def UpdateStatus(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        status_id = request.POST.get('status')

        try:
            book_id = int(book_id)  # Attempt to parse to integer
            print("Conversion successful:", book_id)
            status_id = int(status_id)  # Attempt to parse to integer
            print("Conversion successful:", status_id)
        except (TypeError, ValueError):
            print("Conversion failed: book_master_id is not a valid integer.")

        try:
            # Retrieve the Book instance and update the status
            book = Book.objects.get(book_id=book_id)
            book.status_id = status_id
            book.save()

            print("SUCCESSFUL")
            return JsonResponse({'isSuccess': 'true', 'message': 'Book status updated successfully.'})            

        except Book.DoesNotExist:
            print("SUCCESSFUL2")

            return JsonResponse({
                'success': "false",
                'message': "Book not found."
            })
        except DimStatus.DoesNotExist:
            print("SUCCESSFUL3")
            return JsonResponse({
                'success': "false",
                'message': "Status not found."
            })
        except Exception as e:
            print("SUCCESSFUL4")
            return JsonResponse({
                'success': "false",
                'message': f"An error occurred: {str(e)}"
            })
    return JsonResponse({
        'success': "false",
        'message': "Invalid request."
    })

@login_required(login_url='login')
def UpdateBook(request):
    if request.method == 'POST':
        book_master_id = request.POST.get('bookMasterID')  # Ensure you have the book ID in your form
        print(type(book_master_id))

        try:
            book_master_id = int(book_master_id)  # Attempt to parse to integer
            print("Conversion successful:", book_master_id)
        except (TypeError, ValueError):
            print("Conversion failed: book_master_id is not a valid integer.")

        book_master = Book.objects.get(book_master_id=book_master_id)

        # Update the fields from the request
        book_master.title = request.POST.get('bookTitle')
        book_master.publisher = request.POST.get('publisher')
        book_master.year = request.POST.get('year')
        book_master.location = request.POST.get('location')
        book_master.late_fee = request.POST.get('fine')
        book_master.duration = request.POST.get('duration')
        book_master.summary = request.POST.get('summary')

        # Handle image upload if provided
        if 'bookPic' in request.FILES:
            book_master.image = request.FILES['bookPic']
        if 'softcopy' in request.FILES:
            book_master.soft_copy = request.FILES['softcopy']
        
        # Save the book
        book_master.save()

        # Clear existing authors and categories, if necessary
        BookAuthor.objects.filter(book_master=book_master_id).delete()
        BookCategory.objects.filter(book_master=book_master_id).delete()

        # Update authors
        authors = request.POST.getlist('author[]')
        for author in authors:
            BookAuthor.objects.create(book_master=book_master_id, author=author)
            
        # Update categories
        categories = request.POST.getlist('categories')

        print(categories)
        for category_id in categories:
            category = DimCategory.objects.get(category_id=category_id)
            BookCategory.objects.create(book_master=book_master_id, category_id=category.category_id)

        return JsonResponse({'isSuccess': 'true', 'message': 'Category added successfuly.'})            

    return JsonResponse({'isSuccess': 'false', 'message': 'Book update unsuccessful. please try again.'})            

@login_required(login_url='login')
def RemoveBook(request):
    if request.method == 'POST':
        book_master_id = request.POST.get('book_master_id')

        try:
            book = BookMaster.objects.get(book_master_id=book_master_id)
            book.is_archived = True
            book.save()

            return JsonResponse({'isSuccess': True})

        except Book.DoesNotExist:
            return JsonResponse({'isSuccess': False, 'message': 'Book not found.'})
        except Exception as e:
            return JsonResponse({'isSuccess': False, 'message': str(e)})

    return JsonResponse({'isSuccess': False, 'message': 'Invalid request method.'})

@login_required(login_url='login')
def TransactionHistory(request):
    return render(request, 'TransactionHistoryPage/transaction-history.html', {})
