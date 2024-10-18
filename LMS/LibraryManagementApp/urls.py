from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.Login, name="login"),
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('book-collection/', views.BookCollection, name="book-collection"),
    path('load-books/', views.LoadBooks, name='load-books'),
    path('borrow-return/', views.BorrowReturn, name="borrow-return"),
    path('account-management/', views.AccountManagement, name="account-management"),
    path('bag/', views.Bag, name="bag"),
    path('logbook/', views.Logbook, name="logbook"),
    path('profile/', views.Profile, name="profile"),
    path('book-registration/', views.BookRegistration, name="book-registration"),
    path('book-management/', views.BookManagement, name="book-management"),
    path('get-books', views.GetBooks, name="get-books"),
    path('get-book-info/', views.GetBookInfo, name='get-book-info'),
    path('transaction-history/', views.TransactionHistory, name="transaction-history"),


]
