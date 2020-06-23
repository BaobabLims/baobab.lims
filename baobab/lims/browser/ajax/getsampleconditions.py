import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class ajaxGetSampleConditions(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetSampleConditions, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        rows = []

        # sample_conditions_uid = self.request.form['sample_conditions_uid']
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type="SampleCondition",)

        for brain in brains:
            sample_condition = brain.getObject()
            rows.append({
                sample_condition.UID(): sample_condition.Title()
            })

        print('-------------------Sample Conditions')
        print(json.dumps(rows))

        return json.dumps(rows)




#
# class ComputeTotalPrice(BrowserView):
#     """Return prices of products selected in kit template.
#     """
#
#     def __init__(self, context, request):
#         BrowserView.__init__(self, context, request)
#         self.context = context
#         self.request = request
#
#     def __call__(self):
#         ret = []
#         if 'uids[]' in self.request.form:
#             uids = self.request.form['uids[]']
#             catalog = 'bika_setup_catalog'
#             uc = getToolByName(self.context, catalog)
#             for uid in uids:
#                 brains = uc.searchResults(UID=uid)
#                 product = brains[0].getObject()
#                 ret.append({'title': product.Title(), 'price': product.getPrice()})
#
#         return json.dumps(ret)
