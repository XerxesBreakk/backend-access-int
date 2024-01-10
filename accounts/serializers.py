from djoser.serializers import UserSerializer
from .models import UserAccount
from djoser.conf import settings
from djoser.compat import get_user_email, get_user_email_field_name

class UserCustomSerializer(UserSerializer):
    class Meta:
        model = UserAccount
        fields = tuple(UserAccount.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'is_active','is_staff','last_name'
        )
        read_only_fields = ['is_active','is_staff','last_name']

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(UserAccount)
        instance.email_changed = False
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.email_changed = True
                instance.save(update_fields=["is_active"])
        return super().update(instance, validated_data)