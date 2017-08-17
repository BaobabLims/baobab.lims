import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class ajaxGetProducts(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetProducts, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request[
            'searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type='Product',
                                         inactive_state='active')
        if brains and searchTerm:
            brains = [p for p in brains if
                      p.Title.lower().find(searchTerm) > -1]

        for p in brains:
            rows.append({'product': p.Title,
                         'product_uid': p.UID,
                         'Description': p.Description,
                         'price': p.getPrice})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()),
                      key=itemgetter(sidx and sidx or 'product'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(
                   nr_rows)]}

        return json.dumps(ret)


class ComputeTotalPrice(BrowserView):
    """Return prices of products selected in kit template.
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        ret = []
        if 'uids[]' in self.request.form:
            uids = self.request.form['uids[]']
            catalog = 'bika_setup_catalog'
            uc = getToolByName(self.context, catalog)
            for uid in uids:
                brains = uc.searchResults(UID=uid)
                product = brains[0].getObject()
                ret.append({'title': product.Title(), 'price': product.getPrice()})

        return json.dumps(ret)
