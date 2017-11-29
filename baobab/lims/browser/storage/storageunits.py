from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from baobab.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class StorageUnitsView(BikaListingView):
    """The default listing view for /storage (StorageUnits).

    Shows all items located in /storage folder.  These can be StorageUnit,
    ManagedStorage or UnmanagedStorage.
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageUnitsView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # self.catalog = 'bika_setup_catalog'
        path = '/'.join(self.context.getPhysicalPath())
        self.contentFilter = {
            'path': {'query': path, 'depth': 1, 'level': 0},
            'sort_on': 'sortable_title'
        }
        self.context_actions = {}
        self.title = self.context.Title()
        self.description = ""
        self.icon = self.portal_url + \
                    '/++resource++baobab.lims.images/storageunit_big.png'
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'toggle': False},
            'Type': {'title': _('Type')},
            'Temperature': {'title': _('Temperature'),
                            'toggle': True},
            'Department': {'title': _('Department'),
                           'toggle': True},
        }
        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'Title',
                    'Type',
                    'Description',
                    'Temperature',
                    'Department'
                ]
            },
            {
                'id': 'units',
                'title': _('Storage Units'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'portal_type': 'StorageUnit'
                },
                'transitions': [
                    {'id': 'deactivate'}
                ],
                'columns': [
                    'Title',
                    'Type',
                    'Description',
                    'Temperature',
                    'Department'
                ]
            },
            {
                'id': 'managed',
                'title': _('Managed Storages'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'portal_type': 'ManagedStorage'
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'occupy'}
                ],
                'columns': [
                    'Title',
                    'Type',
                    'Description',
                    'Temperature',
                    'Department'
                ]
            },
            {
                'id': 'unmanaged',
                'title': _('Unmanaged Storages'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'review_state': 'available',
                    'portal_type': 'UnmanagedStorage'
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'occupy'}
                ],
                'columns': [
                    'Title',
                    'Type',
                    'Description',
                    'Temperature',
                    'Department'
                ]
            },
            {
                'id': 'occupied',
                'title': _('Occupied'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'portal_type': 'UnmanagedStorage',
                    'review_state': 'occupied'
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'liberate'}
                ],
                'columns': [
                    'Title',
                    'Type',
                    'Description',
                    'Temperature',
                    'Department'
                ]
            },
            {
                'id': 'occupied_boxes',
                'title': _('Occupied Boxes'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'portal_type': 'ManagedStorage',
                    'review_state': 'occupied'
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'liberate'}
                ],
                'columns': [
                    'Title',
                    'Type',
                    'Description',
                    'Temperature',
                    'Department'
                ]
            }
        ]
        return BikaListingView.__call__(self)

    def folderitem(self, obj, item, index):
        if not item.has_key('obj'):
            return item
        obj = item['obj']
        item['Temperature'] = obj.getTemperature()
        item['Type'] = obj.Type()
        item['Department'] = obj.getDepartment()and obj.getDepartmentTitle() or ''

        if item['Type'] == 'Unmanaged storage':
            title = item['id']
        else:
            title = item['Title']
        item['replace']['Title'] = \
            "<a href='%s'>%s</a>" % (item['url'], title)

        return item
