
from datetime import datetime
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase as TripsTestCase, WebTestCase
from doc.applications.models import (LeaderSupplement as LeaderApplication, 
                                     CrooSupplement, 
                                     GeneralApplication, LeaderApplicationGrade, 
                                     ApplicationInformation)
from doc.timetable.models import Timetable
from doc.trips.models import Section


def open_application(trips_year):

    t = Timetable.objects.timetable()
    t.applications_open += timedelta(-1)
    t.applications_close += timedelta(1)
    t.save()


class ApplicationAccessTestCase(WebTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_anonymous_user_does_not_crash_application(self):
        
        self.app.get(reverse('applications:apply'))

    def test_application_not_visible_if_not_available(self):
        
        # close leader applications:
        t = Timetable.objects.timetable()
        t.applications_open += timedelta(-2)
        t.applications_close += timedelta(-1)
        t.save()

        self.mock_user()
        response = self.app.get(reverse('applications:apply'), user=self.user)
        self.assertTemplateUsed('applications/not_available.html')


class ApplicationFormTestCase(WebTestCase):

    csrf_checks = False
    
    def setUp(self):
        self.init_current_trips_year()
        self.init_previous_trips_year()

    def test_file_uploads_dont_overwrite_each_other(self):
        # TODO / scrap
        
        self.mock_user()
        open_application(self.current_trips_year)

        res = self.app.get(reverse('applications:apply'), user=self.user)
        # print(res)
        #  print(res.form)
                             

    def test_available_sections_in_leader_form_are_for_current_trips_year(self):

        prev_section = mommy.make(Section, trips_year=self.previous_trips_year)
        curr_section = mommy.make(Section, trips_year=self.current_trips_year)

        open_application(self.current_trips_year)
        self.mock_user()

        response = self.app.get(reverse('applications:apply'), user=self.user)
        form = response.context['leader_form']
        self.assertEquals(list(form.fields['available_sections'].queryset),
                          list(Section.objects.filter(trips_year=self.current_trips_year)))
        self.assertEquals(list(form.fields['preferred_sections'].queryset),
                          list(Section.objects.filter(trips_year=self.current_trips_year)))


class ApplicationManagerTestCase(TripsTestCase):

    """ 
    Tested against the LeaderApplication model only; 
    there should be no difference with the CrooApplciation model.
    """
    
    def setUp(self):
        self.init_current_trips_year()
        self.init_previous_trips_year()
        self.mock_user()

    def make_application(self, status=GeneralApplication.PENDING, trips_year=None):

        if trips_year is None:
            trips_year = self.current_trips_year

        application = mommy.make(GeneralApplication, 
                                 status=status,
                                 trips_year=trips_year)
        leader_app = mommy.make(LeaderApplication, 
                                application=application, 
                                trips_year=trips_year)
        croo_app = mommy.make(CrooSupplement, 
                              application=application, 
                              trips_year=trips_year)
        
        return application

    def test_with_no_grades(self):
        
        application = self.make_application()

        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(application.leader_supplement, next)


    def test_graded_ungraded_priority(self):
        
        app1 = self.make_application()
        grade = mommy.make(LeaderApplicationGrade, trips_year=self.current_trips_year,
                           application=app1.leader_supplement)
        app2 = self.make_application()

        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(next, app2.leader_supplement, 'app with no grades should have priority')


    def test_user_can_only_grade_application_once(self):

        application = self.make_application()
        grade = mommy.make(LeaderApplicationGrade, grader=self.user,
                           application=application.leader_supplement,
                           trips_year=self.trips_year)

        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'no applications should be available')


    def test_only_grade_pending_applications(self):
        
        application = self.make_application(status=GeneralApplication.LEADER)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'only PENDING apps should be gradable')


    def test_can_only_grade_applications_for_the_current_trips_year(self):
        
        application = self.make_application(trips_year=self.previous_trips_year)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'should not be able to grade apps from previous years')

    
    def test_correct_number_of_grades(self):

        application = self.make_application()

        for i in range(LeaderApplication.NUMBER_OF_GRADES):

            # works because we are not actually grading with self.user
            next = LeaderApplication.objects.next_to_grade(self.user)
            self.assertEquals(next, application.leader_supplement)
            
            grade = mommy.make(LeaderApplicationGrade, trips_year=self.trips_year,
                               application=application.leader_supplement)
           
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'can only grade NUMBER_OF_GRADES times')
        


                           
    
        
        

        

    