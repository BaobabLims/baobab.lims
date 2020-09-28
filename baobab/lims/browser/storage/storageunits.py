from plone.app.content.browser.interfaces import IFolderContentsView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import json
from bika.lims import api
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
    template = ViewPageTemplateFile("templates/storage_units.pt")

    def __init__(self, context, request):
        super(StorageUnitsView, self).__init__(context, request)
        self.context = context
        self.request = request

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

    def __call__(self):
        self.items = BikaListingView.folderitems(self)
        self.show_workflow_action_buttons = True
        self.actions = self.get_workflow_actions()
        return self.template()


class StorageUnitsxView(BikaListingView):
    """The default listing view for /storage (StorageUnits).

    Shows all items located in /storage folder.  These can be StorageUnit,
    ManagedStorage or UnmanagedStorage.
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageUnitsxView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self, id=None):
        self.positions = self.context.objectValues()
        self.title = self.context.title
        icon_man = self.portal_url + \
            '/++resource++baobab.lims.images/storageunit.png'
        self.positions_table = []
        for i in self.positions:
            p_dict = {"id": i.UID(), "text": str(i.title), 'children': True,
                      'portal_type': i.portal_type}
            image_url = self.portal_url + '/++resource++baobab.lims.images/'
            icon_man = image_url + i.portal_type.lower() + '.png'
            p_dict['icon'] = icon_man
            print i.title
            if i.portal_type != 'StoragePosition' and \
                    i.portal_type != 'UnmanagedStorage':
                p_dict['url'] = i.absolute_url()
            p_dict['children'] = True
            if not i.objectValues():
                p_dict['children'] = False

            self.positions_table.append(p_dict)

        uid = self.request.form.get("id", '#')
        if uid == '#':
            return json.dumps(self.positions_table)
        obj = api.get_object_by_uid(uid)
        self.positions_table = []
        for i in obj.contentValues():
            p_dict = {"id": i.UID(), "text": str(i.title),
                      'portal_type': i.portal_type}
            image_url = self.portal_url + '/++resource++baobab.lims.images/'
            icon_man = '{}{}.png'.format(image_url, i.portal_type.lower())
            p_dict['icon'] = icon_man
            if i.portal_type != 'StoragePosition' and \
                    i.portal_type != 'UnmanagedStorage':
                p_dict['url'] = i.absolute_url()
            p_dict['children'] = True
            if not i.objectValues():
                p_dict['children'] = False

            self.positions_table.append(p_dict)
        # data['jstree'] = build_tree(hierachy)
        # data['actions'] = self.actions
        return json.dumps(self.positions_table)
