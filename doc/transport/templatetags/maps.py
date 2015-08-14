from django.template import Library, loader, Context
from django.conf import settings

from doc.incoming.models import sort_by_lastname
from doc.transport.maps import _split_stops, MapError

register = Library()

@register.simple_tag
def embed_map(stops):
    """
    Embed a google map in the page, showing directions
    along the passed stops. The stop[0] is the origin,
    stop[-1] the destination. Intermediate stops are 
    waypoints on the route.
    """
    orig, waypoints, dest = _split_stops(stops)

    return loader.get_template(
        'transport/maps/embed.html'
    ).render(Context({
        'orig': orig,
        'waypoints': waypoints,
        'dest': dest,
        'key': settings.GOOGLE_MAPS_BROWSER_KEY
    }))


@register.inclusion_tag('transport/maps/directions.html')
def directions(bus):
    """
    Given an internal bus, display directions or MapError.
    """
    try:
        return {
            'directions': bus.directions(),
            'start_stop_template': 'transport/maps/_internal_start_stop.html',
            'end_stop_template': 'transport/maps/_internal_end_stop.html'
        }
    except MapError as exc:
        return {'error': exc}


@register.inclusion_tag('transport/maps/directions.html')
def directions_to_hanover(bus):
    """
    Directions for an external bus to hanover.
    """
    try:
        return {
            'directions': bus.directions_to_hanover(),
            'start_stop_template': 'transport/maps/_external_start_stop.html',
            'end_stop_template': 'transport/maps/_external_end_stop.html'
        }
    except MapError as exc:
        return {'error': exc}


@register.inclusion_tag('transport/maps/directions.html')
def directions_from_hanover(bus):
    """
    Directions for an external bus from hanover.
    """
    try:
        return {
            'directions': bus.directions_from_hanover(),
            'start_stop_template': 'transport/maps/_external_start_stop.html',
            'end_stop_template': 'transport/maps/_external_end_stop.html'
        }
    except MapError as exc:
        return {'error': exc}


@register.inclusion_tag('transport/maps/_trips_with_counts.html')
def trips_with_counts(trips):
    """
    Checklist of trips with size of trips.
    """
    return {'trips': trips}


def split(a, n):
    """
    http://stackoverflow.com/a/2135920/3818777
    """
    import math
    k, m = math.floor(len(a) / n), len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


@register.inclusion_tag('transport/maps/_trippees.html')
def trippees(trippees):
    """
    Checklist of trippees, split into 3 columns.
    """
    trippees = sort_by_lastname(trippees)
    col1, col2, col3 = split(trippees, 3)
    return {
        'trippees': trippees,
        'col1': col1,
        'col2': col2,
        'col3': col3,
    }
