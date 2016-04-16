from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component.interfaces import ComponentLookupError
from bika.lims.interfaces import IHeaderTableFieldRenderer
from zope.component import getAdapter

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

        if "submit" in request: return

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

    def three_column_list(self, input_list):
        list_len = len(input_list)
        sublist_len = (list_len % 2 == 0 and list_len / 2 or list_len / 2 + 1)

        def _list_end(num):
            return num == 1 and list_len or (num + 1) * sublist_len
        final = []
        for i in range(2):
            column = input_list[i * sublist_len:_list_end(i)]

            #this create empty row. Compare with analysisrequest_view.pt
            for j in range(2*len(column)):
                if j % 2 == 1:
                    column.insert(j, {'fieldName': '', 'mode': 'edit'})

            if len(column) > 0:
                final.append(column)

        return final

    def sublists(self):
        ret = []
        prominent = []
        for field in self.context.Schema().fields():
            field_name = field.getName()
            state = field.widget.isVisible(self.context, 'header_table', default='invisible', field=field)
            if state == 'invisible':
                continue
            elif state == 'prominent':
                if field.widget.isVisible(self.context, 'edit', default='invisible', field=field) == 'visible':
                    prominent.append({'fieldName': field_name, 'mode': 'edit'})
            elif state == 'visible':
                if field.widget.isVisible(self.context, 'edit', default='invisible', field=field) == 'visible':
                    ret.append({'fieldName': field_name, 'mode': 'edit'})

        return prominent, self.three_column_list(ret)

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