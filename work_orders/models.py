from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from accounts.models import UserAccount


class WorkOrder(models.Model):
    date = models.DateTimeField()
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    duration = models.DurationField()
    activity= models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    company = models.CharField(max_length=255)
    applicant = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='applicant')
    approver = models.ForeignKey(UserAccount, on_delete=models.CASCADE,null=True, blank=True, related_name='approver')
    pin = models.CharField(max_length=10,blank=True)
    
    def __str__(self):
        return f'Orden de Trabajo {self.id} - {self.applicant.username}'

    def clean_date(self):
        # Validación personalizada para la fecha
        if self.date < timezone.now():
            raise ValidationError('La fecha no puede ser anterior a la fecha actual.')

    def clean_approver(self):
        # Validación personalizada para aprobador
        if not self.approver.is_staff:
            raise ValidationError('El usuario debe ser administrador.')
        
    def is_overlap(self,check_date):
        return (self.date <= check_date  <= (self.date + self.duration))
    
    def check_pin(self,pin):
        if not self.is_active:
            return False
        return self.pin == pin
    
    @staticmethod
    def get_active_workorders_overlap(check_date):
        active_workorders = WorkOrder.objects.filter(is_active=True)
        overlapping_workorders = [workorder for workorder in active_workorders if workorder.is_overlap(check_date)]
        return overlapping_workorders
    
    @staticmethod
    def is_active_workorders_overlap(check_date):
        active_workorders = WorkOrder.objects.filter(is_active=True)
        overlapping_workorders = [workorder for workorder in active_workorders if workorder.is_overlap(check_date)]
        return len(overlapping_workorders)
    
     
    @staticmethod
    def check_pin_workorders(pin):
        active_workorders = WorkOrder.objects.filter(is_active=True)
        for wo in active_workorders:
            if wo.check_pin(pin):
                return True
        return False

        
class DoorEvent(models.Model):
    date=models.DateTimeField(auto_now_add=True)
    is_entry=models.BooleanField(default=True)
    work_order_pin_access=models.ForeignKey(WorkOrder,null=True,on_delete=models.CASCADE,related_name='door_events')

    def __str__(self):
        action='Entrada'
        if self.is_entry:
            action='Salida'
        return f'{action} - {self.date}'

