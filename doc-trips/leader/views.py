
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.db.models import Count
from django.forms import ModelForm

from vanilla import ListView, CreateView, DetailView, UpdateView, FormView, RedirectView
from django_easyfilters import FilterSet

from leader.models import LeaderApplication, LeaderGrade

from db.views import *

logger = logging.getLogger(__name__)


class LeaderApplicationListView(DatabaseListView):
    model = LeaderApplication
    context_object_name = 'leaderapplications'
    template_name = 'leader/leaderapplication_index.html'

class LeaderApplicationUpdateView(DatabaseUpdateView):
    model = LeaderApplication


class LeaderApply(LoginRequiredMixin, CreateView):
    model = LeaderApplication
    
    template_name = 'leader/application_form.html'
    fields = '__all__'

    def form_valid(self, form):
        """ Attach creating user to Application. """
        form.instance.user = self.request.user
        return super(CreateLeaderApplication, self).form_valid(form)


class EditLeaderApplication(LoginRequiredMixin, UpdateView):
    model = LeaderApplication
    template_name = 'leader/application_form.html'
    fields = '__all__'


# TODO: needs to be grader permission based
# TODO: convert to class view
@login_required
def redirect_to_next_gradable_application(request):

    application = LeaderApplication.objects.next_to_grade(request.user)
    # TODO: use template
    if not application:
        return HttpResponse('<h3>No applications left to grade </h3>')
    return redirect('leader:grade', pk=application.pk)
    

class LeaderGradeForm(ModelForm):
    class Meta:
        model = LeaderGrade
        fields = ['grade', 'comment', 'hard_skills', 'soft_skills']


# TODO: restrict this to those with grader permissions
class GradeApplicationView(DetailView, FormView):

    """ Grade a LeaderApplication object. 

    The DetailView encapsulates the LeaderApplication, 
    the FormView the grade form. 
    """

    model = LeaderApplication
    template_name = 'leader/grade.html'
    context_object_name = 'leader_application'

    form_class = LeaderGradeForm
    """ Must be a lazy - this is called before the urlconf is loaded.
    See http://stackoverflow.com/a/22903110/3818777 """
    success_url = reverse_lazy('leader:grade_random')

    def get_context_data(self, **kwargs):
        """ Get context data to render in template.

        Because The DetailView is first in the MRO inheritance tree,
        The super call retrives the LeaderaApplication object (saved as context_object_name).
        Then we manually add the form instance.
        """
        context = super(GradeApplicationView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    
    def form_valid(self, form):
        """ Attach grader and application to the grade, save grade to database.
        
        Redirects to success_url. 
        """
        grade = form.save(commit=False)
        grade.grader = self.request.user
        grade.leader_application = self.get_object()
        grade.save()

        return super(GradeApplicationView, self).form_valid(form)






