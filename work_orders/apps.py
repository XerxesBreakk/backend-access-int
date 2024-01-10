from django.apps import AppConfig


class WorkOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'work_orders'

    def ready(self):
        import work_orders.signals