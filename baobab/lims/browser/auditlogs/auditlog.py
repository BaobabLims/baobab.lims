from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _
# from Products.CMFCore.utils import getToolByName


class AuditLogsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.contentFilter = {
            'portal_type': 'AuditLog',
            'sort_on': 'sortable_title',
            'sort_order': 'reverse'
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Audit Log"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"

        self.context = context
        self.catalog = 'portal_catalog'
        request.set('disable_plone.rightcolumn', 1)

        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'AuditLogs':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title',
                'input_width': '10',
            },
            'AuditDate': {
                'title': _('Audit Date'),
                'input_width': '18'
            },
            'AuditUser': {
                'title': _('Audit User'),
                'input_width': '30'
            },
            'ItemType': {
                'title': _('Item Type'),
                'input_width': '30',
            },
            'ItemTitle': {
                'title': _('Item Title'),
                'input_width': '30',
            },
            'ItemUID': {
                'title': _('Item UID'),
                'input_width': '30',
            },
            'ChangedValue': {
                'title': _('Change'),
                'input_width': '30',
            },
            'OldValue': {
                'title': _('Old Value'),
                'input_width': '30',
            },
            'NewValue': {
                'title': _('New Value'),
                'input_width': '30',
            },
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'sort_on': 'sortable_title',
                    # 'sort_order': 'reverse'
                },
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'Title',
                    'AuditDate',
                    'AuditUser',
                    'ItemType',
                    'ItemTitle',
                    'ItemUID',
                    'ChangedValue',
                    'OldValue',
                    'NewValue',
                ]
            }
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(AddPortalContent, self.context):
            self.show_select_row = True
            self.show_select_column = True

        return BikaListingView.__call__(self)

    def folderitems(self, full_objects=False):

        #
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            return []

        member = membership.getAuthenticatedMember()
        if member.getUserName() != 'admin' and 'LabManagers' not in member.getGroups():
            # print('--------member')
            # print(member.getUserName())
            # print(member.getGroups())
            return []

        items = BikaListingView.folderitems(self)
        reversed_items = []

        for x in range(len(items)):

            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            items[x]['Title'] = obj.Title()
            items[x]['AuditDate'] = obj.getField('AuditDate').get(obj)
            items[x]['AuditUser'] = obj.getField('AuditUser').get(obj)
            items[x]['ItemType'] = obj.getField('ItemType').get(obj)
            items[x]['ItemTitle'] = obj.getField('ItemTitle').get(obj)
            items[x]['ItemUID'] = obj.getField('ItemUID').get(obj)
            items[x]['ChangedValue'] = obj.getField('ChangedValue').get(obj)
            items[x]['OldValue'] = obj.getField('OldValue').get(obj)
            items[x]['NewValue'] = obj.getField('NewValue').get(obj)
            # items[x][''] = obj.getField('').get(obj)
            reversed_items.insert(0, items[x])
        return reversed_items
