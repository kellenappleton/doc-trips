
from django.http import JsonResponse
from dartdm.lookup import dartdm_lookup

def dartdm_lookup_view(request):
    """ 
    Dartmouth Name Directory connector.

    The dartdm netid lookup doesn't allow cross-site requests, 
    hence no AJAX. This view allows us to do DND lookups by acting as 
    an endpoint for typeahead.
    """
    
    try:
        query = request.GET['query']
    except KeyError:
        results = []
    else:
        results = dartdm_lookup(query)
    # setting safe=False allows us to return the JSON array
    return JsonResponse(results, safe=False) 

