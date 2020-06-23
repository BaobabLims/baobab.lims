import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class GetSamplePoolingData(BrowserView):

    def __init__(self, context, request):

        super(GetSamplePoolingData, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        uc = getToolByName(self.context, 'portal_catalog')

        try:
            uid = self.request['UID']
            brains = uc.searchResults(portal_type='SamplePooling', UID=uid)
            sample_pooling = brains[0].getObject()

            return_val = {
                'date_created': str(sample_pooling.getField('DateCreated').get(sample_pooling) or ''),
            }

            return json.dumps(return_val)

        except:
            return json.dumps({
                'date_created': '',
            })