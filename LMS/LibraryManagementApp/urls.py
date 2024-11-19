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
    path('reserve-book', views.ReserveBook, name="reserve-book"),
    path('logbook/', views.LogbookPage, name="logbook"),
    path('profile/', views.Profile, name="profile"),
    path('book-registration/', views.BookRegistration, name="book-registration"),
    path('register-book', views.RegisterBook, name="register-book"),
    path('check-ISBN', views.CheckISBN, name="check-ISBN"),
    path('add-category', views.AddCategory, name="add-category"),
    path('get-categories', views.GetCategories, name="get-categories"),
    path('get-status', views.GetStatus, name="get-status"),
    path('book-management/', views.BookManagement, name="book-management"),
    path('get-books', views.GetBooks, name="get-books"),
    path('get-bookmaster-books', views.GetBookMasterBooks, name="get-bookmaster-books"),
    path('get-book-info/', views.GetBookInfo, name='get-book-info'),
    path('get-accounts', views.GetAccounts, name="get-accounts"),
    path('update-status', views.UpdateStatus, name="update-status"),
    path('update-book', views.UpdateBook, name="update-book"),
    path('remove-book', views.RemoveBook, name="remove-book"),
    path('get-accounts', views.GetAccounts, name="get-accounts"),
    path('get-account-info/', views.GetAccountInfo, name='get-account-info'),
    path('update-account', views.UpdateAccount, name="update-account"),
    path('transaction-history/', views.TransactionHistory, name="transaction-history"),
    path('update-bag-number', views.UpdateBagNumber, name="update-bag-number"),
    path('get-reserved', views.GetReserved, name="get-reserved"),
    path('cancel-reservation/', views.CancelReservation, name='cancel-reservation'),
    path('load-profile/', views.LoadProfile, name='load-profile'),
    path('borrow_selected_books', views.BorrowSelectedBooks, name="borrow_selected_books"),
    path('return_selected_books', views.ReturnSelectedBooks, name="return_selected_books"),
    path('get-transaction', views.GetTransaction, name="get-transaction"),
    path('get-transaction-detail', views.GetTransactionDetail, name="get-transaction-detail"),
    path('get-user-profile', views.GetUserProfile, name="get-user-profile"),
    path('get-user-transaction', views.GetUserTransaction, name="get-user-transaction"),
    path('in-out/', views.InOut, name="in-out"),
    path('create-log', views.CreateLog, name="create-log"),
    path('get-log', views.GetLog, name="get-log"),
    path('get-first-row', views.GetFirstRow, name="get-first-row"),
    path('get-second-row', views.GetSecondRow, name="get-second-row"),
    path('get-third-row/', views.GetThirdRow, name='get-third-row'),
    path('get-current-visitors/', views.GetCurrentVisitors, name='get-current-visitors'),  
    path('get-fourth-row/', views.GetFourthRow, name='get-fourth-row'),
    path('get-category-filters', views.GetCategoryFilters, name='get-category-filters'),
    path('batch-upload', views.BatchUpload, name='batch-upload'),
    path('get-to-borrow', views.GetToBorrow, name='get-to-borrow'),
    path('get-to-return', views.GetToReturn, name='get-to-return'),
    path('add-book-copy/', views.AddBookCopy, name='add-book-copy'),
    path('archive-user/', views.ArchiveUser, name='archive-user'),



    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)