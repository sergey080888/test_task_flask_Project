import smtplib
import os
from celery import Celery


celery_app = Celery(broker="redis://db-redis:6379/0", backend="redis://db-redis:6379/1")


@celery_app.task
def send_mail():
    EMAIL = os.getenv('EMAIL')
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = os.getenv('SMTP_PORT')
    SMTP_LOGIN = os.getenv('SMTP_LOGIN')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    server = smtplib.SMTP_SSL(SMTP_HOST, int(SMTP_PORT))
    server.login(EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_LOGIN, EMAIL, 'test')
    server.quit()
    return
