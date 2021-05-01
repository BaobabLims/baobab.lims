from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class FreezersView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Freezer',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=Freezer',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Freezers"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'Freezers':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {
                'title': _('Title'),
                # 'input_width': '10'
            },
            'Description': {
                'title': _('Description'),
                # 'type': 'choices'
            },
            'StorageUnit': {
                'title': _('StorageUnit'),
                # 'type': 'choices'
            },
            'MonitoringDevice': {
                'title': _('Monitoring Device'),
                # 'type': 'choices'
            },
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'sort_on': 'sortable_title',
                    'sort_order': 'ascending'
                },
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'Title',
                    'Description',
                    'StorageUnit',
                    'MonitoringDevice',
                ]
            }
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(AddPortalContent, self.context):
            self.show_select_row = True
            self.show_select_column = True

        return BikaListingView.__call__(self)

    def folderitems(self, full_objects=False):

        items = BikaListingView.folderitems(self)

        for x in range(len(items)):

            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            items[x]['Title'] = obj.Title()

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'],
                                                    items[x]['Title'])

            items[x]['StorageUnit'] = self.getObjectTitle(obj.getStorageUnit())
            items[x]['MonitoringDevice'] = self.getObjectTitle(obj.getMonitoringDevice())

        return items

    def getObjectTitle(self, obj):
        try:
            return obj.Title()
        except:
            return ''

    def getStringified(self, elements):
        if not elements:
            return ''

        elements_list = []
        for element in elements:
            elements_list.append(element.title)

        elements_string = ', '.join(map(str, elements_list))
        return elements_string
