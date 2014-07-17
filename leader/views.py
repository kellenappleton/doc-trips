
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required

from constance import config

from .models import LeaderApplication

import logging
logger = logging.getLogger(__name__)

from django_easyfilters import FilterSet
class LeaderApplicationFilterSet(FilterSet):
    fields = [
        'status',
        'class_year',
    ]

"""
@login_required
def list_view(request):
    applications = LeaderApplication.objects.all()
    app_filter = LeaderApplicationFilterSet(applications, request.GET)
    return render(request, 'leader/list_application.html', {
        'applications': app_filter.qs,
        'application_filter': app_filter,
    })
"""

from vanilla import ListView

class LeaderApplicationList(ListView):
    
    model = LeaderApplication
    template_name = 'leader/list_application.html'
    context_object_name = 'applications'
    filter_object_name = 'application_filter'

    def get_queryset(self):
        applications = super(LeaderApplicationList, self).get_queryset()
        self.app_filter = LeaderApplicationFilterSet(applications, self.request.GET)
        return self.app_filter.qs

    def get_context_data(self, **kwargs):
        context = super(LeaderApplicationList, self).get_context_data(**kwargs)
        context[self.filter_object_name] = self.app_filter
        return context
        
list_view = login_required(LeaderApplicationList.as_view())
    

class LeaderApplicationView(DetailView):
    model = LeaderApplication
    context_object_name = 'leader_application'
    # default template : leaderapplication_detail.html
    
leaderapplication = login_required(LeaderApplicationView.as_view())

class CreateLeaderApplication(CreateView):
    model = LeaderApplication
    fields = ['class_year', 'gender', 'tshirt_size', 'hinman_box', 'phone',
              'offcampus_address', 'notes',] 
    
    def form_valid(self, form):
        """ Attach creating user to Application. """
        form.instance.user = self.request.user
        form.instance.trips_year = config.trips_year
        return super(CreateLeaderApplication, self).form_valid(form)

    # the views uses the default form leaderapplication_form.html

create_leaderapplication = login_required(CreateLeaderApplication.as_view())

class EditLeaderApplication(UpdateView):
    model = LeaderApplication
    fields = '__all__'

edit_leaderapplication = login_required(EditLeaderApplication.as_view())


