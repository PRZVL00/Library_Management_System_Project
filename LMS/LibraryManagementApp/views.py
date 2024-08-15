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