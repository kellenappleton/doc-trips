
from django.conf.urls import patterns, url

from trip.views import *

trip_urlpatterns = patterns('', 
    url(r'^$', ScheduledTripListView.as_view(), name='trip_index'),
    url(r'^create$', ScheduledTripCreateView.as_view(), name='trip_create'),                   
    url(r'^(?P<pk>[0-9]+)/update', ScheduledTripUpdateView.as_view(), name='trip_update'),
    url(r'^(?P<pk>[0-9]+)/delete', ScheduledTripDeleteView.as_view(), name='trip_delete'),
)

template_urlpatterns = patterns('',
    url(r'^$', TripTemplateListView.as_view(), name='template_index'),
    url(r'^create$', TripTemplateCreateView.as_view(), name='template_create'),
    url(r'^(?P<pk>[0-9]+)/update', TripTemplateUpdateView.as_view(), name='template_update'),
    url(r'^(?P<pk>[0-9]+)/delete', TripTemplateDeleteView.as_view(), name='template_delete'),                                
)                                

triptype_urlpatterns = patterns('',
    url(r'^$', TripTypeListView.as_view(), name='triptype_index'),
    url(r'^create$', TripTypeCreateView.as_view(), name='triptype_create'),                             
    url(r'^(?P<pk>[0-9]+)/update', TripTypeUpdateView.as_view(), name='triptype_update'),                             
    url(r'^(?P<pk>[0-9]+)/delete', TripTypeDeleteView.as_view(), name='triptype_delete'),
)                                

campsite_urlpatterns = CampsiteViews.get_urls()

section_urlpatterns = SectionViews.get_urls()
