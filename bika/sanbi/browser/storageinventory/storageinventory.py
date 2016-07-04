from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi.config import DIMENSION_OPTIONS, INVENTORY_TYPES


class PositionsView(BikaListingView):
    def __init__(self, context, request):
        super(PositionsView, self).__init__(context, request)
        self.context = context
        self.request = request
        path = '/'.join(self.context.getPhysicalPath())
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageInventory',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = (hasattr(self.context, 'Title') and self.context.Title() or
                      self.context.translate(_("Storage Levels")))
        self.icon = self.portal_url
        self.icon += "/++resource++bika.sanbi.images/list_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title'
            },
            'Description': {
                'title': _('Description'),
                'index': 'description',
                'toggle': True
            },
            'StorageUnit': {
                'title': _('Parent'),
                'toggle': True
            },
            'Hierarchy': {
                'title': _('Hierarchy'),
                'toggle': True
            },
            'ISID': {
                'title': _('Stock item ID'),
                'toggle': True
            },
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending',
                               'getLocation': True,
                               'getUnitID': self.context.getId()},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Hierarchy',
                         'ISID']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive',
                               'sort_on': 'created',
                               'sort_order': 'ascending',
                               'getLocation': True,
                               'getUnitID': self.context.getId()},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Hierarchy',
                         'ISID']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {'sort_on': 'created',
                               'sort_order': 'ascending',
                               'getLocation': True,},
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Hierarchy',
                         'ISID']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        out_items=[]
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            items[x]['StorageUnit'] = obj.aq_parent.Title()
            items[x]['Hierarchy'] = obj.getHierarchy()
            items[x]['ISID'] = obj.getISID()
            out_items.append(items[x])

        return out_items

class InventoryStorageView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/storageinventory_view.pt")
    title = _("Storage Inventory View")

    @staticmethod
    def dimension_text(context):
        dimension = context.getDimension()
        text = ''
        if dimension:
            text = DIMENSION_OPTIONS.getValue(dimension[0])

        return text

    @staticmethod
    def type_text(context):
        type = context.getType()
        text = ''
        if type:
            text = INVENTORY_TYPES.getValue(type[0])

        return text

    def __call__(self):
        context = self.context
        request = self.request
        portal = self.portal

        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/info_big.png"
        # Disable the add new menu item #
        context.setLocallyAllowedTypes(())

        # Collect general data #
        self.id = context.getId()
        self.title = context.Title()
        self.type = self.type_text(context)
        self.parent = context.aq_parent.Title()
        self.numPositions = context.getNumPositions()
        self.dimension = self.dimension_text(context)

        table = PositionsView(context, request)
        # table()
        table.show_column_toggles = False
        self.table = table.contents_table()

        return self.template()

class InventoryStorageEdit(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/inventorystorage_edit.pt")

    def __init__(self, context, request):
        super(InventoryStorageEdit, self).__init__(context, request)
        self.icon = ""

    def __call__(self):
        portal = self.portal
        context = self.context
        request = self.request
        setup = portal.bika_setup
        form = request.form

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


class InventoryGraph(InventoryStorageView):
    template = ViewPageTemplateFile("templates/inventory_graph.pt")
    title = _("Managing Inventory")

    def __init__(self, context, request):
        super(InventoryGraph, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', 1)

    def __call__(self):
        return self.template()
