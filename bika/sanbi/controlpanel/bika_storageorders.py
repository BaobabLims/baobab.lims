from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi.config import PROJECTNAME
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IStorageOrders
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

class StorageOrdersView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageOrdersView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageOrder',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=StorageOrder',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Storage Orders"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/department_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25

        self.categories = []
        self.do_cats = True # TODO: Please repace the right part by a variable defined in bika_setup
                            # TODO: check browser/supplier.py line 37
        if self.do_cats:
            self.pagesize = 999999  # hide batching controls
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.category_index = 'getCategoryTitle'

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'getStorageUnit': {'title': _('Storage Level'),
                               'toggle': True},
            'getNumber': {'title': _('Number Items'),
                          'toggle': True},
            'getParent': {'title': _('Parent'),
                          'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'getStorageUnit',
                         'getNumber',
                         'getParent']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'getStorageUnit',
                         'getNumber',
                         'getParent']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description',
                         'getStorageUnit',
                         'getNumber',
                         'getParent']},
        ]

    def parentLevel(self, uid):
        catalog = getToolByName(self.context, 'portal_catalog')
        if uid:
            brains = catalog(UID=uid)
            obj = brains[0].getObject()
            if obj.portal_type == "StorageOrders":
                return obj.Title()
        return None

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            cat = obj.getCategoryTitle()
            if self.do_cats:
                items[x]['category'] = cat
                if cat not in self.categories:
                    self.categories.append(cat)
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['getStorageUnit'] = obj.getStorageUnit().Title()
            items[x]['getNumber'] = int(obj.getNumber())
            items[x]['getParent'] = self.parentLevel(obj.getParent())

        return items

schema = ATFolderSchema.copy()
class StorageOrders(ATFolder):
    implements(IStorageOrders)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StorageOrders, PROJECTNAME)
