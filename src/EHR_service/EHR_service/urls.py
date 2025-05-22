"""
URL configuration for EHR_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title='EHR Service API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/ehr/', include('EHR.urls')),  # Add EHR app URLs
    path('api-auth/', include('rest_framework.urls')),  # Add DRF auth URLs
    path('docs/', include_docs_urls(title='EHR Service API')),  # Add API documentation
    path('schema/', schema_view),  # Add schema view
]
