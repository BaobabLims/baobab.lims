import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class GetSampleDates(BrowserView):

    def __init__(self, context, request):

        super(GetSampleDates, self).__init__(context, request)
        self.context = context
        self.request = request

        # print('===================')
        # print('Ajax has been reached.')



    def __call__(self):

        uc = getToolByName(self.context, 'portal_catalog')

        # print('===================')
        title = self.request.form['title']
        # print(title)
        # print('Ajax has been reached.')
        # print(self.request)

        brains = uc.searchResults(portal_type='Sample', Title=title)

        try:
            sample = brains[0].getObject()
            return_val = {
                'sampling_date': str(sample.getField('SamplingDate').get(sample) or ''),
                'frozen_time': str(sample.getField('FrozenTime').get(sample) or '')
            }

            # print('return val is %s' %str(return_val))
            return json.dumps(return_val)

        except:
            return json.dumps({
                'sampling_date': '',
                'frozen_time': ''
            })





        # if 'yes_sample_uids[]' in self.request.form:
        #     yes_sample_uids = self.request.form['yes_sample_uids[]']
        #
        #     if isinstance(yes_sample_uids, basestring):
        #         yes_sample_uids = [yes_sample_uids]
        #
        #     for uid in yes_sample_uids:
        #         brains = uc.searchResults(UID=uid)
        #         sample = brains[0].getObject()
        #         sample.WillReturnFromShipment = True
        #         sample.reindexObject()
        #
        # if 'no_sample_uids[]' in self.request.form:
        #     no_sample_uids = self.request.form['no_sample_uids[]']
        #
        #     if isinstance(no_sample_uids, basestring):
        #         no_sample_uids = [no_sample_uids]
        #
        #     for uid in no_sample_uids:
        #         brains = uc.searchResults(UID=uid)
        #         sample = brains[0].getObject()
        #         sample.WillReturnFromShipment = False
        #         sample.reindexObject()

        # return json.dumps(None)