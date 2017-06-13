import json

from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims.interfaces import ISample
from baobab.lims.browser.biospecimens.biospecimens import BiospecimensView
from baobab.lims import bikaMessageFactory as _
from baobab.lims.browser.multimage import MultimagesView
from baobab.lims.interfaces import IBiospecimenStorage
from baobab.lims.config import VOLUME_UNITS


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
            object_provides = IBiospecimenStorage.__identifier__,
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

class AliquotsView(BiospecimensView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AliquotsView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'Sample',
            'sort_on': 'sortKey',
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Aliquots"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/aliquot_big.png"

    def folderitems(self, full_objects=False):
        items = super(AliquotsView, self).folderitems(self)
        linked_samples = self.context.getBackReferences("SampleSample")
        new_items = []
        for x, item in enumerate(items):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            if not ISample.providedBy(obj) or obj not in linked_samples:
                continue

            items[x]['Type'] = obj.getSampleType() and obj.getSampleType().Title() or ''
            items[x]['Volume'] = obj.getField('Volume').get(obj)
            items[x]['Unit'] = VOLUME_UNITS[0]['ResultText']
            items[x]['SubjectID'] = obj.getField('SubjectID').get(obj)
            kit = obj.getField('Kit').get(obj)
            project = obj.getField('Project').get(obj)
            items[x]['Kit'] = kit
            items[x]['Project'] = project
            if project:
                items[x]['replace']['Project'] = \
                    '<a href="%s">%s</a>' % (project.absolute_url(),
                                             project.Title())
            if kit:
                items[x]['replace']['Kit'] = \
                    '<a href="%s">%s</a>' % (kit.absolute_url(), kit.Title())

                items[x]['replace']['Type'] = \
                    '<a href="%s">%s</a>' % (obj.getSampleType().absolute_url(),
                                             obj.getSampleType().Title())

            items[x]['Barcode'] = obj.getField('Barcode').get(obj)
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            new_items.append(item)

        return new_items

