"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path

from authorities.views import AuthorityDetailView, AuthorityListView
from inquests.views import InquestDetailView, InquestListView

urlpatterns = [
    path('inquests/', InquestListView.as_view(), name='inquest-list'),
    path('inquests/<int:pk>/', InquestDetailView.as_view(), name='inquest-detail'),
    path('authorities/', AuthorityListView.as_view(), name='authority-list'),
    path('authorities/<int:pk>/', AuthorityDetailView.as_view(), name='authority-detail'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
]
