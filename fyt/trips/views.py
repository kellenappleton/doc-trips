from collections import OrderedDict, defaultdict
from statistics import mean

from braces.views import FormValidMessageMixin, SetHeadlineMixin
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.utils.safestring import mark_safe
from vanilla import FormView, UpdateView

from .forms import (
    FoodboxFormsetHelper,
    LeaderAssignmentForm,
    SectionForm,
    TrippeeAssignmentForm,
)
from .models import (
    NUM_BAGELS_REGULAR,
    NUM_BAGELS_SUPPLEMENT,
    Campsite,
    Document,
    Section,
    Trip,
    TripTemplate,
    TripType,
)

from fyt.applications.models import (
    LeaderSectionChoice,
    LeaderSupplement,
    LeaderTripTypeChoice,
    Volunteer,
)
from fyt.db.views import (
    BaseUpdateView,
    DatabaseCreateView,
    DatabaseDeleteView,
    DatabaseDetailView,
    DatabaseListView,
    DatabaseTemplateView,
    DatabaseUpdateView,
    TripsYearMixin,
)
from fyt.incoming.models import (
    AVAILABLE,
    FIRST_CHOICE,
    PREFER,
    IncomingStudent,
    RegistrationSectionChoice,
    RegistrationTripTypeChoice,
)
from fyt.permissions.views import (
    ApplicationEditPermissionRequired,
    DatabaseEditPermissionRequired,
    TripInfoEditPermissionRequired,
)
from fyt.transport.models import ExternalBus, InternalBus
from fyt.utils.cache import cache_as
from fyt.utils.forms import crispify
from fyt.utils.views import PopulateMixin


class _SectionMixin():
    """
    Utility mixin for CBVs which have a section_pk url kwarg.
    """
    @cache_as('_section')
    def get_section(self):
        return Section.objects.get(pk=self.kwargs['section_pk'])

    def get_context_data(self, **kwargs):
        kwargs['section'] = self.get_section()
        return super().get_context_data(**kwargs)


class _TripMixin():
    """
    Mixin to pull a trip object from a trip_pk url kwarg
    """
    @cache_as('_trip')
    def get_trip(self):
        return Trip.objects.get(pk=self.kwargs['trip_pk'])

    def get_context_data(self, **kwargs):
        kwargs['trip'] = self.get_trip()
        return super().get_context_data(**kwargs)


class _TripTemplateMixin():
    """
    Mixin to pull a TripTemplate object from a triptemplate_pk url kwarg
    """
    @cache_as('_triptemplate')
    def get_triptemplate(self):
        return TripTemplate.objects.get(pk=self.kwargs['triptemplate_pk'])

    def get_context_data(self, **kwargs):
        kwargs['triptemplate'] = self.get_triptemplate()
        return super().get_context_data(**kwargs)


class TripList(DatabaseTemplateView):
    template_name = 'trips/trip_index.html'

    def extra_context(self):
        return {'matrix': Trip.objects.matrix(self.kwargs['trips_year'])}


class TripUpdate(DatabaseUpdateView):
    model = Trip
    fields = [
        'dropoff_route',
        'pickup_route',
        'return_route',
        'notes'
    ]

    def get_headline(self):
        return mark_safe(
            "Edit %s <small> Trip </small>" % self.object
        )


class TripDetail(DatabaseDetailView):
    model = Trip
    template_name = 'trips/trip_detail.html'

    fields = [
        'section',
        'template',
        'leaders',
        'trippees',
        'notes',
        ('dropoff route', 'get_dropoff_route'),
        ('dropoff bus', 'get_dropoff_bus'),
        ('dropoff time', 'get_dropoff_time'),
        ('pickup route', 'get_pickup_route'),
        ('pickup bus', 'get_pickup_bus'),
        ('pickup time', 'get_pickup_time'),
        ('return route', 'get_return_route')
    ]

    triptemplate_fields = [
        'triptype',
        'max_trippees',
        'swimtest_required',
        'desc_intro',
        'dropoff_stop',
        'desc_day1',
        'campsite1',
        'desc_day2',
        'campsite2',
        'desc_day3',
        'pickup_stop',
        'desc_conc',
        'revisions']


