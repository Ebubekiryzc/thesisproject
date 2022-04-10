from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.account.models import User


@shared_task(name="send_activation_email_task")
def send_activation_email_task(context):
    user = User.objects.get(id=context["user"])
    
    task_context={
        "context": context,
        "user": user
    }

    email_subject = 'Hesabınızı Aktifleştirin'
    email_body = render_to_string('account/activate.html', task_context)
    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_HOST_USER, to=[user.email])
    email.send()
