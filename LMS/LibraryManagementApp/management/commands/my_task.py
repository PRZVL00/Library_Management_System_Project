from django.core.management.base import BaseCommand
from datetime import datetime
from LibraryManagementApp.views import *

class Command(BaseCommand):
    help = 'Send library reports and notifications'

    def handle(self, *args, **kwargs):
        # Call the function to send the library report
        send_library_report()
        self.stdout.write(self.style.SUCCESS('Library report email sent successfully!'))
