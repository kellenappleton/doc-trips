import django_tables2 as tables
from django.utils.safestring import mark_safe

from fyt.db.templatetags.links import detail_link, edit_link


class DetailLinkColumn(tables.Column):
    """
    Render a ForeignKey value as a link to the object's
    detail view.
    """
    def render(self, value):
        return detail_link(value)


class RegistrationTable(tables.Table):
    """
    Table for Registrations
    """
    class Meta:
        attrs = {
            "class": "table table-condensed"  # bootstrap
        }

    user = tables.Column(
        verbose_name='Registration'
    )
    trip_assignment = tables.Column(
        accessor='trippee', order_by='-trippee__trip_assignment'
    )
    trippee = DetailLinkColumn(
        verbose_name='Incoming Student Data'
    )
    edit_link = tables.Column(
        verbose_name=' ', accessor='user'
    )

    def render_user(self, record):
        return detail_link(record)

    def render_trip_assignment(self, value):
        return detail_link(value.trip_assignment) or mark_safe('&mdash;')

    def render_edit_link(self, record):
        return edit_link(record)


class IncomingStudentTable(tables.Table):
    """
    Table for displaying Incoming Students
    """
    class Meta:
        attrs = {
            "class": "table table-condensed"
        }

    name = tables.Column(
        verbose_name='Student'
    )
    registration = DetailLinkColumn(
        verbose_name='Registration'
    )
    trip_assignment = DetailLinkColumn(
        verbose_name='Trip'
    )
    incoming_status = tables.Column(
        verbose_name='Status'
    )
    bus_assignment_round_trip = DetailLinkColumn(
        verbose_name='Bus ROUND TRIP', orderable=False
    )
    bus_assignment_to_hanover = DetailLinkColumn(
        verbose_name='Bus TO Hanover', orderable=False
    )
    bus_assignment_from_hanover = DetailLinkColumn(
        verbose_name='Bus FROM Hanover', orderable=False
    )

    def render_name(self, record):
        return detail_link(record)
