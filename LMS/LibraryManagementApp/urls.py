from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.Login, name="login"),
    path('registration/', views.Registration, name="registration"),
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('book-collection/', views.BookCollection, name="book-collection"),
    path('borrow-return/', views.BorrowReturn, name="borrow-return"),
    path('account-management/', views.AccountManagement, name="account-management"),
    path('bag/', views.Bag, name="bag"),
    path('logbook/', views.Logbook, name="logbook"),
    path('profile/', views.Profile, name="profile"),
    path('book-registration/', views.BookRegistration, name="book-registration"),
    path('book-management/', views.BookManagement, name="book-management"),
    path('transaction-history/', views.TransactionHistory, name="transaction-history"),


]
