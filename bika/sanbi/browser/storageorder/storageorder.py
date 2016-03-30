from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class StorageOrderEdit(BrowserView):

    template = ViewPageTemplateFile("templates/storageorder_edit.pt")

    def __init__(self, context, request):
        super(StorageOrderEdit, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/department_big.png"

    def __call__(self):
        portal = self.portal
        context = self.context
        request = self.request
        setup = portal.bika_setup

        if "submit" in request:
            '''
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            '''
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

class StorageOrderView(BrowserView):

    template = ViewPageTemplateFile('templates/storageorder_view.pt')
    title = _("Storage Levels")

    def __call__(self):

        context = self.context
        portal = self.portal

        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup
        # Disable the add new menu item
        context.setConstrainTypesMode(1)
        context.setLocallyAllowedTypes(())
        # Collect general data
        self.id = context.getId()
        self.title = context.Title()

        return self.template()