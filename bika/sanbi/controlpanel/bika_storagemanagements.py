from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi.config import PROJECTNAME
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IStorageManagements
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo


class StorageManagementsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageManagementsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {
            'portal_type': 'StorageManagement',
            'sort_on': 'created',
            'sort_order': 'ascending'
        }
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name=StorageManagement',
                'icon': '++resource++bika.lims.images/add.png'
            }
        }
        self.title = self.context.translate(_("Storage Management"))
        self.icon = self.portal_url +"/++resource++bika.lims.images/department_big.png"
        self.description = ''
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
            'Shelves': {
                    'title': _('Children Number'),
                    'toggle': True
            },
            'Hierarchy': {
                    'title': _('Hierarchy'),
                    'toggle': True
            },
            #TODO: MAYBE WE NEED TO ADD A COLUMN SHOWING THE DIMENSION, 1D,2D,3D
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Shelves',
                         'Hierarchy']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Shelves',
                         'Hierarchy']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{'sort_on': 'created',
                              'sort_order': 'ascending'},
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Shelves',
                         'Hierarchy']},
        ]

    def __call__(self):
        return super(StorageManagementsView, self).__call__()

    def folderitems(self, full_objects = False):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['StorageUnit'] = obj.getStorageUnit().Title()
            items[x]['Shelves'] = obj.getShelves() and int(obj.getShelves()) or 0
            items[x]['Hierarchy'] = obj.getHierarchy()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class StorageManagements(ATFolder):
    implements(IStorageManagements)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(StorageManagements, PROJECTNAME)