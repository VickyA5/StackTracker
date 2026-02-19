from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    WelcomeView,
    RegisterView,
    DashboardView,
    SupplierListView,
    SupplierCreateView,
    SupplierUploadView,
    ComparisonResultView,
    ComparisonDownloadView,
    SupplierDeleteView,
    SupplierSettingsView,
)

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('home/', DashboardView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/upload/', SupplierUploadView.as_view(), name='supplier_upload'),
    path('suppliers/<int:pk>/comparison/', ComparisonResultView.as_view(), name='supplier_comparison'),
    path('suppliers/<int:pk>/comparison/download/', ComparisonDownloadView.as_view(), name='supplier_comparison_download'),
    path('suppliers/<int:pk>/settings/', SupplierSettingsView.as_view(), name='supplier_settings'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),
]
