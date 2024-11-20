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
from datetime import datetime, timedelta
from django.db.models import Q, Exists, OuterRef
from django.templatetags.static import static
from django.db.models import Count
from django.db.models import Count, Q, BooleanField, Case, When
from django.utils import timezone
from datetime import timedelta
import json
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd
from django.db.models.functions import TruncDate
from django.utils.timezone import make_aware
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from io import BytesIO


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
        if CustomUser.objects.filter(Q(email=email) & Q(is_active=True)).exists():
            return JsonResponse({'isSuccess': 'false', 'message': 'Email already in use'})
        
        if CustomUser.objects.filter(Q(email=email) & Q(is_active=False)).exists():
            return JsonResponse({'isSuccess': 'false', 'message': 'This email is already registered but inactive. Please proceed to the librarian to activate the account.'})
        
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

            # Send welcome email with QR code
            subject = "Welcome to the School Library"
            context = {
                'username': user_profile.username,
                'first_name': user_profile.first_name,
                'last_name': user_profile.last_name,
            }
            html_message = render_to_string('Email/welcomeUser.html', context)
            plain_message = strip_tags(html_message)  # Fallback to plain text
            from_email = 'no-reply@pnhslibrarymanagemensystem.site'  # Replace with your sender email
            recipient_list = [user_profile.email]

            # Prepare email with attachment
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=recipient_list,
            )
            email_message.attach_alternative(html_message, "text/html")

            # Attach the QR image
            qr_buffer.seek(0)  # Reset buffer pointer
            email_message.attach(f'QR_{user_profile.id}.png', qr_buffer.read(), 'image/png')

            # Send email
            email_message.send()

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
    if request.user.is_staff or  request.user.is_superuser:
        return render(request, 'DashboardPage/dashboard.html', {})
    else:
        return redirect('book-collection') 

@login_required(login_url='login')
def BookCollection(request):
    return render(request, 'BookCollectionPage/book-collection.html', {})
  
@login_required(login_url='login')
def LoadBooks(request):
    # Get the search term and selected categories from the request
    search_term = request.GET.get('search', '').strip()
    selected_categories = request.GET.get('categories', '').split(',')

    print(search_term)
    print(selected_categories)

    # Filter out empty strings from selected_categories
    selected_categories = [cat_id for cat_id in selected_categories if cat_id]

    # Start with the base queryset for BookMaster
    bookmasters = BookMaster.objects.annotate(
        available_books=Count(
            'book', 
            filter=Q(book__status=1)  # Adjust this if you need a specific status filter
        )
    ).filter(
        is_archived=False  # Filter out archived books
    )

    # If a search term is provided, filter the bookmasters based on relevant fields
    if search_term:
        bookmasters = bookmasters.filter(
            Q(title__icontains=search_term) |
            Q(isbn__icontains=search_term) |
            Q(location__icontains=search_term) |
            Q(summary__icontains=search_term) |
            Q(year__icontains=search_term) |
            Q(publisher__icontains=search_term) |
            Q(bookauthor__author__icontains=search_term)  # Assuming related name is 'bookauthor'
        ).distinct()

    # If categories are selected and valid, filter based on the selected categories
    if selected_categories:
        bookmasters = bookmasters.filter(
            bookcategory__category__category_id__in=[int(cat_id) for cat_id in selected_categories]
        )

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(bookmasters, 12)
    page_obj = paginator.get_page(page_number)
    
    # Render only the bookmaster cards HTML
    html = render_to_string('BookCollectionPage/_by-cards.html', {'page_obj': page_obj})
    
    return JsonResponse({'html': html, 'has_next': page_obj.has_next()})


@login_required(login_url='login')
def BorrowReturn(request):
    if request.user.is_staff or  request.user.is_superuser:
        return render(request, 'BorrowReturnPage/borrow-return.html', {})
    else:
        return redirect('book-collection')

@login_required(login_url='login')
def AccountManagement(request):
    if request.user.is_staff or  request.user.is_superuser:
        return render(request, 'AccountManagementPage/account-management.html', {})
    else:
        return redirect('book-collection')

