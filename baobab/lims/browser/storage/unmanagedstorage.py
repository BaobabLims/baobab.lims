from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims import bikaMessageFactory as _
from baobab.lims.controlpanel.bika_products import ProductsView


class UnmanagedStorageView(BikaListingView):
    """This is the default view for Unmanaged storage.
    """
    template = ViewPageTemplateFile("templates/unmanagedstorage_view.pt")

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.request.set('disable_plone.rightcolumn', 1)

    def __call__(self):

        StoredItems = StoredItemsView(self.context, self.request)
        self.stored_items_table = StoredItems.__call__()

        return self.template()

class StoredItemsView(BikaListingView):
    """This listing shows all items which are stored here.
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.request = request
        self.catalog = 'bika_setup_catalog'
        path = '/'.join(context.getPhysicalPath())
        self.contentFilter = {
            'portal_type': 'StockItem',
            'sort_on': 'sortable_title',
            'path': {'query': path, 'depth': 1, 'level': 0}
        }
        self.context_actions = {}
        self.title = ''
        self.icon = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.columns = {
            'ItemID': {'title': _('Item ID'), 'index': 'id'},
            'ItemTitle': {'title': _('Item Title'), 'index': 'sortable_title'},
            'ItemType': {'title': _('Item Type'), 'index': 'Type'},
            'review_state': {'title': _('State'), 'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'review_state': 'available'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['ItemID',
                         'ItemTitle',
                         'ItemType',
                         'review_state']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['ItemID',
                         'ItemTitle',
                         'ItemType',
                         'review_state']},
        ]

    def folderitem(self, obj, item, index):
        if not item.has_key('obj'):
            return item
        obj = item['obj']

        item['ItemID'] = obj.getId()
        item['ItemTitle'] = obj.Title()
        item['ItemType'] = obj.portal_type
        item['Location'] = obj.getStorageLocation().getHierarchy()
        item['replace']['ItemID'] = \
            "<a href='%s'>%s</a>" % (item['url'], item['ItemID'])
        stitles = [s['title'] for s in obj.getStorageLocation().getStorageTypes()]
        item['StorageTypes'] = ','.join(stitles)

        return item

    def contentsMethod(self, contentFilter):
        return self.context.getBackReferences("ItemStorageLocation")

    def __call__(self):
        self._process_request()
        return self.contents_table(table_only=True)


class UnmanagedStorageContent(ProductsView):
    """This class shows the products in this storage and their quantities
    """
    def __init__(self, context, request):
        # StoredItemsView.__init__(self, context, request)
        ProductsView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.columns = {
            'Title': {'title': _('Title'), 'index': 'sortable_title'},
            'Quantity': {'title': _('Quantity')},
        }
        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {'inactive_state': 'active'},
                'transitions': [],
                'columns': [
                    'Title',
                    'Quantity'
                ]
            },
            {
                'id': 'all',
                'title': _('All'),
                'contentFilter': {'inactive_state': 'active'},
                'transitions': [],
                'columns': [
                    'Title',
                    'Quantity'
                ]
             },
        ]

    def folderitems(self, full_objects=False):
        """
        """
        # si_items = StoredItemsView.folderitems(self, full_objects=False)
        items = ProductsView.folderitems(self)
        stock_items = self.context.getBackReferences("ItemStorageLocation")
        ret = []
        for x in range(len(items)):
            obj = items[x]['obj']
            quantity = 0
            for si in stock_items[:]:
                if si.portal_type == "StockItem":
                    if obj == si.getProduct():
                        quantity += si.getQuantity()
                        stock_items.remove(si)
                else: continue
            if quantity > 0:
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                        (items[x]['url'], items[x]['Title'])
                items[x]['Quantity'] = quantity
                ret.append(items[x])

        return ret
