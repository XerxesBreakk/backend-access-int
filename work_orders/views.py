import random
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .models import WorkOrder, DoorEvent
from .serializers import WorkOrderSerializer, WorkOrderApprovalSerializer, WorkOrderPinSerializer, PinUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import UserAccount
from rest_framework.permissions import AllowAny
import pytz

class WorkOrderListCreateView(ListCreateAPIView):
    serializer_class=WorkOrderSerializer
    permission_classes=[IsAuthenticated]
    
    
    def get_queryset(self):
        user = self.request.user
        is_active_param = self.request.query_params.get('is_active', None)
        if is_active_param is not None:
            # Convierte el valor de 'is_active' a un booleano
            is_active_param = is_active_param.lower() == 'true'
            if user.is_staff:
                return WorkOrder.objects.all().filter(is_active=is_active_param)
            
        if user.is_staff:
            return WorkOrder.objects.all()
        return WorkOrder.objects.filter(applicant=user)
    
    def perform_create(self, serializer):
        # Establecemos el solicitante automáticamente basándonos en el usuario autenticado
        serializer.save(applicant=self.request.user, is_active=False)

    
class WorkOrderApprovalView(UpdateAPIView):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderApprovalSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Validate and update the serializer data (even though there are no fields)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Check if the user is an administrator
        if not request.user.is_staff:
            return Response(
                {'detail': 'No tienes permisos para aprobar ordenes de trabajo.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Set is_active to True, set approver to the authenticated user, and generate a random 5-digit PIN
        instance.is_active = True
        instance.approver = request.user
        instance.pin = str(random.randint(10000, 99999))
        instance.save()
        
        # Send emails to the applicant and administrators
        self.send_approval_emails(instance)

        return Response({'detail': 'WorkOrder approved successfully.'})
    
    
    def send_approval_emails(self, work_order):
        # Send email to the applicant
        subject_applicant = 'Orden de trabajo aprobada'
        message_applicant = f'Tu orden de trabajo (ID: {work_order.id}) ha sido aprobada para la fecha {work_order.date} y la compañia {work_order.company}.'
        send_mail(subject_applicant, message_applicant, settings.DEFAULT_FROM_EMAIL, [work_order.applicant.email])

        # Send email to administrators
        subject_admin = 'Nueva orden de trabajo aprobada'
        message_admin = f'Se aprobo una orden de trabajo (ID: {work_order.id}).\n\nDETALLES:\n{work_order}'
        admin_emails = UserAccount.objects.filter(is_staff=True).values_list('email', flat=True)
        send_mail(subject_admin, message_admin, settings.DEFAULT_FROM_EMAIL, admin_emails)

class VerifyAndUpdatePinView(UpdateAPIView):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderPinSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        # Obtener el código del payload
        code = request.data.get('pin', None)

        if not code:
            return Response({'error': 'El código no ha sido proporcionado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la orden de trabajo por el código
        work_order = get_object_or_404(WorkOrder, pin=code)

        # Verificar si la fecha actual está dentro del rango de tiempo
        current_datetime = datetime.now().replace(tzinfo=pytz.UTC)
        start_datetime = work_order.date
        end_datetime = start_datetime + work_order.duration

        if not (start_datetime <= current_datetime <= end_datetime):
            return Response({'error': 'No se encuentra en el rango de horario para ser autorizado el ingreso.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generar un nuevo pin y actualizar la orden de trabajo
        new_pin = str(random.randint(10000, 99999))
        work_order.pin = new_pin #TODO revisar que el pin no este repetido en otra OT y que no es el mismo que el anterior
        work_order.save()

        # Serializar y devolver la orden de trabajo actualizada
        serializer = self.get_serializer(work_order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PinUpdateView(APIView):
    serializer_class = PinUpdateSerializer
    permission_classes=[AllowAny] #TODO Restringir para que solo los equipos puedan enviar esto
    #Agregar un throttle para que solo puedan enviarse 10 claves por minuto

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            pin = serializer.validated_data['pin']
            workorder = self.get_valid_workorder(pin)

            if workorder:
                # Cambiar el pin por uno nuevo
                new_pin = str(random.randint(10000, 99999))  # Asume que tienes una función para generar un nuevo pin
                workorder.pin = new_pin
                workorder.save()

                # Crear DoorEvent
                DoorEvent.objects.create(is_entry=True, work_order_pin_access=workorder)

                return Response({'detail': 'Pin actualizado y DoorEvent creado.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Pin o WorkOrder no válidos.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Datos no válidos.'}, status=status.HTTP_400_BAD_REQUEST)

    def get_valid_workorder(self, pin):
        # Buscar una WorkOrder activa con el pin proporcionado
        try:
            workorder = WorkOrder.objects.get(is_active=True, pin=pin)
            return workorder
        except WorkOrder.DoesNotExist:
            return None