@login_required(login_url='login')
def Bag(request):
    return render(request, 'BagPage/bag.html', {})

@login_required(login_url='login')
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
                'stillAvailable': still_available
            })

        else:
            # No available book found
            return JsonResponse({'status': 'error', 'message': 'No available books found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required(login_url='login')
def LogbookPage(request):
    if request.user.is_staff or  request.user.is_superuser:
        return render(request, 'LogbookPage/logbook.html', {})
    else:
        return render(request, 'LogbookPage/logbook.html', {})

@login_required(login_url='login')
def Profile(request):
    return render(request, 'ProfilePage/profile.html', {})

@login_required(login_url='login')
def BookRegistration(request):
    if request.user.is_staff or  request.user.is_superuser:
        return render(request, 'BookRegistrationPage/book-registration.html', {})
    else:
        return redirect('book-collection')
    

@login_required(login_url='login')
def BookManagement(request):
    if request.user.is_staff or  request.user.is_superuser:
        return render(request, 'BookManagementPage/book-management.html', {})
    else:
        return redirect('book-collection')
    

@login_required(login_url='login')
def RegisterBook(request):
    if request.method == 'POST':
        book_title = request.POST.get('bookTitle')
        publisher = request.POST.get('publisher')
        year = request.POST.get('year')
        isbn = request.POST.get('isbn')  # Ensure to include the ISBN field
        authors = [author for author in request.POST.getlist('author[]') if author]  # Filters out empty or null authors
        location = request.POST.get('location')
        duration = request.POST.get('duration')
        summary = request.POST.get('summary')
        categories = request.POST.getlist('categories')  # Handles multiple categories
        copies = int(request.POST.get('copies', 1))  # Ensure copies is an integer, default to 1 if not provided
        
        # Handle file uploads
        book_pic = request.FILES.get('bookPic')
        soft_copy = request.FILES.get('softcopy')

        if not summary:
            summary = "No summary available"

        if not location:
            location = "Unknown"

        current_user = request.user

        try:
            # Check if the ISBN already exists
            existing_book = BookMaster.objects.filter(Q(isbn=isbn) & Q(is_archived=False)).first()

            book_master_reference = None

            if existing_book:
                # If ISBN exists, create new Book instances referencing it
                book_master_reference = existing_book

            else:
                # If ISBN doesn't exist, create a new BookMaster instance
                book_master = BookMaster(
                    title=book_title,
                    publisher=publisher,
                    year=year,
                    isbn=isbn,
                    late_fee=0,
                    location=location,
                    duration=duration,
                    image=book_pic,
                    summary=summary,
                    soft_copy=soft_copy,
                    added_by=current_user  # Save the user who added the book
                )
                book_master.save()
                book_master_reference = book_master

            # Save authors (this should happen once for each book_master_reference)
            for author_name in authors:
                if author_name:
                    book_author = BookAuthor(author=author_name, book_master=book_master_reference)
                    book_author.save()

            # Save categories
            is_main_assigned = False  # Track if the main category has been assigned
            for category_id in categories:
                if category_id:
                    category = DimCategory.objects.get(category_id=category_id)
                    book_category = BookCategory(
                        book_master=book_master_reference,
                        category=category,
                        is_main=not is_main_assigned  # Set is_main=True for the first iteration only
                    )
                    book_category.save()
                    is_main_assigned = True  # Update the flag after the first category is saved

            # Save multiple copies of the book
            for _ in range(copies):
                book = Book(
                    book_master=book_master_reference,
                    status_id=1,
                    qr_value='',  
                    qr_image='',
                    added_by=current_user  # Save the user who added the book
                )
                book.save()

            # After creating the books, generate and assign QR codes
            for book in Book.objects.filter(book_master=book_master_reference):
                book.qr_value = f"QR-{book.book_id}-{book_title}-{year}-{isbn}"
                book.save()

                # Generate QR code
                qr_img = qrcode.make(book.qr_value)

                # Save the QR code to a BytesIO object
                qr_buffer = BytesIO()
                qr_img.save(qr_buffer, format='PNG')
                qr_buffer.seek(0)

                # Save the QR code to the book's qr_image field
                book.qr_image.save(f'qr_{book.book_id}.png', ContentFile(qr_buffer.read()), save=True)

            print('QR Code saved')

            # Return a JSON response indicating success
            return JsonResponse({'isSuccess': 'true'})

        except DimCategory.DoesNotExist:
            return JsonResponse({'isSuccess': 'false', 'message': 'Category does not exist.'})

        except ValidationError as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'Validation error: ' + str(e)})

        except Exception as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'An error occurred: ' + str(e)})

    # If not POST, return an error
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
def AddBookCopy(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn')  # Retrieve ISBN from the POST request
        current_user = request.user  # Get the logged-in user

        try:
            # Check if a BookMaster with the given ISBN exists and is not archived
            book_master = BookMaster.objects.filter(Q(isbn=isbn) & Q(is_archived=False)).first()

            if not book_master:
                return JsonResponse({'isSuccess': 'false', 'message': 'Book with the provided ISBN does not exist.'})

            # Create a new Book instance linked to the existing BookMaster
            book = Book(
                book_master=book_master,
                status_id=1,  # Set an initial status, e.g., available
                qr_value='',  # Will be updated later
                qr_image='',  # Will be updated later
                added_by=current_user  # Track which user added the book copy
            )
            book.save()

            # Generate and assign QR codes for the new Book
            book.qr_value = f"QR-{book.book_id}-{book_master.title}-{book_master.year}-{isbn}"
            book.save()

            # Generate QR code
            qr_img = qrcode.make(book.qr_value)

            # Save the QR code to a BytesIO object
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)

            # Save the QR code to the book's qr_image field
            book.qr_image.save(f'qr_{book.book_id}.png', ContentFile(qr_buffer.read()), save=True)

            return JsonResponse({'isSuccess': 'true', 'message': 'Book copy added successfully.'})

        except Exception as e:
            return JsonResponse({'isSuccess': 'false', 'message': f'An error occurred: {str(e)}'})

    # If not POST, return an error
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
def GetStatus(request):
    if request.method == 'GET':
        statusList = list(DimStatus.objects.values())
        return JsonResponse({'status': statusList})

