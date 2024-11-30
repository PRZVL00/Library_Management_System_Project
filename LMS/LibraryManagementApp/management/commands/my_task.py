from django.core.management.base import BaseCommand
import os
import django
from LibraryManagementApp.views import send_library_report

class Command(BaseCommand):
    help = 'Send library reports and notifications'

    def handle(self, *args, **kwargs):
        # Set up Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
        django.setup()

        # Call the function to send the library report
        send_library_report()
        self.stdout.write(self.style.SUCCESS('Library report email sent successfully!'))
