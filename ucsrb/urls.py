from django.conf.urls import url

from . import views

urlpatterns = [
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
    url(r'^home/?', views.home),
    url(r'^app/?', views.app, name="app"),
    url(r'^account/', views.account, name='login'),
]