@login_required(login_url='login')
def GetBooks(request):
    if request.method == 'GET':
        caller = request.GET.get('caller', '')  # Get the caller parameter

        # If the caller is 'Management', get all books regardless of status
        if caller == 'Management':
            bookList = list(
                BookMaster.objects.filter(is_archived=False).annotate(
                    has_invalid_books=Case(
                        When(book__status__in=[1, 2], then=False),
                        default=True,
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
                    'has_invalid_books',  # Add this field to the response
                ).distinct()
            )
        else:
            # Get only books with at least one related Book with status 1
            bookList = list(
                BookMaster.objects.filter(
                    Q(is_archived=False)
                ).annotate(
                    has_invalid_books=Case(
                        When(book__status__in=[1, 2], then=False),
                        default=True,
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
                    'has_invalid_books',  # Add this field to the response
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
                'has_invalid_books': book['has_invalid_books'],  # Add this field to the formatted books
            }
            for book in bookList
        ]

        return JsonResponse({'books': formatted_books})

    
@login_required(login_url='login')
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

@login_required(login_url='login')
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
        ).order_by('-is_active'))  # Inactive accounts will appear last
        return JsonResponse({'accounts': accountList})


@login_required(login_url='login')
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
            book_master = BookMaster.objects.get(book_master_id=book_master_id)

            # Check if any related books have a status other than 1 or 2
            invalid_books = book_master.book_set.filter(~Q(status__in=[1, 2])).exists()

            if invalid_books:
                return JsonResponse({'isSuccess': False, 'message': 'Cannot delete book master. Some related books have invalid status.'})

            # Proceed with archiving the book master
            book_master.is_archived = True
            book_master.save()

            return JsonResponse({'isSuccess': True})

        except BookMaster.DoesNotExist:
            return JsonResponse({'isSuccess': False, 'message': 'Book master not found.'})
        except Exception as e:
            return JsonResponse({'isSuccess': False, 'message': str(e)})

    return JsonResponse({'isSuccess': False, 'message': 'Invalid request method.'})

