from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import WorkOrder
from accounts.models import UserAccount

@receiver(post_save, sender=WorkOrder) 
def send_email_on_work_order_creation(sender, instance, created, **kwargs):
    if created:
        subject = 'Nueva orden de trabajo'
        message = f'Una nueva orden de trabajo (ID: {instance.id}) ha sido creada.\n\nDETALLES:\nFecha: {instance.date}\nEmpresa: {instance.company}\nDuración del trabajo: {instance.duration}\nActividad a realizar: {instance.activity}'
        from_email = settings.DEFAULT_FROM_EMAIL

        # Get all users with is_staff=True
        admin_emails = UserAccount.objects.filter(is_staff=True).values_list('email', flat=True)

        send_mail(subject, message, from_email, admin_emails)