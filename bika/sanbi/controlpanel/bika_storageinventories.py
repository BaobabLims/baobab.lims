from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi.config import PROJECTNAME
from bika.sanbi import bikaMessageFactory as _
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.sanbi.interfaces import IStorageInventories

class StorageInventoriesView(BikaListingView):
    #template = ViewPageTemplateFile('templates/storagelevels.pt')
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageInventoriesView, self).__init__(context, request)
        path = '/'.join(self.context.getPhysicalPath())
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageInventory',
                              'sort_on': 'sortable_title'}
        # self.context_actions = {_('Add'):
        #                         {'url': 'createObject?type_name=StorageInventory',
        #                          'icon': '++resource++bika.lims.images/add.png'}}
        self.title = (hasattr(self.context, 'Title') and self.context.Title() or
                      self.context.translate(_("Storage Levels")))
        self.icon = self.portal_url
        self.icon += "/++resource++bika.sanbi.images/inventory_big.png"
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
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending',
                               'getHasChildren': True},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Hierarchy']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive',
                               'sort_on': 'created',
                               'sort_order': 'ascending',
                               'getHasChildren': True,
                               'getUnitID': context.getId()},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Hierarchy']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{'sort_on': 'created',
                              'sort_order': 'ascending',
                              'getHasChildren': True,
                              'getUnitID': context.getId()},
             'columns': ['Title',
                         'Description',
                         'StorageUnit',
                         'Hierarchy']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['StorageUnit'] = obj.aq_parent.Title()
            items[x]['Hierarchy'] = obj.getHierarchy()
            # items[x]['IsOccupied'] = 'yes' if obj.getIsOccupied() else 'no'

        return items

schema = ATFolderSchema.copy()
class StorageInventories(ATFolder):
    implements(IStorageInventories)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StorageInventories, PROJECTNAME)
