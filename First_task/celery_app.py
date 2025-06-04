from celery import Celery
import os

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(
    "first_task",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

@celery.task
def send_email_task(email: str):
    import time
    time.sleep(5) # имитация задачи 
    print(f"Email sent to {email}")
    return f"Email sent to {email}"
