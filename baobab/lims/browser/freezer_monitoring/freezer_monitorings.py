from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView


class FreezerMonitoringView(BrowserView):
    template = ViewPageTemplateFile("templates/freezer_monitorings.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        return self.template()
