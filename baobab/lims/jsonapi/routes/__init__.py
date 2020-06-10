from bika.lims.jsonapi import add_route as add_bika_route

BASE_URL = "/v3"


def add_route(route, endpoint=None, **kw):
    """Add a new v2 JSON API route
    """

    # ensure correct amout of slashes
    def apiurl(route):
        return '/'.join(s.strip('/') for s in ["", BASE_URL, route])

    return add_bika_route(apiurl(route), endpoint, **kw)
