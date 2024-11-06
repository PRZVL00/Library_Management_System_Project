from django.conf import settings
from django.conf.urls.static import static
from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.Login, name="login"),
    path('verify-login/', views.VerifyLogin, name="verify-login"),
    path('Forgotpassword/', views.Forgotpassword, name="Forgotpassword"),
    path('ResetPassAuth/', views.ResetPassAuth, name="ResetPassAuth"),
    path('ResetPassword/', views.ResetPassword, name="ResetPassword"),
    path('ResetPassSucc/', views.ResetPassSucc, name="ResetPassSucc"),
    path('registration/', views.Registration, name="registration"),
    path('register-user/', views.RegisterUser, name="register-user"),
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('book-collection/', views.BookCollection, name="book-collection"),
    path('load-books/', views.LoadBooks, name='load-books'),
    path('borrow-return/', views.BorrowReturn, name="borrow-return"),
    path('account-management/', views.AccountManagement, name="account-management"),
    path('bag/', views.Bag, name="bag"),
    path('logbook/', views.Logbook, name="logbook"),
    path('profile/', views.Profile, name="profile"),
    path('book-registration/', views.BookRegistration, name="book-registration"),
    path('register-book', views.RegisterBook, name="register-book"),
    path('add-category', views.AddCategory, name="add-category"),
    path('get-categories', views.GetCategories, name="get-categories"),
    path('get-status', views.GetStatus, name="get-status"),
    path('book-management/', views.BookManagement, name="book-management"),
    path('get-books', views.GetBooks, name="get-books"),
    path('get-book-info/', views.GetBookInfo, name='get-book-info'),
    path('update-book', views.UpdateBook, name="update-book"),
    path('remove-book', views.RemoveBook, name="remove-book"),
    path('get-accounts', views.GetAccounts, name="get-accounts"),
    path('get-account-info/', views.GetAccountInfo, name='get-account-info'),
    path('update-account', views.UpdateAccount, name="update-account"),
    path('transaction-history/', views.TransactionHistory, name="transaction-history"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)