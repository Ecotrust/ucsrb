from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    ### App URLs
    url(r'^home/?', views.home),
    url(r'^app/?', views.app, name="app"),
    url(r'^sign_in/$', views.sign_in, name='sign_in'),
    url(r'^sign_out/$', views.sign_out, name='sign_out'),
    url(r'^sign_up/$', views.register, name='sign_up'),

    ### API urls
    url(r'^get_veg_unit_by_bbox', views.get_veg_unit_by_bbox),
    url(r'^get_segment_by_bbox', views.get_segment_by_bbox),
    # url(r'^get_segment_by_id', views.get_segment_by_id),
    url(r'^segment/(?P<id>[\w_]+)', views.get_segment_by_id),
    url(r'^pourpoint/(?P<id>[\w_]+)', views.get_pourpoint_by_id),
    url(r'^filter_results', views.filter_results),
    url(r'^get_results_by_scenario_id', views.get_results_by_scenario_id),
    url(r'^get_results_by_state', views.get_results_by_state),

    ### Filter/Scenarios Work
    url(r'get_scenarios$', views.get_scenarios),
    url(r'get_planningunits$', views.get_planningunits),

    ### end API urls
    url(r'^', views.index, name='index'),
]