class TripCreate(PopulateMixin, DatabaseCreateView):
    model = Trip
    fields = ['section', 'template']


class TripDelete(DatabaseDeleteView):
    model = Trip
    success_url_pattern = 'db:trip:index'


class TripTemplateList(DatabaseListView):
    model = TripTemplate
    context_object_name = 'templates'
    template_name = 'trips/template_index.html'

    def get_queryset(self):
        qs = super(TripTemplateList, self).get_queryset()
        return qs.select_related(
            'triptype',
            'campsite1',
            'campsite2',
            'dropoff_stop',
            'pickup_stop'
        )


class TripTemplateCreate(DatabaseCreateView):
    model = TripTemplate


class TripTemplateDetail(DatabaseDetailView):
    model = TripTemplate
    template_name = 'trips/triptemplate_detail.html'
    fields = [
        'name',
        'description_summary',
        'triptype',
        ('files', 'documents'),
        'max_trippees',
        'swimtest_required',
        'dropoff_stop',
        'campsite1',
        'campsite2',
        'pickup_stop',
        'return_route',
        'desc_intro',
        'desc_day1',
        'desc_day2',
        'desc_day3',
        'desc_conc',
        'revisions',
    ]


class TripTemplateUpdate(TripInfoEditPermissionRequired, BaseUpdateView):
    model = TripTemplate


class TripTemplateDelete(DatabaseDeleteView):
    model = TripTemplate
    success_url_pattern = 'db:triptemplate:index'


class UploadTripTemplateDocument(_TripTemplateMixin, DatabaseCreateView):
    """
    Upload a supplementary file and attach it to a TripTemplate.
    """
    model = Document
    fields = ['name', 'file']

    def get_headline(self):
        return mark_safe(
            "Upload File <small>%s</small>" % self.get_triptemplate()
        )

    def form_valid(self, form):
        form.instance.template = self.get_triptemplate()
        return super(UploadTripTemplateDocument, self).form_valid(form)

    def get_success_url(self):
        return self.get_triptemplate().detail_url()


class TripTemplateDocumentList(DatabaseDetailView):
    model = TripTemplate
    template_name = 'trips/document_list.html'


class TripTemplateDocumentDelete(_TripTemplateMixin, DatabaseDeleteView):
    model = Document

    def get_success_url(self):
        return reverse('db:triptemplate:document_list',
                       kwargs=self.get_triptemplate().obj_kwargs())


class TripTypeList(DatabaseListView):
    model = TripType
    context_object_name = 'triptypes'
    template_name = 'trips/triptype_index.html'


class TripTypeCreate(DatabaseCreateView):
    model = TripType


class TripTypeDetail(DatabaseDetailView):
    model = TripType
    fields = [
        'name',
        'hidden',
        'trippee_description',
        'leader_description',
        'packing_list',
        'half_kickin',
        'gets_supplemental',
    ]


class TripTypeUpdate(TripInfoEditPermissionRequired, BaseUpdateView):
    model = TripType
    fields = [
        'name',
        'hidden',
        'leader_description',
        'trippee_description',
        'packing_list',
        'half_kickin',
        'gets_supplemental',
    ]


class TripTypeDelete(DatabaseDeleteView):
    model = TripType
    success_url_pattern = 'db:triptype:index'


class CampsiteMatrix(DatabaseTemplateView):
    model = Campsite
    template_name = 'trips/campsite_index.html'

    def extra_context(self):
        return {
            'matrix': Campsite.objects.matrix(self.kwargs['trips_year'])
        }


class CampsiteCreate(DatabaseCreateView):
    model = Campsite


class CampsiteDetail(DatabaseDetailView):
    model = Campsite
    fields = [
        'name',
        'capacity',
        'directions',
        'water_source',
        'shelter',
        'bear_bag',
        'bugout',
        'secret'
    ]


class CampsiteUpdate(DatabaseUpdateView):
    model = Campsite


class CampsiteDelete(DatabaseDeleteView):
    model = Campsite
    success_url_pattern = 'db:campsite:index'


class SectionList(DatabaseListView):
    model = Section
    context_object_name = 'sections'
    template_name = 'trips/section_index.html'