@login_required(login_url='login')
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
            'is_staff': account.is_staff
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

        if request.POST.get('position') == "0":
            account.is_staff = False
        else:
            account.is_staff = True

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
    if request.user.is_staff or request.user.is_superuser:
        return render(request, 'TransactionHistoryPage/transaction-history.html', {})
    else:
        return render(request, 'TransactionHistoryPage/transaction-history.html', {})

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def LoadProfile(request):
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
   
@login_required(login_url='login')
def GetToBorrow(request):
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

        reserved_books = Reservation.objects.filter(
            reservist=user, is_processed=False, is_canceled=False, is_expired=False
        ).values(
            'reservation_id',  # ID for checkbox
            'book__book_master__title',  # Book title
            'book__book_master__isbn',  # ISBN
            'book__book_master__book_master_id',  # Book master ID for More Info button
        )

        # Format the reserved books
        reserved_books_data = list(reserved_books)

        # Return only the necessary data for the DataTable
        return JsonResponse({
            'isSuccess': 'true',
            'reserved_books': reserved_books_data
        })

@login_required(login_url='login')
def GetToReturn(request):
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

        # Get user's borrowed books (only non-returned books)
        borrowed_books = TransactionDetail.objects.filter(user=user, is_returned=False).values(
            'transaction_detail_id',
            'book__book_master__book_master_id', 
            'book__book_master__title', 
            'book__book_master__isbn', 
            'book__book_master__image', 
            'expected_date_return'
        )
        
        # Format the borrowed books
        borrowed_books_data = list(borrowed_books)

        # Return user data and book details
        return JsonResponse({
            'isSuccess': 'true',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'cellphone_number': user.cellphone_number,
                'email': user.email,
                'profile_pic': user.image.url,
            },
            'borrowed_books': borrowed_books_data
        })


@login_required(login_url='login')
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

@login_required(login_url='login')
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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    specific_date = request.GET.get('specific_date')
    date_count = int(request.GET.get('date_count', 0))

    print(start_date, end_date, specific_date, date_count)

    # Query to get transactions with the number of books
    if request.user.is_staff or  request.user.is_superuser:
        transactions = TransactionMaster.objects.annotate(number_of_books=Count('transactiondetail')).select_related('user', 'approver')
    else:
        transactions = TransactionMaster.objects.annotate(number_of_books=Count('transactiondetail')).select_related('user', 'approver').filter(user = request.user)

    # Debugging: print the incoming parameters to the console
    print(f"Start Date: {start_date}, End Date: {end_date}, Specific Date: {specific_date}, Date Count: {date_count}")

    # Apply the filters based on the date_count
    if date_count == 2 and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        transactions = transactions.filter(
            transaction_date__date__gte=start_date,
            transaction_date__date__lte=end_date
        )
        print(f"Filtering by date range: {start_date} to {end_date}")
    elif date_count == 1 and specific_date:
        specific_date = datetime.strptime(specific_date, '%Y-%m-%d').date()
        transactions = transactions.filter(
            transaction_date__date=specific_date
        )
        print(f"Filtering by specific date: {specific_date}")

    # Debugging: Print out the number of transactions after filtering
    print(f"Filtered transactions count: {transactions.count()}")

    # Prepare the data for the response
    data = [
        {
            'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'borrower': transaction.user.username,
            'number_of_books': transaction.number_of_books,
            'approver': f"{transaction.approver.first_name} {transaction.approver.last_name}",
        }
        for transaction in transactions
    ]
    
    return JsonResponse(data, safe=False)

