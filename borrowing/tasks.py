from celery import shared_task
from django.utils import timezone
from borrowing.models import Borrowing
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage"
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")


@shared_task
def notify_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Overdue borrowing alert! 📚\n"
                f"Book: {borrowing.book.title}\n"
                f"Author: {borrowing.book.author}\n"
                f"Borrowed by: {borrowing.user.email}\n"
                f"Expected return date: {borrowing.expected_return_date}\n"
            )
            send_telegram_message(message)
    else:
        send_telegram_message.delay("No borrowings overdue today!")


@shared_task
def send_telegram_message(text):
    requests.post(TELEGRAM_API_URL, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