class SectionCreate(DatabaseCreateView):
    model = Section
    form_class = SectionForm
    template_name = 'trips/section_create.html'


class SectionDetail(DatabaseDetailView):
    model = Section
    fields = [
        'name',
        'leaders_arrive',
        'is_local',
        'is_exchange',
        'is_transfer',
        'is_international',
        'is_native',
        'is_fysep'
    ]


class SectionUpdate(DatabaseUpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'trips/section_update.html'


class SectionDelete(DatabaseDeleteView):
    model = Section
    success_url_pattern = 'db:section:index'


class LeaderTrippeeIndexView(DatabaseListView):
    """
    Show all Trips with leaders and trippees.

    Links to pages to assign leaders and trippees.
    """
    model = Trip
    template_name = 'trips/assignments.html'
    context_object_name = 'trips'

    def get_queryset(self):
        return (
            super(LeaderTrippeeIndexView, self).get_queryset()
            .prefetch_related('leaders', 'leaders__applicant', 'trippees')
        )


class AssignTrippee(_TripMixin, DatabaseListView):
    """
    Assign trippees to a trip.

    The trip's pk is passed in the url arg.

    Each trippee passed to the context has the following properties:

    * ``assignment_url`` - the url to assign trippee to this trip
    * ``triptype_pref`` - 'first choice', 'prefer', or 'available'
    * ``section_pref`` - 'prefer' or 'available'
    * ``bus_available`` - ``True`` if trippee requested a bus and it is
      scheduled this section, otherwise ``False``

    Because of our database structure, preferences are not easy to
    compute efficiently. See below...
    """
    model = IncomingStudent
    template_name = 'trips/assign_trippee.html'
    context_object_name = 'available_trippees'

    def get_queryset(self):
        """
        All trippees who prefer, are available, or chose this
        trip as their first choice.

        Only pull in required fields because a whole application
        queryset is big enough to slow down performance.
        """
        return (
            self.model.objects.available_for_trip(
                self.get_trip()
            ).select_related(
                'trip_assignment',
                'trip_assignment__template',
                'trip_assignment__section',
                'registration',
                'registration__bus_stop_round_trip',
                'registration__bus_stop_to_hanover',
                'registration__bus_stop_from_hanover'
            )
        )

    # TODO: refactor this with the new M2M setup
    def get_context_data(self, **kwargs):
        """
        In order to compute each trippee's triptype or section
        preference,

        Initially I tried using ``prefetch_related`` to load all
        ``preferred_triptypes``, ``available_triptypes``, etc.
        However, this requires the database to load each trip, in the
        worst case, on *every* tripppee, up to ``O(n)`` times for the
        entire, queryset. Multiply this by the total number of trips,
        and there goes performance.

        Perhaps a SQL guru can figure out a clever way to compute this
        in-database, but I could not.

        The solution: use the ``through`` objects created by ``M2M`` fields.
        We iterate through these objects for the sections and triptypes in
        question and save each trippee's preference in a dict.
        This technique is ``O(1)`` for queries and ``O(n)`` for in-memory
        processing, which is quite acceptable. See http://goo.gl/QbK99D
        """
        context = super(AssignTrippee, self).get_context_data(**kwargs)
        context['trip'] = trip = self.get_trip()
        section = trip.section
        triptype = trip.template.triptype
        trips_year = self.kwargs['trips_year']

        triptype_pref = {
            pref.registration_id: pref.preference
            for pref in RegistrationTripTypeChoice.objects.filter(
                triptype=triptype,
                preference__in=[AVAILABLE, PREFER, FIRST_CHOICE]
            )
        }
        section_pref = {
            pref.registration_id: pref.preference
            for pref in RegistrationSectionChoice.objects.filter(
                section=section,
                preference__in=[AVAILABLE, PREFER]
            )
        }

        # all external buses for this section
        buses = ExternalBus.objects.filter(
            trips_year=trips_year, section=section)
        # all ids of routes running on this section
        route_ids = [bus.route_id for bus in buses]

        for trippee in self.object_list:
            reg = trippee.registration
            url = reverse('db:assign_trippee_to_trip', kwargs={
                'trips_year': trips_year,
                'trippee_pk': trippee.pk
            })
            trippee.assignment_url = '%s?assign_to=%s' % (url, trip.pk)
            trippee.triptype_pref = triptype_pref[reg.id]
            trippee.section_pref = section_pref[reg.id]

            bus_requests = (
                reg.bus_stop_round_trip,
                reg.bus_stop_to_hanover,
                reg.bus_stop_from_hanover
            )
            if not any(bus_requests):  # don't want a bus
                trippee.bus_available = False
            else:
                trippee.bus_available = all([
                    bus.route_id in route_ids for bus in bus_requests if bus
                ])
        return context


class AssignTrippeeToTrip(FormValidMessageMixin, DatabaseUpdateView):

    model = IncomingStudent
    lookup_url_kwarg = 'trippee_pk'
    template_name = 'db/update.html'
    form_class = TrippeeAssignmentForm

    def get(self, request, *args, **kwargs):
        """
        Pull the 'assign_to' trip from GET qs
        """
        data = {'trip_assignment': request.GET['assign_to']}
        form = self.get_form(data=data)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, **kwargs):
        return self.get_form_class()(self.get_trips_year(), **kwargs)

    def get_form_valid_message(self):
        """ Flash success message """
        return '{} assigned to {}'.format(
            self.object, self.object.trip_assignment
        )

    def get_headline(self):
        self.object = self.get_object()
        return 'Assign {} to trip'.format(self.object)

    def get_success_url(self):
        """ Override DatabaseUpdateView default """
        return reverse('db:leader_index',
                       kwargs={'trips_year': self.get_trips_year()})


