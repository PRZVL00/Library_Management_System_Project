from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.Login, name="login"),
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('book-collection/', views.BookCollection, name="book-collection"),
    path('borrow-return/', views.BorrowReturn, name="borrow-return"),
    path('account-management/', views.AccountManagement, name="account-management"),
]
