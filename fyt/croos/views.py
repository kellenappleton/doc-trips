
from fyt.croos.models import Croo
from fyt.db.views import (
    DatabaseCreateView,
    DatabaseDeleteView,
    DatabaseDetailView,
    DatabaseListView,
    DatabaseUpdateView,
)


class CrooListView(DatabaseListView):
    model = Croo
    template_name = 'croos/croo_index.html'
    context_object_name = 'croos'


class CrooCreateView(DatabaseCreateView):
    model = Croo


class CrooDetailView(DatabaseDetailView):
    model = Croo
    fields = ['name', 'description', 'croo_members']


class CrooUpdateView(DatabaseUpdateView):
    model = Croo


class CrooDeleteView(DatabaseDeleteView):
    model = Croo
    success_url_pattern = 'db:croo:index'