class AssignLeader(_TripMixin, DatabaseListView):
    """
    Assign a leader to a trip.

    The trip's pk is passed in the url kwargs.

    The template is passed a list of tuples of the form
    ``(LeaderApplication, assign_url, triptype_pref, section_pref)``

    * ``assign_url`` will be None if the leader is already assigned to a trip.
    * ``triptype_pref`` - 'prefer' or 'available'
    * ``section_pref`` - 'prefer' or 'available'
    """
    model = Volunteer
    template_name = 'trips/assign_leader.html'
    context_object_name = 'leader_applications'

    def get_queryset(self):
        qs = (
            self.model.objects.prospective_leaders_for_trip(self.get_trip())
            .select_related(
                'applicant',
                'assigned_trip',
                'assigned_trip__template',
                'assigned_trip__section'
            ).prefetch_related(
                'leader_supplement__grades'
            )
        )

        # For some reason, annotating grades using Avg adds an
        # expensive GROUP BY clause to the query, killing the site.
        # See https://code.djangoproject.com/ticket/17144.
        # Does this need to be reopened?
        # TODO: check with 1.8
        # This is a hackish workaround to explicitly compute the
        # average for all applications with reasonable performance:
        for app in qs:
            if app.leader_supplement.grades.exists():
                app.avg_grade = mean(
                    map(lambda g: g.grade, app.leader_supplement.grades.all())
                )
            else:
                app.avg_grade = None
        # return 0 in case someone has no grades
        return sorted(qs, key=lambda x: x.avg_grade or 0, reverse=True)

    def get_assign_url(self, leader, trip):
        """
        Return the url used to assign leader to trip
        """
        url = reverse('db:assign_leader_to_trip', kwargs={
            'trips_year': self.kwargs['trips_year'],
            'leader_pk': leader.pk
        })
        return '%s?assigned_trip=%s' % (url, trip.pk)

    def get_context_data(self, **kwargs):
        """
        Compute whether each leader prefers or is available for this
        trip's section and triptype. We use the through fields of the
        ``M2M`` models because ``prefetch_related`` pulls in *all* related
        objects--and all fields of the related objects--which is a huge
        query and kills performance.

        See :class:`~fyt.trips.views.AssignTrippee` for a similar situation
        and more explanation.
        """
        context = super(AssignLeader, self).get_context_data(**kwargs)
        context['trip'] = trip = self.get_trip()

        triptype_pref = {
            pref.application.application_id: pref.preference
            for pref in LeaderTripTypeChoice.objects.filter(
                triptype=trip.template.triptype,
                preference__in=[PREFER, AVAILABLE]
            ).select_related('application')
        }

        section_pref = {
            pref.application.application_id: pref.preference
            for pref in LeaderSectionChoice.objects.filter(
                section=trip.section,
                preference__in=[PREFER, AVAILABLE]
            ).select_related('application')
        }

        def process_leader(leader):
            return (
                leader,
                self.get_assign_url(leader, trip),
                triptype_pref[leader.id],
                section_pref[leader.id]
            )

        leaders = [process_leader(x) for x in self.object_list]
        context[self.context_object_name] = leaders
        return context


