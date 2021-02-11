from django.urls import path, re_path, register_converter
from . import views


urlpatterns = [
    #path('', views.index, name='index'),
    #path('<path:origin_form>', views.m2mrequest, name='absolute-m2mrequest'),
    re_path(r'(?P<cseid>\w+)\/?(?P<resourceid>[A-Za-z0-9\?\=\&]+)?\/?(?P<attrib>[\w+\?\=\&]+)?$', views.m2mrequest),
]