@login_required(login_url='login')
def GetTransactionDetail(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    specific_date = request.GET.get('specific_date')
    date_count = int(request.GET.get('date_count', 0))

    print(f"Start Date: {start_date}, End Date: {end_date}, Specific Date: {specific_date}, Date Count: {date_count}")

    if request.user.is_staff or  request.user.is_superuser:
        transaction_details = TransactionDetail.objects.select_related(
                'transaction_master', 'book', 'user', 'approver', 'book__book_master', 'book__status')
    else:
        transaction_details = TransactionDetail.objects.select_related(
                'transaction_master', 'book', 'user', 'approver', 'book__book_master', 'book__status').filter(user = request.user)

    # Apply the filters based on the date_count
    if date_count == 2 and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        transaction_details = transaction_details.filter(
            transaction_master__transaction_date__date__gte=start_date,
            transaction_master__transaction_date__date__lte=end_date
        )
        print(f"Filtering by date range: {start_date} to {end_date}")
    elif date_count == 1 and specific_date:
        specific_date = datetime.strptime(specific_date, '%Y-%m-%d').date()
        transaction_details = transaction_details.filter(
            transaction_master__transaction_date__date=specific_date
        )
        print(f"Filtering by specific date: {specific_date}")

    # Debugging: Print out the number of transaction details after filtering
    print(f"Filtered transaction details count: {transaction_details.count()}")

    data = [
        {
            'transaction_date': detail.transaction_master.transaction_date.strftime('%Y-%m-%d'),
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
            )
        }
        for detail in transaction_details
    ]

    return JsonResponse(data, safe=False)

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def CreateLog(request):
    if request.method == 'POST':
        try:
            qr_value = request.POST.get('qr_value')

            # Check if the QR value exists
            user = CustomUser.objects.filter(qr_value=qr_value).first()
            if not user:
                return JsonResponse({'success': False, 'message': 'Invalid QR code. Please try again.'})

            # Retrieve the latest log for the user
            latest_log = Logbook.objects.filter(user=user).order_by('-time_in').first()

            if latest_log and latest_log.time_out is None:
                # User is logging out
                latest_log.time_out = timezone.now()
                latest_log.save()
                return JsonResponse({'success': True, 'message': 'Thank you!'})
            else:
                # User is logging in
                Logbook.objects.create(user=user, time_in=timezone.now())
                return JsonResponse({'success': True, 'message': 'Welcome!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

@login_required(login_url='login')
def GetLog(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    specific_date = request.GET.get('specific_date')
    date_count = int(request.GET.get('date_count', 0))

    print(start_date, end_date, specific_date, date_count)
    
    if request.user.is_staff or  request.user.is_superuser:
        logs = Logbook.objects.all()
    else:
        logs = Logbook.objects.filter(user = request.user)


    # Filtering based on date inputs
    if date_count == 2 and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        logs = logs.filter(time_in__date__gte=start_date, time_in__date__lte=end_date)
    elif date_count == 1 and specific_date:
        specific_date = datetime.strptime(specific_date, '%Y-%m-%d').date()
        logs = logs.filter(time_in__date=specific_date)

    data = [
        {
            'user': f"{log.user.first_name} {log.user.last_name}",
            'id_number': log.user.id_number,
            'email': log.user.email,
            'time_in': log.time_in.strftime('%Y-%m-%d %H:%M:%S') if log.time_in else 'Not In',
            'time_out': log.time_out.strftime('%Y-%m-%d %H:%M:%S') if log.time_out else 'Not Out'
        }
        for log in logs
    ]

    return JsonResponse(data, safe=False)

@login_required(login_url='login')
def GetFirstRow(request):
    total_books = Book.objects.filter(book_master__is_archived=False).count()
    print(total_books)

    total_borrowed = Book.objects.filter(status=4).count()
    print(total_borrowed)

    # Get total late transactions
    total_late = TransactionDetail.objects.filter(
        Q(expected_date_return__date__lt=datetime.now().date()) &  # Only compare dates
        Q(actual_date_return__isnull=True)  
    ).count()
    print(total_late)

    active_users = CustomUser.objects.filter(is_active=True).count()
    print(active_users)
    
    # Return the data as JSON
    return JsonResponse({
        'total_books': total_books,
        'total_borrowed': total_borrowed,
        'total_late': total_late,
        'active_users': active_users
    })

@login_required(login_url='login')
def GetSecondRow(request):
    if request.method == 'POST':
        time_range = request.POST.get('time_range')
        today = datetime.now()

        # Initialize empty lists for data
        labels = []@login_required(login_url='login')
def GetSecondRow(request):
    if request.method == 'POST':
        time_range = request.POST.get('time_range')
        today = datetime.now()

        # Initialize empty lists for data
        labels = []
        borrowed_data = []
        returned_data = []
        date_ranges = []
        year = today.year  # Current year

        try:
            for i in range(12):
                start_date = None
                end_date = None
                period_label = ""
                borrowed_count = 0
                returned_count = 0

                if time_range == 'daily':
                    start_date = today - timedelta(days=i)
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    period_label = start_date.strftime("%b %d")
                    labels.append(period_label)

                    borrowed_count = TransactionDetail.objects.filter(
                        date_borrowed__date=start_date.date(),
                        is_returned=False
                    ).count()
                    returned_count = TransactionDetail.objects.filter(
                        actual_date_return__date=start_date.date(),
                        is_returned=True
                    ).count()

                elif time_range == 'weekly':
                    week_start_date = today - timedelta(weeks=i, days=today.weekday())
                    week_end_date = week_start_date + timedelta(days=6)
                    start_date = week_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = week_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    period_label = f"Week {today.isocalendar()[1] - i}"
                    labels.append(period_label)

                    borrowed_count = TransactionDetail.objects.filter(
                        date_borrowed__date__gte=start_date.date(),
                        date_borrowed__date__lte=end_date.date(),
                        is_returned=False
                    ).count()
                    returned_count = TransactionDetail.objects.filter(
                        actual_date_return__date__gte=start_date.date(),
                        actual_date_return__date__lte=end_date.date(),
                        is_returned=True
                    ).count()

                elif time_range == 'monthly':
                    first_day_of_month = today.replace(day=1) - timedelta(days=i * 30)
                    last_day_of_month = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                    start_date = first_day_of_month.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = last_day_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)
                    period_label = first_day_of_month.strftime("%b %Y")
                    labels.append(period_label)

                    borrowed_count = TransactionDetail.objects.filter(
                        date_borrowed__date__gte=start_date.date(),
                        date_borrowed__date__lte=end_date.date(),
                        is_returned=False
                    ).count()
                    returned_count = TransactionDetail.objects.filter(
                        actual_date_return__date__gte=start_date.date(),
                        actual_date_return__date__lte=end_date.date(),
                        is_returned=True
                    ).count()

                borrowed_data.append(borrowed_count)
                returned_data.append(returned_count)
                date_ranges.append(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

            # Reverse the data to maintain chronological order
            labels.reverse()
            borrowed_data.reverse()
            returned_data.reverse()
            date_ranges.reverse()

            print(labels)
            print(borrowed_data)
            print(returned_data)
            print(date_ranges)

            return JsonResponse({
                'labels': labels,
                'borrowed_data': borrowed_data,
                'returned_data': returned_data,
                'date_ranges': date_ranges,
                'current_year': year
            })

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Something went wrong'}, status=500)

        
def GetThirdRow(request):
    try:
        # Fetch the top 5 main categories with their book counts
        categories = BookCategory.objects.filter(is_main=True) \
            .values('category__category_name') \
            .annotate(book_count=Count('book_master')) \
            .order_by('-book_count')[:5]
        
        print(categories)

        # Extract category names and counts
        category_names = [category['category__category_name'] for category in categories]
        book_counts = [category['book_count'] for category in categories]

        # Add 'Others' category, summing the remaining count of books
        remaining_books_count = BookCategory.objects.filter(is_main=True) \
            .exclude(category__category_name__in=category_names) \
            .aggregate(remaining_books=Count('book_master'))['remaining_books']

        category_names.append('Others')
        book_counts.append(remaining_books_count)

        return JsonResponse({
            'category_names': category_names,
            'book_counts': book_counts,
        })

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': 'Something went wrong'}, status=500)

def GetCurrentVisitors(request):
    try:
        # Fetch all logs where time_out is null (currently inside the library)
        logs = Logbook.objects.filter(time_out__isnull=True).select_related('user')

        # Prepare the data for the response
        log_data = []
        for log in logs:
            log_data.append({
                'full_name': f'{log.user.first_name} {log.user.last_name}',  # Concatenate first and last name
                'id_number': log.user.id_number,  # Use the id_number field for the ID column
                'username': log.user.username,  # Use the username field for the Username column
                'time_in': log.time_in.strftime('%Y-%m-%d %H:%M:%S')  # Format time_in
            })

        return JsonResponse(log_data, safe=False)

    except Exception as e:
        print(f"Error fetching logs: {e}")
        return JsonResponse({'error': 'An error occurred while fetching logs.'}, status=500)
    
@login_required(login_url='login')
def GetFourthRow(request):
    if request.method == 'POST':
        time_range = request.POST.get('time_range')
        today = datetime.now()

        # Initialize empty lists for data
        labels = []
        entered_data = []
        date_ranges = []

        try:
            for i in range(12):
                start_date = None
                end_date = None
                period_label = ""

                if time_range == 'daily':
                    start_date = today - timedelta(days=i)
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    period_label = start_date.strftime("%b %d")  # Format label as 'Feb 01'
                    labels.append(period_label)

                elif time_range == 'weekly':
                    week_start_date = today - timedelta(weeks=i, days=today.weekday())
                    week_end_date = week_start_date + timedelta(days=6)
                    start_date = week_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = week_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    period_label = f"Week {today.isocalendar()[1] - i}"
                    labels.append(period_label)

                elif time_range == 'monthly':
                    first_day_of_month = today.replace(day=1) - timedelta(days=i * 30)
                    last_day_of_month = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                    start_date = first_day_of_month.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = last_day_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)
                    period_label = first_day_of_month.strftime("%b %Y")  # Format label as 'Feb 2024'
                    labels.append(period_label)

                # Fetch the number of people who entered the library
                entered_count = Logbook.objects.filter(
                    time_in__range=[start_date, end_date],
                ).count()

                entered_data.append(entered_count)

                # Calculate date range for tooltip
                date_ranges.append(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

            # Reverse the data to maintain chronological order
            labels.reverse()
            entered_data.reverse()
            date_ranges.reverse()

            return JsonResponse({
                'labels': labels,
                'entered_data': entered_data,
                'date_ranges': date_ranges,  # Send date ranges for tooltips
            })

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Something went wrong'}, status=500)
        
@login_required(login_url='login')
def GetCategoryFilters(request):
    if request.method == 'GET':
        category_list = list(DimCategory.objects.values('category_id', 'category_name').distinct())
        return JsonResponse({'categories': category_list})
    
@login_required(login_url='login')
def BatchUpload(request):
    if request.method == 'POST':
        # Read the uploaded file
        excel_file = request.FILES.get('excel_file')

        try:
            # Load the Excel file into a DataFrame
            df = pd.read_excel(excel_file)

            # Check for headers
            expected_headers = [
                "Title", "ISBN", "Publisher", "Year", "Location", 
                "Author", "Category", "Copies"
            ]

            if list(df.columns) != expected_headers:
                return JsonResponse({"error": "Invalid headers"}, status=400)

            # Process each row
            for index, row in df.iterrows():
                title = row['Title']
                isbn = row['ISBN']
                publisher = row['Publisher']
                year = row['Year']
                location = row['Location']
                authors = row['Author'].split('/') if pd.notna(row['Author']) else []
                categories = row['Category'].split('/') if pd.notna(row['Category']) else []
                copies = int(row['Copies']) if pd.notna(row['Copies']) else 1  # Default to 1 copy if not specified

                print(title, isbn, publisher, year, location, authors, categories, copies)

                # Handle default values for summary and duration
                summary = "No summary available"  # Default summary
                duration = 3  # Default duration

                current_user = request.user

                # Check if the ISBN already exists
                existing_book = BookMaster.objects.filter(Q(isbn=isbn) & Q(is_archived=False)).first()

                book_master_reference = None

                if existing_book:
                    # If ISBN exists, create a new Book instance referencing it
                    for _ in range(copies):  # Save multiple copies
                        book = Book(
                            book_master=existing_book,
                            status_id=1,
                            qr_value='',  
                            qr_image='',
                            added_by=current_user  # Save the user who added the book
                        )
                        book.save()

                    book_master_reference = existing_book

                else:
                    # If ISBN doesn't exist, create a new BookMaster and Book instance
                    book_master = BookMaster(
                        title=title,
                        publisher=publisher,
                        year=year,
                        isbn=isbn,
                        late_fee=0,
                        location=location,
                        duration=duration,
                        image=None,  # No image field here, but you can add if needed
                        summary=summary,
                        soft_copy=None,  # No soft copy field here, but you can add if needed
                        added_by=current_user  # Save the user who added the book
                    )
                    book_master.save()

                    for _ in range(copies):  # Save multiple copies
                        book = Book(
                            book_master=book_master,
                            status_id=1,
                            qr_value='',  
                            qr_image='',
                            added_by=current_user  # Save the user who added the book
                        )
                        book.save()

                    book_master_reference = book_master

                    # Save authors
                    for author_name in authors:
                        if author_name:  # Ensure the author name is not empty
                            # Create and save the author relationship
                            book_author = BookAuthor(author=author_name, book_master=book_master_reference)
                            book_author.save()  # Save each author related to the book

                    # Save categories
                    is_main_assigned = False  # Track if the main category has been assigned
                    for category_name in categories:
                        if category_name:  # Ensure the category name is not empty
                            # Check if the category already exists in DimCategory
                            category, created = DimCategory.objects.get_or_create(
                                category_name=category_name,
                                defaults={'added_by': current_user}  # Only set added_by if it's a new category
                            )
                            # Set is_main=True for the first category
                            book_category = BookCategory(
                                book_master=book_master_reference, 
                                category=category,
                                is_main=not is_main_assigned  # Set is_main=True for the first iteration only
                            )
                            book_category.save()
                            is_main_assigned = True  # Update the flag after the first category is saved

                # After all books and copies are saved, generate and save QR code
                for book in Book.objects.filter(book_master=book_master_reference):
                    book.qr_value = f"QR-{book.book_id}-{title}-{year}-{isbn}"
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

            # Return a JSON response indicating success
            return JsonResponse({'isSuccess': 'true'})

        except DimCategory.DoesNotExist:
            return JsonResponse({'isSuccess': 'false', 'message': 'Category does not exist.'})

        except ValidationError as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'Validation error: ' + str(e)})

        except Exception as e:
            return JsonResponse({'isSuccess': 'false', 'message': 'An error occurred: ' + str(e)})

    # If not POST, return an error
    return JsonResponse({'isSuccess': 'false', 'message': 'Invalid request method.'})

@login_required  # Ensure the user is logged in
def ArchiveUser(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        # Check if the logged-in user is trying to delete their own account
        if str(user_id) == str(request.user.id):  # Compare the IDs as strings
            return JsonResponse({'status': 'error', 'message': 'You cannot delete the account you are currently using.'})

        try:
            # Find the user by id
            user = CustomUser.objects.get(id=user_id)
            
            # Toggle the is_active status
            user.is_active = not user.is_active 
            user.save()

            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'User archived successfully'})
        
        except CustomUser.DoesNotExist:
            # Return an error response if the user does not exist
            return JsonResponse({'status': 'error', 'message': 'User not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})