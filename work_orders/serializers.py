from django.utils import timezone
from rest_framework import serializers
from .models import WorkOrder, DoorEvent


class WorkOrderSerializer(serializers.ModelSerializer):
    applicant_username = serializers.ReadOnlyField(source='applicant.username')
    class Meta:
        model = WorkOrder
        fields = ['id', 'date', 'duration', 'activity', 'company', 'capacity','pin','is_active','applicant_username']
        read_only_fields = ['is_active','pin','applicant_username']
        
    def validate_date(self, value):
        print(timezone.now())
        print(value)
        if value < timezone.now():
            raise serializers.ValidationError('La fecha no puede ser anterior.')
        return value
    
    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError('La capacidad debe ser al menos 1.')
        return value
        
class WorkOrderApprovalSerializer(serializers.Serializer):
    pass  # No need for additional fields for this case

class WorkOrderPinSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = ['pin','date','activity','duration']
        read_only_fields=['date','activity','duration']
        

class PinUpdateSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=10)

class DoorEventCreateSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=10)
    is_entry = serializers.BooleanField()

    def validate_pin(self,value):
        if not WorkOrder.check_pin_workorders(value):
            raise serializers.ValidationError('El pin proporcionado no es valido.')
        return value

    
    def create(self, validated_data):
        # Extraer el pin e is_entry del validated_data
        pin = validated_data.pop('pin')
        is_entry = validated_data.pop('is_entry')
        # Encontrar la WorkOrder activa con el pin proporcionado
        work_order = WorkOrder.objects.get(pin=pin, is_active=True)
        # Crear el DoorEvent asociado a la WorkOrder
        door_event = DoorEvent(is_entry=is_entry, work_order_pin_access=work_order)
        print('!!')
        door_event.save()
        print('pasa el save')

        return door_event