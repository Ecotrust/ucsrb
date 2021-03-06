from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.flatpages import views as flat_views

from . import views

urlpatterns = [
    ### App URLs
    url(r'^home/?$', views.home),
    url(r'^$', views.home),
    url(r'^app/?$', views.app, name="app"),
    url(r'^help/$', flat_views.flatpage, {'url': '/help/'}, name="help"),
    url(r'^methods/$', flat_views.flatpage, {'url': '/methods/'}, name='methods'),
    url(r'^thankyou/$', flat_views.flatpage, {'url': '/thankyou/'}, name='thankyou'),

    ### API urls
    url(r'^get_veg_unit_by_bbox', views.get_veg_unit_by_bbox),
    # url(r'^get_segment_by_bbox', views.get_segment_by_bbox), # suspected ununsed RDH 7/31/2018
    # url(r'^get_segment_by_id', views.get_segment_by_id),
    # url(r'^segment/(?P<id>[\w_]+)', views.get_segment_by_id), # suspected unused RDH 7/31/2018
    url(r'^pourpoint/(?P<id>[\w_]+)', views.get_pourpoint_by_id),
    # url(r'^filter_results', views.filter_results), # suspected ununsed RDH 7/31/2018
    url(r'^get_results_by_scenario_id', views.get_results_by_scenario_id),
    url(r'^get_downstream_pour_points', views.get_downstream_pour_points),
    url(r'^get_hydro_results_by_pour_point_id', views.get_hydro_results_by_pour_point_id),
    url(r'^get_results_by_state', views.get_results_by_state),
    url(r'^get_focus_area_at', views.get_focus_area_at),
    url(r'^get_focus_area', views.get_focus_area),
    url(r'^get_basin', views.get_basin),
    url(r'^save_drawing', views.save_drawing),
    url(r'^upload_treatment_shapefile/', views.upload_treatment_shapefile, name='shp_upload'),

    ### Filter/Scenarios Work
    url(r'get_scenarios/(?P<scenario_model_name>[\w_]+)/$', views.get_scenarios),
    url(r'get_scenarios$', views.get_scenarios),
    url(r'get_scenarios/$', views.get_scenarios),
    url(r'get_planningunits$', views.get_planningunits),

    url(r'^get_user_scenario_list/$', views.get_user_scenario_list),

    ### end API urls
    url(r'^', views.index, name='index'),
]
