from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView
from bika.sanbi import bikaMessageFactory as _


class AliquotEdit(BrowserView):
    # template = ViewPageTemplateFile('templates/aliquot_edit.pt')
    title = _("Sample Add/Edit")

    def __init__(self, context, request):
        super(AliquotEdit, self).__init__(context, request)
        self.context = context
        self.request = request

        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/aliquot_big.png"

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        form = self.request.form
        if 'submit' in request:
            context.setConstrainTypesMode(constraintypes.DISABLED)

            # If we edit sample with empty location we have to set location
            # too free
            if not form.get('StorageLocation', ''):
                wftool = self.context.portal_workflow
                locs = self.context.getBackReferences('ItemStorageLocation')
                if locs:
                    loc = locs[0]
                    state = wftool.getInfoFor(loc, 'review_state')
                    if state == 'occupied':
                        loc.setAliquot(None)
                        wftool.doActionFor(loc, action='liberate',
                                           wf_id='bika_storage_workflow')

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
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
