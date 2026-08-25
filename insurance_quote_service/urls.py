"""
URL configuration for insurance_quote_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app.views import CustomerView, QuoteView, PolicyListView, PolicyDetailView, \
    PolicyHistoryView

urlpatterns = [
    path('admin/', admin.site.urls),

    path("api/v1/create_customer/", CustomerView.as_view(), name="customer"),
    path("api/v1/customer/", CustomerView.as_view(), name="customer-search"),

    path("api/v1/quote/", QuoteView.as_view(), name="quote"),
    path("api/v1/policies/", PolicyListView.as_view(), name="policy-for-user"),
    path("api/v1/policies/<uuid:pk>/", PolicyDetailView.as_view(), name="policy-details"),

    path("api/v1/policies/<uuid:policy_id>/history/", PolicyHistoryView.as_view(), name="policy-history"),
]