class AssignLeaderToTrip(ApplicationEditPermissionRequired, PopulateMixin,
                         SetHeadlineMixin, FormValidMessageMixin,
                         TripsYearMixin, UpdateView):
    model = Volunteer
    lookup_url_kwarg = 'leader_pk'
    template_name = 'db/update.html'

    def get_form(self, **kwargs):
        form = LeaderAssignmentForm(self.kwargs['trips_year'], **kwargs)
        label = 'Assign to %s' % (
            Trip.objects.get(pk=self.request.GET['assigned_trip'])
        )
        return crispify(form, label)

    def get_form_valid_message(self):
        return '{} assigned to lead {}'.format(
            self.object.applicant, self.object.assigned_trip
        )

    def get_headline(self):
        self.object = self.get_object()
        return 'Assign {} to trip'.format(
            self.object.applicant
        )

    def get_success_url(self):
        return reverse('db:leader_index', kwargs={
            'trips_year': self.kwargs['trips_year']
        })


class RemoveAssignedTrip(ApplicationEditPermissionRequired,
                         FormValidMessageMixin, TripsYearMixin, UpdateView):
    """
    Remove a leader's assigned trip
    """
    model = Volunteer
    lookup_url_kwarg = 'leader_pk'
    template_name = 'trips/remove_leader_assignment.html'

    def get_form(self, **kwargs):
        # save old assignment so we can show it after deletion
        self._assigned_trip = kwargs['instance'].assigned_trip
        form = LeaderAssignmentForm(
            self.kwargs['trips_year'], initial={'assigned_trip': None}, **kwargs
        )
        return crispify(form, 'Remove', 'btn-danger')

    def get_form_valid_message(self):
        return 'Leader {} removed from Trip {}'.format(
            self.object.applicant, self._assigned_trip
        )

    def get_success_url(self):
        return self.object.detail_url()


class TrippeeLeaderCounts(DatabaseTemplateView):
    """
    Shows a matrix of the number of tripees and leaders for all trips
    """
    template_name = 'trips/trippee_leader_counts.html'

    def extra_context(self):
        return {
            'matrix': Trip.objects.matrix(self.kwargs['trips_year'])
        }


class FoodboxCounts(DatabaseListView):

    model = Trip
    template_name = 'trips/foodboxes.html'
    context_object_name = 'trips'

    def get_queryset(self):
        return Trip.objects.filter(
            trips_year=self.kwargs['trips_year']
        ).select_related(
            'template__triptype'
        )

    def extra_context(self):
        qs = self.object_list
        return {
            'full': len(qs),
            'half': len(list(filter(lambda x: x.half_foodbox, qs))),
            'supp': len(list(filter(lambda x: x.supp_foodbox, qs))),
            'bagels': sum(map(lambda x: x.bagels, qs)),
            'bagel_ratio': NUM_BAGELS_REGULAR,
            'supp_bagel_ratio': NUM_BAGELS_SUPPLEMENT,
        }


class FoodboxRules(DatabaseEditPermissionRequired, TripsYearMixin, FormView):

    template_name = 'trips/foodbox_rules.html'

    def get_queryset(self):
        return TripType.objects.filter(trips_year=self.kwargs['trips_year'])

    def get_form(self, **kwargs):
        FoodRulesFormset = modelformset_factory(
            TripType, fields=['name', 'half_kickin', 'gets_supplemental'],
            extra=0
        )
        formset = FoodRulesFormset(queryset=self.get_queryset(), **kwargs)
        formset.helper = FoodboxFormsetHelper()
        formset.helper.form_class = 'form-inline'
        formset.helper.add_input(Submit('submit', 'Save'))
        return formset

    def form_valid(self, formset):
        formset.save()
        return super(FoodboxRules, self).form_valid(formset)

    def get_success_url(self):
        return self.request.path


