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
from django.db.models import Count
from django.db.models import Count, Q, BooleanField, Case, When
from django.utils import timezone
from datetime import timedelta
import json
from django.core.exceptions import ObjectDoesNotExist





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
    # Check if the user is both staff and admin
    if request.user.is_staff and request.user.is_superuser:
        return render(request, 'DashboardPage/dashboard.html', {})
    else:
        return redirect('sbook-collection') 

@login_required(login_url='login')
def BookCollection(request):
    return render(request, 'BookCollectionPage/book-collection.html', {})
  
@login_required(login_url='login')
def LoadBooks(request):
    # Annotate BookMaster objects with the count of associated books with status=1
    bookmasters = BookMaster.objects.annotate(
        available_books=Count(
            'book', 
            filter=Q(book__status=1)  # Adjust this if you need a specific status filter
        )
    ).filter(
        is_archived=False  # Filter out archived books
    )


    current_datetime = datetime.now()
    print("Current datetime (no timezone):", current_datetime)
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(bookmasters, 12)

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

def ReserveBook(request):
    if request.method == 'POST':
        book_master_id = request.POST.get('book_master_id')

        # Find the first available book for the given BookMaster ID with status=1 (available)
        available_book = Book.objects.filter(
            book_master_id=book_master_id,
            status=1  # Assuming 1 means 'available'
        ).first()

        current_user = request.user

        
        if available_book:
            reserved_status = DimStatus.objects.get(status_id=3)  
            available_book.status = reserved_status
            available_book.save()
            
            # Calculate reservation dates
            date_reserved = datetime.now()
            print(date_reserved)
            expiration_date = date_reserved + timedelta(days=1)  
            
            # Create a Reservation record
            reservation = Reservation.objects.create(
                book=available_book,
                date_reserved=date_reserved,
                expiration_date=expiration_date,
                reservist = current_user
            )

            # Check if there are still available books for the given BookMaster ID
            still_available = Book.objects.filter(
                book_master_id=book_master_id,
                status=1  # status=1 means 'available'
            ).exists()
            
            # Return response with success message and availability status
            return JsonResponse({
                'isSuccess': 'true',
                'message': 'Book added to your bag successfully!',
                'stillAvailable': 'true' if still_available else 'false'
            })

        else:
            # No available book found
            return JsonResponse({'status': 'error', 'message': 'No available books found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required(login_url='login')
def LogbookPage(request):
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

        current_user = request.user

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
                    qr_image='',
                    added_by=current_user  # Save the user who added the book

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
                    soft_copy=soft_copy,
                    added_by=current_user  # Save the user who added the book

                )
                book_master.save()

                book = Book(
                    book_master=book_master,
                    status_id=status_id,
                    qr_value='',  
                    qr_image='',
                    added_by=current_user  # Save the user who added the book

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
def GetStatus(request):
    if request.method == 'GET':
        statusList = list(DimStatus.objects.values())
        return JsonResponse({'status': statusList})


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
                BookMaster.objects.filter(is_archived=False).annotate(
                    has_available_books=Case(
                        When(book__status=1, then=True),
                        default=False,
                        output_field=BooleanField()
                    )
                ).values(

                    'book_master_id',
                    'title',
                    'publisher',
                    'year',
                    'isbn',
                    'location',
                    'late_fee',
                    'has_available_books',
                ).distinct()
              
            )
        else:
            # Get only books with at least one related Book with status 1
            bookList = list(
                BookMaster.objects.filter(
                    Q(is_archived=False)
                ).annotate(
                    has_available_books=Case(
                        When(book__status=1, then=True),
                        default=False,
                        output_field=BooleanField()
                    )
                ).values(

                    'book_master_id',
                    'title',
                    'publisher',
                    'year',
                    'isbn',
                    'location',
                    'late_fee',
                    'has_available_books',
                ).distinct()

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
                'has_available_books': book['has_available_books'],

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
            'id',
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

        book_master = BookMaster.objects.get(book_master_id=book_master_id)

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
            book_master.image = request.FILES.get('bookPic')
            print(f"Book Picture: {book_master.image.name}")  # Debug: Check the file name

        if 'softcopy' in request.FILES:
            book_master.soft_copy = request.FILES.get('softcopy')
        
        # Save the book master instance
        book_master.save()

        # Clear existing authors and categories, if necessary
        BookAuthor.objects.filter(book_master=book_master_id).delete()
        BookCategory.objects.filter(book_master=book_master_id).delete()

        # Update authors
        authors = request.POST.getlist('author[]')
        for author in authors:
            BookAuthor.objects.create(book_master=book_master, author=author)
            
        # Update categories
        categories = request.POST.getlist('categories')
        for category_id in categories:
            category = DimCategory.objects.get(category_id=category_id)
            BookCategory.objects.create(book_master=book_master, category=category)

        return JsonResponse({'isSuccess': 'true', 'message': 'Book updated successfully.'})            

    return JsonResponse({'isSuccess': 'false', 'message': 'Book update unsuccessful. Please try again.'})
         

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

def GetAccountInfo(request):
    account_id = request.GET.get('id')
    try:
        account = CustomUser.objects.get(id=account_id)
        data = {
            'account_id': account.id,
            'first_name': account.first_name, 
            'last_name': account.last_name,
            'email': account.email,
            'is_active': account.is_active,
            'id_number': account.id_number,
            'cellphone_number': account.cellphone_number,
            'image_url': account.image.url,
        }

        return JsonResponse(data)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

    

@login_required(login_url='login')
def UpdateAccount(request):
    if request.method == 'POST':
        account_id = request.POST.get('account_id')  # Ensure you have the book ID in your form
        account = CustomUser.objects.get(id=account_id)

        print(account)

        # Update the fields from the request
        account.first_name = request.POST.get('first_name')
        account.last_name = request.POST.get('last_name')
        account.id_number = request.POST.get('id_number')
        account.cellphone_number = request.POST.get('contact_number')
        account.email = request.POST.get('email')

        print(request.FILES.get('profile_picture'))

        # Handle image upload if provided
        if 'profile_picture' in request.FILES:
            account.image = request.FILES.get('profile_picture')
        
        # Save the account
        account.save()

        return JsonResponse({'isSuccess': 'true', 'message': 'Account update successfuly.'})            

    return JsonResponse({'isSuccess': 'false', 'message': 'Account update unsuccessful. please try again.'})
    

@login_required(login_url='login')
def TransactionHistory(request):
    return render(request, 'TransactionHistoryPage/transaction-history.html', {})

def UpdateBagNumber(request):
    current_user = request.user

    try:
        # Get the current time (to filter expiration date)
        now = datetime.now()

        # Build the conditions individually using Q() and combine them with & (AND)
        conditions = Q(reservist=current_user) & Q(is_processed=False) & Q(is_canceled=False) & Q(is_expired=False) & Q(expiration_date__gt=now)

        # Filter reservations using the combined Q object and count
        reservation_count = Reservation.objects.filter(conditions).count()

        # Return the count as a JSON response
        return JsonResponse({'total_reservations': reservation_count})

    except Exception as e:
        # Handle any exceptions and return a failure response
        return JsonResponse({'error': str(e)}, status=500)

#bag page
def GetReserved(request):
    # Get the current logged-in user
    user = request.user

    # Get the current date and time
    current_time = timezone.now()

    # Query reservations with filters applied
    reservations = Reservation.objects.filter(
        reservist=user, 
        expiration_date__gt=current_time, 
        is_processed=False, 
        is_canceled=False, 
        is_expired=False
    ).select_related('book__book_master')  # Use select_related to avoid additional queries

    # Prepare data to return in the DataTable format
    data = []
    for reservation in reservations:
        book = reservation.book.book_master  # Accessing the related BookMaster
        
        # Populate the data list with reservation details
        data.append({
            'book_title': book.title,
            'reservation_date': reservation.date_reserved.strftime('%Y-%m-%d %H:%M:%S'),
            'borrow_duration': book.duration,
            'late_fee': str(book.late_fee),  # Make sure it's a string to display
            'reservation_id': reservation.reservation_id
        })

    # Return data in JSON format
    return JsonResponse({'reserved': data})

def CancelReservation(request):
    if request.method == 'POST':
        # Get the reservation ID fromupdat the AJAX request
        reservation_id = request.POST.get('reservation_id')

        # Get the reservation object or return a 404 if not found
        reservation = Reservation.objects.filter(reservation_id=reservation_id).first()
        if not reservation:
            return JsonResponse({'success': False, 'message': 'Reservation not found.'})

        # Update the is_canceled field to True
        reservation.is_canceled = True
        reservation.save()

        # Update the book's status to 1 (assuming '1' corresponds to an available status in DimStatus)
        book = reservation.book
        available_status = DimStatus.objects.get(pk=1)  # Modify this if '1' isn't the correct ID
        book.status = available_status
        book.save()

        # Return a success response
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def LoadReservedBook(request):
   if request.method == "POST":
        borrower = request.POST.get('borrower')
        print(borrower)
        
        # Try finding the user by QR or email
        user = CustomUser.objects.filter(qr_value=borrower).first()
        if not user:
            user = CustomUser.objects.filter(username=borrower).first()
        
        if not user:
            return JsonResponse({
                'isSuccess': 'false',
                'message': 'User not found.'
            })

        # Get user's reserved and borrowed books
        reserved_books = Reservation.objects.filter(reservist=user, is_processed=False, is_canceled = False, is_expired = False).values(
            'reservation_id',
            'book__book_master__book_master_id', 
            'book__book_master__title', 
            'book__book_master__isbn', 
            'book__book_master__image', 
        )

        print(reserved_books)

        borrowed_books = TransactionDetail.objects.filter(user=user, is_returned=False).values(
            'transaction_detail_id',
            'book__book_master__book_master_id', 
            'book__book_master__title', 
            'book__book_master__isbn', 
            'book__book_master__image', 
            'expected_date_return'
        )
                # Format the reserved and borrowed books
        reserved_books_data = list(reserved_books)
        borrowed_books_data = list(borrowed_books)

        # Get the number of reserved, on-hand, and delayed books
        reserved_books_count = len(reserved_books_data)
        on_hand_books_count = len(borrowed_books_data)
        delayed_books_count = sum(1 for book in borrowed_books_data if timezone.now() > book['expected_date_return'])

        # Return user data and book details
        return JsonResponse({
            'isSuccess': 'true',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'cellphone_number': user.cellphone_number,
                'email': user.email,
                'reserved_books_count': reserved_books_count,
                'on_hand_books_count': on_hand_books_count,
                'delayed_books_count': delayed_books_count,
                'profile_pic':user.image.url,
            },
            'reserved_books': reserved_books_data,
            'borrowed_books': borrowed_books_data
        })
def BorrowSelectedBooks(request):
    if request.method == "POST":
        # Get the list of books to borrow (passed as JSON)
        to_borrow = request.POST.get('to_borrow')
        
        if to_borrow:
            to_borrow = json.loads(to_borrow)  # Convert JSON string to Python list

            try:
                # List to store transaction details
                transaction_details = []
                
                # Iterate over the selected books to borrow
                for reservation_id in to_borrow:
                    # Find the reservation
                    reservation = Reservation.objects.get(reservation_id=reservation_id, is_processed=False)
                    
                    # Ensure that the reservist is not None (i.e., someone made the reservation)
                    if not reservation.reservist:
                        return JsonResponse({'success': False, 'message': f'Reservation {reservation_id} does not have a reservist.'})
                    
                    # Create a TransactionMaster record for the reservist (borrower)
                    transaction_master = TransactionMaster.objects.create(
                        user=reservation.reservist,  # Use the reservist as the borrower
                        approver=request.user,  # You can change approver logic as needed
                        transaction_date=timezone.now()
                    )

                    # Set reservation as processed
                    reservation.is_processed = True
                    reservation.save()

                    # Get the corresponding book and update its status
                    book = reservation.book
                    book.status = DimStatus.objects.get(status_name='Borrowed')  # Update the book status to "Borrowed"
                    book.save()

                    # Create a transaction detail for each borrowed book
                    transaction_detail = TransactionDetail.objects.create(
                        transaction_master=transaction_master,
                        book=book,
                        date_borrowed=timezone.now(),
                        expected_date_return=timezone.now() + timezone.timedelta(days=book.book_master.duration),
                        user=reservation.reservist,  # Borrower is the reservist
                        approver=request.user  # Approver can be different if necessary
                    )

                    transaction_details.append(transaction_detail)

                # Return success response
                return JsonResponse({'success': True, 'transaction_master_id': transaction_master.transaction_master_id})

            except Reservation.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Some reservations not found or already processed.'})
        else:
            return JsonResponse({'success': False, 'message': 'No books selected.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def ReturnSelectedBooks(request):
    if request.method == "POST":
        try:
            # Get the list of transaction detail IDs that the user wants to return
            to_return = request.POST.get('to_return')
            to_return = json.loads(to_return)

            # Query the TransactionDetail objects by IDs in to_return
            transaction_details = TransactionDetail.objects.filter(transaction_detail_id__in=to_return)

            # Loop through each transaction detail and update the book's status and transaction detail status
            for transaction_detail in transaction_details:
                # Get the related book and update its status to "Available"
                book = transaction_detail.book
                available_status = DimStatus.objects.get(status_name="Available")  # Assuming "Available" is a valid status
                book.status = available_status  # Update the book's status to available
                book.save()

                # Mark the transaction as returned
                transaction_detail.is_returned = True
                transaction_detail.actual_date_return = transaction_detail.expected_date_return  # Or you can set the actual return date to now
                transaction_detail.save()

            return JsonResponse({
                'success': True,
            })
        except Exception as e:
            # Log the exception or handle errors as needed
            return JsonResponse({'success': False, 'message': str(e)})

def GetTransaction(request):
    transactions = TransactionMaster.objects.annotate(number_of_books=Count('transactiondetail')).select_related('user', 'approver')
    data = [
        {
            'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'borrower': transaction.user.username,
            'number_of_books': transaction.number_of_books,
            'approver': transaction.approver.first_name + ' ' + transaction.approver.last_name,
        }
        for transaction in transactions
    ]
    return JsonResponse(data, safe=False)

def GetTransactionDetail(request):
    transaction_details = TransactionDetail.objects.select_related('transaction_master', 'book', 'user', 'approver', 'book__book_master', 'book__status')
    
    data = [
        {   'transaction_date': detail.transaction_master.transaction_date.strftime('%Y-%m-%d'),
            'book_title': detail.book.book_master.title,
            'isbn': detail.book.book_master.isbn,
            'date_borrowed': detail.date_borrowed.strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': detail.expected_date_return.strftime('%Y-%m-%d'),
            'date_returned': detail.actual_date_return.strftime('%Y-%m-%d %H:%M:%S') if detail.actual_date_return else 'Not Returned',
            'status': 'Returned' if detail.is_returned else 'In Progress',
            'is_late': 'Yes' if detail.is_late else 'No',
            'fine': str(detail.late_fee) if detail.late_fee else '0.00',
            'borrower': detail.user.first_name + ' ' + detail.user.last_name,
            'approver': detail.approver.first_name + ' ' + detail.approver.last_name,
            'fine_status': (
                'No Fine' if not detail.is_late else 
                'Paid' if detail.is_paid else 
                'Not Paid'
            )  # New field with condition for "No Fine" if not late
        }
        for detail in transaction_details
    ]
    
    return JsonResponse(data, safe=False)

def GetUserProfile(request):
    current_user = request.user
    user_profile = CustomUser.objects.filter(id=current_user.id).first()

    # Serialize user data
    if user_profile:
        data = {
            'id': user_profile.id,
            'name': user_profile.get_full_name(),
            'student_id': user_profile.id_number,
            'contact': user_profile.cellphone_number,
            'email': user_profile.email,
            'image_url': user_profile.image.url if user_profile.image else None,
            'qr_image_url': user_profile.qr_image.url if user_profile.qr_image else None
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'User not found'}, status=404)
    
from django.http import JsonResponse
from datetime import datetime

def GetUserTransaction(request):
    current_user = request.user
    transaction_details = TransactionDetail.objects.select_related(
        'transaction_master', 'book', 'user', 'approver', 'book__book_master', 'book__status'
    ).filter(user=current_user, is_returned = False)  # Filter by the current user
    
    data = [
        {   
            'transaction_date': detail.transaction_master.transaction_date.strftime('%Y-%m-%d'),
            'book_title': detail.book.book_master.title,
            'date_borrowed': detail.date_borrowed.strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': detail.expected_date_return.strftime('%Y-%m-%d'),
            'status': 'Late' if detail.expected_date_return < datetime.now() else 'On Time'
        }
        for detail in transaction_details
    ]
    
    return JsonResponse(data, safe=False)

def InOut(request):
    return render(request, 'InOutPage/inout.html', {})

def CreateLog(request):
    if request.method == 'POST':
        try:
            qr_value = request.POST.get('qr_value')

            # Retrieve the user based on the provided QR value
            user = CustomUser.objects.filter(qr_value=qr_value).first()

            if user:
                # Retrieve the latest log for the user
                latest_log = Logbook.objects.filter(user=user).order_by('-time_in').first()

                # If there's an existing log and the time_out is empty, fill it
                if latest_log and latest_log.time_out is None:
                    latest_log.time_out = timezone.now()
                    latest_log.save()
                else:
                    # Otherwise, create a new log entry with time_in
                    Logbook.objects.create(
                        user=user,
                        time_in=timezone.now()
                    )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def GetLog(request):
    if request.method == 'GET':
        try:
            logs = Logbook.objects.all()  # Retrieve all log entries
            data = [
                {
                    'user': log.user.first_name + " " + log.user.last_name,
                    'id_number': log.user.id_number,
                    'email': log.user.email,
                    'time_in': log.time_in.strftime('%Y-%m-%d %H:%M:%S') if log.time_in else 'Not In',
                    'time_out': log.time_out.strftime('%Y-%m-%d %H:%M:%S') if log.time_out else 'Not Out'
                }
                for log in logs  # Iterate through all logs
            ]
            
            # Ensure data is always an array, even if empty
            return JsonResponse(data, safe=False) if data else JsonResponse([], safe=False)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Logbook records not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
