from bika.sanbi import bikaMessageFactory as _
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.lims.browser.multifile import MultifileView

class SupplyExMultifileView(MultifileView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SupplyExMultifileView, self).__init__(context, request)
        self.show_workflow_action_buttons = False
        self.title = self.context.translate(_("Kit Attachments"))
        self.description = "Different interesting documents and files to be attached to the kit"