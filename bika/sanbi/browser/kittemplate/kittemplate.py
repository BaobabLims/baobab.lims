from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from operator import itemgetter, methodcaller

from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView

from Products.ATContentTypes.lib import constraintypes

class EditView(BrowserView):

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

        if 'submit' in request:
            print 'salam'
        else:
            request.response.redirect(context.absolute_url())
