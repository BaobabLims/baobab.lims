from bika.lims import bikaMessageFactory as _
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.sanbi.browser.multimage import MultimagesView
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
import json

class BiospecimenEdit(BrowserView):
    template = ViewPageTemplateFile('templates/biospecimen_edit.pt')
    title = _("Biospecimen Add/Edit")

    def __init__(self, context, request):
        self.context = context
        self.request = request

        super(BiospecimenEdit, self).__init__(context, request)
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/biospecimen_big.png"

    def __call__(self):
        portal = self.portal
        form = self.request.form

        if 'submit' in self.request:
            self.context.setConstrainTypesMode(constraintypes.DISABLED)

            portal_factory = getToolByName(self.context, 'portal_factory')
            biospecimen = portal_factory.doCreate(self.context, self.context.id)
            biospecimen.processForm()
            biospecimen.edit(
                quantity=1
            )
            obj_url = biospecimen.absolute_url_path()
            self.request.response.redirect(obj_url)
            return

        return self.template()

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields

    def get_storage_units(self):
        display_list = list(self.context.getStorageUnits().items())
        return display_list

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
        brains = brains = bsc.searchResults(
                        portal_type='StorageLocation',
                        inactive_state='active',
                        sort_on='sortable_title',
                        path={'query': "/".join(box.getPhysicalPath()), 'level': 0})

        message = 'No free position in stock. Please select another container.' if not len(brains) else ''
        if message:
            return json.dumps({'error': message})

        return json.dumps({'uid': brains[0].UID, 'address': brains[0].title})

class BiospecimenMultimageView(MultimagesView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(BiospecimenMultimageView, self).__init__(context, request)
        self.show_workflow_action_buttons = False
        self.title = self.context.translate(_("Biospecimen Files"))
        self.description = "Different interesting documents, files and " \
                           "images to be attached to the biospecimen."
