from bika.lims.browser import BrowserView
import plone

class ajaxReferenceWidgetSearch(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)