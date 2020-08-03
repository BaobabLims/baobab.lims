import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class ajaxGetSamplePackages(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetSamplePackages, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        rows = []

        # sample_conditions_uid = self.request.form['sample_conditions_uid']
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="SamplePackage")

        for brain in brains:
            strain = brain.getObject()
            rows.append({
                strain.UID(): strain.Title()
            })

        return json.dumps(rows)