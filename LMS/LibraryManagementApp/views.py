from django.shortcuts import render

# Create your views here.
def Login(request):
    return render(request, 'LogInPage/login.html', {})

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
