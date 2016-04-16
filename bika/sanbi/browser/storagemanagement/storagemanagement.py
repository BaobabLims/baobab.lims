from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.sanbi.controlpanel.bika_storagemanagements import StorageManagementsView


class StorageView(StorageManagementsView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.children = self.context.getChildren()
        super(StorageView, self).__init__(context, request)

    def folderitems(self, full_objects = False):
        items = StorageManagementsView.folderitems(self)
        out_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if obj in self.children or obj.UID() == self.context.UID():
                items[x]['StorageUnit'] = obj.getStorageUnit().Title()
                items[x]['Shelves'] = obj.getShelves() and int(obj.getShelves()) or 0
                items[x]['Hierarchy'] = obj.getHierarchy()
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                               (items[x]['url'], items[x]['Title'])
                out_items.append(items[x])

        return out_items
    
    def __call__(self):
        return super(StorageView, self).__call__()


class StorageManagementView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/storagemanage_view.pt")
    title = _("Managing Storage")

    def __call__(self):
        context = self.context
        request = self.request
        portal = self.portal

        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup

        # __Disable the add new menu item__ #
        context.setLocallyAllowedTypes(())

        # __Collect general data__ #
        self.id = context.getId()
        self.title = context.Title()
        self.type = context.getType()
        self.storage_unit = context.getStorageUnit().Title()
        self.shelves = context.getShelves()
        self.dimension = context.getDimension()

        storages_view = StoragesView(context, request)
        storages_view()
        storages_view.show_column_toggles = False
        self.table = storages_view.contents_table()

        # storage_view = StorageManagementsView(context, request)
        # TODO: THIS LINE IS VERY IMPORTANT IT ALLOWS TO CALL __call__ IN bika_storagemanagements.py
        # TODO: THIS ONE IN TURN CALL __call__ OF BikaListingView CLASS IN bika_listing.py AND
        # TODO: CALL _process_request() WHICH MODIFY self.contentFilter TO ADD FOR EG inactive_state
        # TODO: IN CASE WE CLICK IN dormant BUTTON OF the active-inactive WORKFLOW.
        # storage_view()
        # storage_view.show_column_toggles = False
        # self.table = storage_view.contents_table()

        return self.template()

class StorageManagementEdit(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/storagemanage_edit.pt")

    def __init__(self, context, request):
        super(StorageManagementEdit, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/department_big.png"

    def __call__(self):
        portal = self.portal
        context = self.context
        request = self.request
        setup = portal.bika_setup
        form = request.form

        if "submit" in request: return

        return self.template()

    def get_fields_with_visibility(self, visiblity, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default="invisible", field=field)
            if v == visiblity:
                fields.append(field)

        return fields

    def number_childs_add_sub(self, context, values):
        old_num_items = context.getShelves() and context.getShelves() or 0
        new_num_items = values.get('Shelves') and int(values['Shelves']) or 0

        if 'Shelves' not in values.keys():
            return 0, 0

        num_childs_add = 0
        num_childs_sub = 0
        if new_num_items > old_num_items:
            num_childs_add = new_num_items - old_num_items
        elif new_num_items < old_num_items:
            num_childs_sub = old_num_items - new_num_items

        return num_childs_add, num_childs_sub
