from django.urls import path
from .views import WorkOrderListCreateView, WorkOrderApprovalView,VerifyAndUpdatePinView,PinUpdateView

urlpatterns = [
    path('', WorkOrderListCreateView.as_view(), name='crear_listar_ot'),
    path('approve/<int:pk>/', WorkOrderApprovalView.as_view(), name='aprobar_orden'),
    path('verify-and-update-pin/', VerifyAndUpdatePinView.as_view(), name='verify-and-update-pin'),
    path('pin-consume/',PinUpdateView.as_view(),name='pin_update'),
]