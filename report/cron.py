from .models import Fournisseur
from .views import sendEmail
from django.utils import timezone
from calendar import monthrange
from datetime import timedelta

def send_weekly_email():
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    for supplier in Fournisseur.objects.filter(is_tracked=True, send_email=True):
        sendEmail(supplier, today, last_week)
        print('Weekely Email sent', today)

def send_monthly_email():
    today = timezone.now().date()
    last_day_of_month = monthrange(today.year, today.month)[1]
    if today.day != last_day_of_month:
        return 
    
    start_date = today.replace(day=1)
    end_date = today

    for supplier in Fournisseur.objects.filter(is_tracked=True, send_email=True):
        sendEmail(supplier, start_date, end_date)
        print('Monthly Email sent', today)
