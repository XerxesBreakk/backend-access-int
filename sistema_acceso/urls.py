from django.urls import path,include
#from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('auth/',include('djoser.urls')),
    path('work-order/',include('work_orders.urls')),
    path('auth/',include('djoser.urls.jwt')),
    #path("docs/",include_docs_urls(title="sistema acceso")),
]

#urlpatterns += [re_path(r'^.*',TemplateView.as_view(template_name='index.html'))]