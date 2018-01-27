"""marineplanner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
### INSERT ADDITIONAL IMPORTS HERE ###
import accounts.urls
### END PROJECT URL IMPORTS ###
from ucsrb.views import demo, get_planningunits, get_filter_count, get_filter_results

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    ### INSERT PROJECT URL INCLUDES HERE ###
    url(r'^features/', include('features.urls')),
    url(r'^manipulators/', include('manipulators.urls')),
    url('^account/auth/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^account/', include('accounts.urls', namespace="account")),
    url(r'^data_manager/', include('data_manager.urls')),
    url(r'^visualize/', include('visualize.urls')),
    url(r'^scenario/demo$', demo),
    url(r'^scenario/get_planningunits$', get_planningunits),
    url(r'^scenario/get_filter_count$', get_filter_count),
    url(r'^scenario/get_filter_results$', get_filter_results),
    url(r'^scenario/demo$', demo),
    url(r'^scenario/', include('scenarios.urls')),
    # url(r'^filter/', include('filter.urls')),
    url(r'^ucsrb/', include('ucsrb.urls')),
    url(r'^drawing/', include('drawing.urls')),
    url(r'^api/', include('ucsrb.urls')),
    url(r'', include('ucsrb.urls')),
    ### END PROJECT URL INCLUDES ###
    # url(r'^visualize/', include('visualize.urls')),
    # url(r'^account/auth/', include('social.apps.django_app.urls', namespace='social')),
    # url(r'^account/', include('accounts.urls', namespace="account")),
    # url(r'^data_manager/', include('data_manager.urls', namespace="data_manager")),
]
