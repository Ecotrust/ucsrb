from django.conf.urls import url

from . import views

urlpatterns = [
    ### API urls
    url(r'^get_segment_by_bbox', views.get_segment_by_bbox),


    ### end API urls
    url(r'^', views.index, name='index'),
]
