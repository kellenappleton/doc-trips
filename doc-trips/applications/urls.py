
from django.conf.urls import patterns, url

from db.urlhelpers import DB_REGEX
from applications.views import NewApplication, ContinueApplication, SetupApplication

urlpatterns = patterns(
    '',
    url(r'^apply/$', NewApplication.as_view(), name='apply'),
    url(r'^continue/$', ContinueApplication.as_view(), name='continue'),
    url(r'^setup/$', SetupApplication.as_view(), name='setup'),
)
