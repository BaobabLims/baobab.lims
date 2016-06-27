from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.sanbi.browser.multimage import MultimagesView

class BiospecimenMultimageView(MultimagesView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(BiospecimenMultimageView, self).__init__(context, request)
        self.show_workflow_action_buttons = False
        self.title = self.context.translate(_("Biospecimen Files"))
        self.description = "Different interesting documents, files and " \
                           "images to be attached to the biospecimen."
