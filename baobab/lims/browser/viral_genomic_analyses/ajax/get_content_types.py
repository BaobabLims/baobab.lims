import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class AjaxGetMethods(BrowserView):
    """
    """

    def __init__(self, context, request):
        super(AjaxGetMethods, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        methods = []

        catalog = 'portal_catalog'
        portal_catalog = getToolByName(self.context, catalog)
        brains = portal_catalog(portal_type='Method')
        print('---------------Methods')
        print(brains)

        for brain in brains:
            method = brain.getObject()
            methods.append({method.UID(): method.Title()})

        return json.dumps(methods)



class AjaxGetVirusSamples(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(AjaxGetVirusSamples, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        virus_samples = []
        if 'project_uid' in self.request.form:
            current_project = self.get_content_type(self.request.form['project_uid'])
            catalog = 'portal_catalog'
            portal_catalog = getToolByName(self.context, catalog)
            brains = portal_catalog(portal_type='VirusSample', inactive_state='active')
            print(brains)

            for brain in brains:
                virus_sample = brain.getObject()
                if current_project and current_project.Title() == self.get_title(virus_sample):
                    virus_samples.append({virus_sample.UID(): virus_sample.Title()})

        return json.dumps(virus_samples)

    def get_content_type(self, content_type_uid, catalog="portal_catalog"):
        try:
            catalog = self.get_catalog(catalog)
            brains = catalog(UID=content_type_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

    def get_catalog(self, catalog="portal_catalog"):
        if catalog == 'bika_setup_catalog':
            return getToolByName(self.context, 'bika_setup_catalog')

        if catalog == 'portal_catalog':
            return getToolByName(self.context, 'portal_catalog')

    def get_title(self, virus_sample):
        try:
            return virus_sample.getProject().Title()
        except:
            return ''

