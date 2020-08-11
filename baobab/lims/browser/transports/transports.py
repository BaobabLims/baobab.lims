from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class TransportsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.catalog = 'portal_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Transport',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=Transport',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Transports"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'Transport':
            self.request.set('disable_border', 1)

        self.columns = {
            'ApplicationNumber': {
                'title': _('Application Number'),
                # 'input_width': '10'
            },
            'DepositorName': {
                'title': _('Depositor Name'),
                # 'type': 'choices'
            },
            'NumberOfPackages': {
                'title': _('Number Of Packages'),
                # 'type': 'choices'
            },
            'DepartureDate': {
                'title': _('Departure Date'),
                # 'input_width': '10'
            },
            'ArrivalDate': {
                'title': _('Arrival Date'),
                # 'type': 'choices'
            }
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                    # 'cancellation_state': 'active',
                    'sort_on': 'sortable_title',
                    'sort_order': 'ascending'
                },
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'ApplicationNumber',
                    'DepositorName',
                    'NumberOfPackages',
                    'DepartureDate',
                    'ArrivalDate',
                ]
            },

            {
                'id': 'departed',
                'title': _('Departed'),
                'contentFilter': {
                    'review_state': 'departed',
                    # 'cancellation_state': 'active',
                    'inactive_state': 'active',
                    'sort_on': 'sortable_title',
                    'sort_order': 'ascending'
                },
                'transitions': [{'id': 'arrives'}],
                'columns': [
                    'ApplicationNumber',
                    'DepositorName',
                    'NumberOfPackages',
                    'DepartureDate',
                    'ArrivalDate',
                ]
            },

            {
                'id': 'arrived',
                'title': _('Arrived'),
                'contentFilter': {
                    'review_state': 'arrived',
                    # 'cancellation_state': 'active',
                    'inactive_state': 'active',
                    'sort_on': 'sortable_title',
                    'sort_order': 'ascending'
                },
                'columns': [
                    'ApplicationNumber',
                    'DepositorName',
                    'NumberOfPackages',
                    'DepartureDate',
                    'ArrivalDate',
                ]
            },
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

            items[x]['ApplicationNumber'] = obj.getField('ApplicationNumber').get(obj)

            items[x]['replace']['ApplicationNumber'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'],
                                                    items[x]['ApplicationNumber'])
            items[x]['DepositorName'] = obj.getField('DepositorName').get(obj)
            items[x]['NumberOfPackages'] = obj.getField('NumberOfPackages').get(obj)
            items[x]['DepartureDate'] = obj.getField('DepartureDate').get(obj)
            items[x]['ArrivalDate'] = obj.getField('ArrivalDate').get(obj)

        return items

    def getStringified(self, elements):
        if not elements:
            return ''

        elements_list = []
        for element in elements:
            elements_list.append(element.title)

        elements_string = ', '.join(map(str, elements_list))
        return elements_string
