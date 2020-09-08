import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class GetTransportDates(BrowserView):

    def __init__(self, context, request):

        super(GetTransportDates, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        uc = getToolByName(self.context, 'portal_catalog')

        try:
            uid = self.request['UID']
            brains = uc.searchResults(portal_type='Transport', UID=uid)
            transport = brains[0].getObject()

            return_val = {
                'departure_date': str(transport.getField('DepartureDate').get(transport) or ''),
                'arrival_date': str(transport.getField('ArrivalDate').get(transport) or '')
            }

            return json.dumps(return_val)

        except:
            return json.dumps({
                'sampling_date': '',
                'frozen_time': ''
            })