from Products.CMFCore.utils import getToolByName

from bika.lims.workflow import doActionFor
from bika.lims.browser import BrowserView
from bika.lims.browser.sample import SampleEdit as SE


class SampleEdit(SE):
    """This overrides the edit and view of sample.
    """

    def __init__(self, context, request):
        SE.__init__(self, context, request)
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/biospecimen_big.png"
        self.allow_edit = True

    def __call__(self):
        SE.__call__(self)
        return self.template()


class SampleView(SampleEdit):
    """The view of a single sample
    """
    def __call__(self):
        self.allow_edit = False
        return SampleEdit.__call__(self)

class UpdateBoxes(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if 'locTitle' in self.request.form:
            location_title = self.request.form['locTitle']
            if location_title:
                bsc = getToolByName(self.context, "bika_setup_catalog")
                brains = bsc.searchResults(title=location_title)
                location = brains[0].getObject()
                state = self.context.portal_workflow.getInfoFor(location, 'review_state')
                if state != 'occupied':
                    doActionFor(location, 'occupy')
            else:
                location = self.context.getStorageLocation()
                if location:
                    doActionFor(location, 'liberate')

            # TODO: UPDATE THE STATE OF THE BOXES.
        return []