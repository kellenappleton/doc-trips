import datetime

from django.forms.models import model_to_dict
from django.urls import reverse
from model_mommy import mommy

from fyt.safety.models import Incident
from fyt.test import FytTestCase
from fyt.trips.models import Trip


class IncidentViewsTestCase(FytTestCase):

    csrf_checks = False

    def test_safety_leads_can_access_incident_report(self):
        trips_year = self.init_trips_year()
        url = reverse('core:safety:list', kwargs={'trips_year': trips_year})
        self.app.get(url, user=self.make_user(), status=403)
        self.app.get(url, user=self.make_director())  # OK
        self.app.get(url, user=self.make_safety_lead())  # OK

    def test_new_incident_adds_trip_year(self):
        trips_year = self.init_trips_year()
        url = reverse('core:safety:create', kwargs={'trips_year': trips_year})
        data = model_to_dict(
            mommy.prepare(
                Incident,
                trip=mommy.make(Trip, trips_year=trips_year),
                when=datetime.datetime.now(),
            )
        )
        self.app.post(url, params=data, user=self.make_director())
        self.assertEqual(Incident.objects.get().trips_year, trips_year)
