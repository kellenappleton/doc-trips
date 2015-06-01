from collections import OrderedDict

from vanilla import TemplateView
from django.core.exceptions import ImproperlyConfigured
from braces.views import SetHeadlineMixin

from doc.db.views import TripsYearMixin
from doc.permissions.views import DatabaseReadPermissionRequired
from doc.applications.models import GeneralApplication
from doc.trips.models import TripType, Section


class BaseEmailList(DatabaseReadPermissionRequired, TripsYearMixin,
                    SetHeadlineMixin, TemplateView):
    """ 
    Base class for email list view
    """
    template_name = 'emails/emails.html'

    def get_email_lists(self):
        """ 
        Should return an iterable of duples in the form
        (email_list_name, list_of_emails)
        """
        raise ImproperlyConfigured()

    def get_context_data(self, **kwargs):
        context = super(BaseEmailList, self).get_context_data(**kwargs)
        context['email_lists'] = OrderedDict(self.get_email_lists())
        return context


def emails(qs):
    """ 
    Return a list of applicant emails from GenApp qs 
    """
    values = qs.values('applicant__email')
    return list(map(lambda x: x['applicant__email'], values))


class Applicants(BaseEmailList):

    headline = "Applicant Emails"

    def get_email_lists(self):

        trips_year = self.get_trips_year()
        qs = GeneralApplication.objects.filter(trips_year=trips_year)

        email_list = [
            ('all applicants', emails(qs)),
            ('complete leader application', emails(
                GeneralApplication.objects.leader_applications(trips_year))),
            ('complete croo application', emails(
                GeneralApplication.objects.croo_applications(trips_year))),
            ('leaders', emails(qs.filter(
                status=GeneralApplication.LEADER))),
            ('leader waitlist', emails(
                qs.filter(status=GeneralApplication.LEADER_WAITLIST))),
            ('croo members', emails(
                qs.filter(status=GeneralApplication.CROO))),
            ('rejected applicants', emails(
                qs.filter(status=GeneralApplication.REJECTED))),
        ]
   
        return email_list


class LeadersByTripType(BaseEmailList):

    headline = "Leader Emails by TripType"

    def get_email_lists(self):

        trips_year = self.get_trips_year()
        leaders = GeneralApplication.objects.filter(
            trips_year=trips_year, status=GeneralApplication.LEADER)
        email_list = []
        triptypes = TripType.objects.filter(trips_year=trips_year)
        for triptype in triptypes:
            email_list.append(
                ('%s leaders' % triptype,
                 emails(leaders.filter(assigned_trip__template__triptype=triptype))))
        return email_list


class LeadersBySection(BaseEmailList):

    headline = "Leader Emails by Section"

    def get_email_lists(self):
        trips_year = self.get_trips_year()
        leaders = GeneralApplication.objects.filter(
            trips_year=trips_year, status=GeneralApplication.LEADER)
        email_list = []

        sections = Section.objects.filter(trips_year=trips_year)
        for section in sections:
            email_list.append(
                ('%s leaders' % section,
                 emails(leaders.filter(assigned_trip__section=section)))
            )
        return email_list