class LeaderPacket(DatabaseDetailView):
    """
    All information that leader's need: schedule, directions,
    medical info, etc.
    """
    model = Trip
    template_name = 'trips/leader_packet.html'


class PacketsForSection(_SectionMixin, DatabaseListView):
    """
    All leader packets for a section.
    """
    model = Trip
    template_name = 'trips/section_packet.html'
    context_object_name = 'trips'

    def get_queryset(self):
        return super(PacketsForSection, self).get_queryset().filter(
            section=self.get_section()
        ).select_related(
            'template__campsite1',
            'template__campsite2',
            'template__dropoff_stop',
            'template__pickup_stop'
        ).prefetch_related(
            'leaders',
            'leaders__applicant',
            'trippees',
            'trippees__registration'
        )


class MedicalInfoForSection(PacketsForSection):
    """
    Packets for croos, by section.

    Contains leader and trippee med information.
    """
    template_name = 'trips/medical_packet.html'


class TrippeeChecklist(_SectionMixin, DatabaseListView):
    """
    Checklist of a trippees for a section.
    """
    model = IncomingStudent
    template_name = 'trips/person_checklist.html'
    header_text = 'Trippee'

    def get_queryset(self):
        qs = super(TrippeeChecklist, self).get_queryset()
        return qs.filter(trip_assignment__section=self.get_section())


class LeaderChecklist(_SectionMixin, DatabaseListView):
    """
    All leaders for a section.
    """
    model = Volunteer
    template_name = 'trips/person_checklist.html'
    header_text = 'Leader'

    def get_queryset(self):
        qs = super(LeaderChecklist, self).get_queryset()
        return qs.filter(assigned_trip__section=self.get_section())


class Checklists(DatabaseTemplateView):
    """
    Central list of all checklists"
    """
    template_name = 'trips/checklists.html'

    def extra_context(self):

        trips_year = self.kwargs['trips_year']

        dates = Section.dates.leader_dates(trips_year)
        d = OrderedDict([date, []] for date in dates)

        for sxn in Section.objects.filter(trips_year=trips_year):
            kwargs = {
                'trips_year': trips_year,
                'section_pk': sxn.pk
            }
            d[sxn.leaders_arrive].append((
                'Section %s Leader Checkin' % sxn.name,
                reverse('db:checklists:leaders', kwargs=kwargs)))

            d[sxn.trippees_arrive].append((
                'Section %s Trippee Checkin' % sxn.name,
                reverse('db:checklists:trippees', kwargs=kwargs)))

            d[sxn.trippees_arrive].append((
                'Section %s Leader Packets' % sxn.name,
                reverse('db:packets:section', kwargs=kwargs)))

            d[sxn.trippees_arrive].append((
                'Section %s Medical Information' % sxn.name,
                reverse('db:packets:medical', kwargs=kwargs)))

        buses = InternalBus.objects.filter(trips_year=trips_year)
        for date in set(map(lambda x: x.date, buses)):
            d[date].append((
                'Internal Bus Directions for %s' % date.strftime('%m/%d'),
                reverse('db:internalbus:packet_for_date', kwargs={
                    'trips_year': trips_year, 'date': date
                })
            ))

        buses = ExternalBus.objects.filter(trips_year=trips_year)
        bus_dict = defaultdict(set)
        for bus in buses:
            bus_dict[bus.date_to_hanover].add(bus)
            bus_dict[bus.date_from_hanover].add(bus)

        for date, buses in bus_dict.items():
            for bus in buses:
                d[date].append((
                    '%s Directions for %s' % (bus.route, date.strftime('%m/%d')),
                    reverse('db:externalbus:packet_for_date_and_route', kwargs={
                        'trips_year': trips_year,
                        'date': date,
                        'route_pk': bus.route.pk})))

                d[date].append((
                    '%s Riders Spreadsheet' % bus.route,
                    reverse('db:reports:bus_riders', kwargs={
                        'trips_year': trips_year,
                        'bus_pk': bus.pk})))

        return {'date_dict': d}
