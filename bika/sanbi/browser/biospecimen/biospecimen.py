import json

from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.sanbi.browser.multimage import MultimagesView
from bika.sanbi.interfaces import IBioSpecimenStorage


class AjaxBoxPositions:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        uc = getToolByName(self.context, 'uid_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = uc(UID=form['uid'])
        box = brains[0].getObject()
        brains = bsc.searchResults(
            portal_type='StorageLocation',
            object_provides = IBioSpecimenStorage.__identifier__,
            inactive_state='active',
            sort_on='sortable_title',
            path={'query': "/".join(box.getPhysicalPath()), 'level': 0})

        if not brains:
            msg = 'No free storage position. Please select another container.'
            return json.dumps({'error': self.context.translate(_(msg))})

        return json.dumps({'uid': brains[0].UID, 'address': brains[0].title})


class BiospecimenMultimageView(MultimagesView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(BiospecimenMultimageView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.show_workflow_action_buttons = False
        self.title = self.context.translate(_("Biospecimen Files"))
        self.description = "Different interesting documents, files and " \
                           "images to be attached to the biospecimen."
