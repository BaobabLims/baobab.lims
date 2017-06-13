from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from baobab.lims.interfaces import IProducts

class ProductsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ProductsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'Product',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Product',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Products"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/product_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        if self.context.portal_type == 'Products':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'CAS': {'title': _('CAS'),
                    'toggle': True},
            'SupplierCatalogueID': {'title': _('Supplier Catalogue ID'),
                                    'toggle': False},
            'Quantity': {'title': _('Quantity'),
                         'toggle': True},
            'VATAmount': {'title': _('VATAmount'),
                           'toggle': True},
            'Price': {'title': _('Price'),
                      'toggle': False},
            'TotalPrice': {'title': _('Total Price'),
                           'toggle': True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'CAS',
                         'Quantity',
                         'VATAmount',
                         'Price',
                         'TotalPrice']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'CAS',
                         'Quantity',
                         'VATAmount',
                         'Price',
                         'TotalPrice']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'CAS',
                         'Quantity',
                         'VATAmount',
                         'Price',
                         'TotalPrice']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['CAS'] = obj.getCAS()
            items[x]['Quantity'] = obj.getQuantity()
            if obj.getQuantity() and obj.getUnit():
                items[x]['Quantity'] = str(obj.getQuantity())
            items[x]['VATAmount'] = obj.getVATAmount()
            items[x]['Price'] = obj.getPrice()
            items[x]['TotalPrice'] = obj.getTotalPrice()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
        return items

schema = ATFolderSchema.copy()
class Products(ATFolder):
    implements(IProducts)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Products, PROJECTNAME)
