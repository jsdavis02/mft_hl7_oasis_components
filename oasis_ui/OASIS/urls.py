from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('audits/', views.analyst_audit_list_view, name='analyst-audit-list-view'),
    path('audits/detail/<int:pk>/', views.analyst_audit_detail_view, name='analyst-audit-detail-view'),
    path('audits/download/<int:pk>/', views.analyst_download_audit_file, name='analyst-audit-download'),
    path('endpoints/', views.analyst_endpoint_list_view, name='analyst-endpoint-list-view'),
    path('endpoint/detail/<int:pk>/', views.analyst_endpoint_detail_view, name='analyst-endpoint-detail-view'),
    path('intrequest/add/', views.analyst_int_request_view, name='analyst-int-request-view'),
    path('accounts/sign_up/', views.sign_up, name="sign-up"),
    path('password_change/', views.change_password, name='change-password'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
