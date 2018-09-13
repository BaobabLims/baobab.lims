import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class ajaxSetSamplesReturn(BrowserView):

    def __init__(self, context, request):
        super(ajaxSetSamplesReturn, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        catalog = 'portal_catalog'
        uc = getToolByName(self.context, catalog)

        if 'yes_sample_uids[]' in self.request.form:
            yes_sample_uids = self.request.form['yes_sample_uids[]']

            if isinstance(yes_sample_uids, basestring):
                yes_sample_uids = [yes_sample_uids]

            for uid in yes_sample_uids:
                brains = uc.searchResults(UID=uid)
                sample = brains[0].getObject()
                sample.WillReturnFromShipment = True
                sample.reindexObject()

        if 'no_sample_uids[]' in self.request.form:
            no_sample_uids = self.request.form['no_sample_uids[]']

            if isinstance(no_sample_uids, basestring):
                no_sample_uids = [no_sample_uids]

            for uid in no_sample_uids:
                brains = uc.searchResults(UID=uid)
                sample = brains[0].getObject()
                sample.WillReturnFromShipment = False
                sample.reindexObject()

        return json.dumps(None)