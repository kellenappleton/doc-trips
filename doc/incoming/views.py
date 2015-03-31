import io
import logging

from django import forms
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from vanilla import CreateView, UpdateView, DetailView, TemplateView, ListView, FormView
from braces.views import LoginRequiredMixin, FormMessagesMixin

from doc.incoming.models import Registration, IncomingStudent
from doc.incoming.forms import RegistrationForm, IncomingStudentsForm
from doc.core.models import Settings
from doc.db.models import TripsYear
from doc.db.views import TripsYearMixin
from doc.timetable.models import Timetable
from doc.permissions.views import (DatabaseReadPermissionRequired,
                                   DatabaseEditPermissionRequired)

""" 
Views for incoming students.

The first set of views are public facing and allow incoming 
students to register for trips. The second set handle manipulation of
registrations and trippees in the database.

"""

logger = logging.getLogger(__name__)


class IfRegistrationAvailable():
    """ Redirect if trippee registration is not currently available """

    def dispatch(self, request, *args, **kwargs):
        
        if not Timetable.objects.timetable().registration_available():
            return HttpResponseRedirect(reverse('incoming:registration_not_available'))
        return super(IfRegistrationAvailable, self).dispatch(request, *args, **kwargs)


class RegistrationNotAvailable(TemplateView):
    template_name = 'incoming/not_available.html'


class BaseRegistrationView(LoginRequiredMixin, IfRegistrationAvailable,
                           FormMessagesMixin):
    model = Registration
    template_name = 'incoming/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('incoming:portal')
    form_valid_message = "Your registration has been saved"
    form_invalid_message = "Uh oh, looks like there's an error somewhere in the form"


class Register(BaseRegistrationView, CreateView):
    """
    Register for trips 
    
    Redirects to the edit view if this incoming student 
    has already registered.
    """

    def dispatch(self, request, *args, **kwargs):
        """ Redirect to edit existing application """
        reg = Registration.objects.filter(
            trips_year=TripsYear.objects.current(),
            user=request.user).first()
        if reg: 
            return HttpResponseRedirect(reverse('incoming:edit_registration'))

        return super(Register, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form, **kwargs):
        """ 
        Add the registering user to the registration 

        The registration will be automagically matched with a 
        corresponding IncomingStudent model if it exists.
        """
        form.instance.trips_year = TripsYear.objects.current()
        form.instance.user = self.request.user
        return super(Register, self).form_valid(form, **kwargs)


class EditRegistration(BaseRegistrationView, UpdateView):
    """ Edit a trippee registration """

    def get_object(self):
        """ Get registration for user """        
        return get_object_or_404(
            self.model, user=self.request.user,
            trips_year=TripsYear.objects.current()
        )


class IncomingStudentPortal(LoginRequiredMixin, TemplateView):
    """
    Information for incoming students.

    Shows trip assignment, if available, and link to registration.
    """
    template_name = 'incoming/portal.html'

    def get_registration(self):
        """ Return current user's registration, or None if DNE """
        try:
            return Registration.objects.get(
                user=self.request.user,
                trips_year=TripsYear.objects.current()
            )
        except Registration.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        timetable = Timetable.objects.timetable()
        kwargs['registration'] = reg = self.get_registration()
        kwargs['trip_assignment'] = reg.get_trip_assignment() if reg else None
        kwargs['registration_available'] = timetable.registration_available()
        kwargs['registration_closes'] = timetable.trippee_registrations_close
        kwargs['after_deadline'] = timetable.trippee_registrations_close > timezone.now()
        kwargs['assignment_available'] = timetable.trippee_assignment_available
        kwargs['contact_url'] = Settings.objects.get().contact_url
        kwargs['trips_year'] = TripsYear.objects.current()
        return super(IncomingStudentPortal, self).get_context_data(**kwargs)


# ----- database internal views --------

class RegistrationIndexView(DatabaseReadPermissionRequired, 
                            TripsYearMixin, ListView):
    """ All trippee registrations """

    model = Registration
    template_name = 'incoming/registration_index.html'
    context_object_name = 'registrations'

    
class IncomingStudentIndexView(DatabaseReadPermissionRequired,
                               TripsYearMixin, ListView):
    """ All incoming students """

    model = IncomingStudent
    template_name = 'incoming/trippee_index.html'
    context_object_name = 'trippees'


class IncomingStudentDetailView(DatabaseReadPermissionRequired,
                                TripsYearMixin, DetailView):
    model = IncomingStudent
    template_name = 'incoming/trippee_detail.html'
    context_object_name = 'trippee'

    admin_fields = ['registration', 'trip_assignment', 
                    'decline_reason', 'notes']
    college_fields = ['name', 'netid', 'class_year', 'gender',
                      'ethnic_code', 'incoming_status', 'email', 
                      'blitz']


class IncomingStudentUpdateView(DatabaseEditPermissionRequired,
                                TripsYearMixin, UpdateView):
    model = IncomingStudent
    template_name = 'db/update.html'
    context_object_name = 'trippee'
    

class UploadIncomingStudentData(DatabaseEditPermissionRequired,
                                TripsYearMixin, FormView):
    """
    Accept an upload of CSV file of incoming students. 

    Parses the CSV file and adds the data to the database as
    CollegeInfo objects.

    TODO: parse or input the status of the incoming student 
    (eg first year, transfer, etc.)
    """

    form_class = IncomingStudentsForm
    template_name = 'incoming/upload_incoming_students.html'

    def form_valid(self, form):

        file = io.TextIOWrapper(form.files['csv_file'].file, 
                                encoding='utf-8', errors='replace')

        (created, ignored) = IncomingStudent.objects.create_from_csv_file(file, self.kwargs['trips_year'])

        msg = 'Created incoming students with NetIds %s' % created
        logger.info(msg)
        messages.info(self.request, msg)
        
        msg = 'Ignored existing incoming students with NetIds %s' % ignored
        logger.info(msg)
        messages.warning(self.request, msg)

        return super(UploadIncomingStudentData, self).form_valid(form)        

    def get_success_url(self):
        return self.request.path
        
 

    
