from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class CustomUser(AbstractUser):
    # Additional fields from your diagram
    id_number = models.CharField(max_length=255, unique=True)
    cellphone_number = models.CharField(max_length=20)
    qr_value = models.CharField(max_length=255)
    qr_image = models.ImageField(upload_to='qr_images/', null=True, blank=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)

    def __str__(self):
        return self.username


class DimStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status_name
    
@receiver(post_migrate)
def create_default_statuses(sender, **kwargs):
    if sender.name == 'LibraryManagementApp':
        default_statuses = ["Available","Under Maintenance", "Reserved", "Borrowed", ]
        for status_name in default_statuses:
            DimStatus.objects.get_or_create(status_name=status_name)

class DimCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name

class BookMaster(models.Model):
    book_master_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    publisher = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255, unique=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    image = models.ImageField(upload_to='book_images/')
    summary = models.TextField()
    location = models.CharField(max_length=255)
    soft_copy = models.FileField(upload_to='soft_copies/', null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_master = models.ForeignKey(BookMaster, on_delete=models.CASCADE)
    status = models.ForeignKey(DimStatus, on_delete=models.CASCADE)
    qr_value = models.CharField(max_length=255)
    qr_image = models.ImageField(upload_to='book_qr/')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.book_id


class BookCategory(models.Model):
    book_category_id = models.AutoField(primary_key=True)
    book_master = models.ForeignKey(BookMaster, on_delete=models.CASCADE)
    category = models.ForeignKey(DimCategory, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.book.title} - {self.category.category_name}'
    
class BookAuthor(models.Model):
    book_author_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=255)
    book_master = models.ForeignKey(BookMaster, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.book.title} - {self.author}'
    
class Reservatiop(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_reserved = models.DateTimeField()
    expiration_date = models.DateTimeField()
    is_processed = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction Detail {self.transaction_detail_id}'


class TransactionMaster(models.Model):
    transaction_master_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    approver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='approver')
    transaction_date = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction {self.transaction_master_id}'


class TransactionDetail(models.Model):
    transaction_detail_id = models.AutoField(primary_key=True)
    transaction_master = models.ForeignKey(TransactionMaster, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_borrowed = models.DateTimeField()
    expected_date_return = models.DateTimeField()
    actual_date_return = models.DateTimeField(null=True, blank=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    return_id = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction Detail {self.transaction_detail_id}'


class Logbook(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time_in = models.DateTimeField()
    time_out = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Log {self.log_id} for {self.user.username}'


class ForgetPassword(models.Model):
    forget_password_id = models.AutoField(primary_key=True)
    forget_password_code = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_generated = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Password reset for {self.user.username}'
