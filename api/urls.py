from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('<path:origin_form>', views.m2mrequest, name='absolute-m2mrequest'),
    #path('instances/', views.primitive, name='instances'),
]
