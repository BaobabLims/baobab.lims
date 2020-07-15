from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class CollectionRequestsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.catalog = 'portal_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'CollectionRequest',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=CollectionRequest',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Collection Requests"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'CollectionRequest':
            self.request.set('disable_border', 1)

        self.columns = {
            'RequestNumber': {
                'title': _('RequestNumber'),
                'input_width': '10'
            },
            'Client': {
                'title': _('Client'),
                'input_width': '20'
            },
            'DateOfRequest': {
                'title': _('Date Of Request'),
                'input_width': '10'
            },
            'DateEvaluated': {
                'title': _('Date Evaluated'),
                'input_width': '10'
            },
            'ResultOfEvaluation': {
                'title': _('Result Of Evaluation'),
                'input_width': '10'
            }
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
                    'RequestNumber',
                    'Client',
                    'ResultOfEvaluation',
                    'DateOfRequest',
                    'DateEvaluated',
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

            if 'RequestNumber' in items[x] and items[x]['RequestNumber']:
                items[x]['replace']['RequestNumber'] = "<a href='%s'>%s</a>" % \
                    (items[x]['url'], items[x]['RequestNumber'])
            else:
                items[x]['RequestNumber'] = obj.getId()
                items[x]['replace']['RequestNumber'] = "<a href='%s'>%s</a>" % \
                                                       (items[x]['url'], items[x]['RequestNumber'])

            items[x]['DateOfRequest'] = obj.getField('DateOfRequest').get(obj)
            items[x]['DateEvaluated'] = obj.getField('DateEvaluated').get(obj)
            items[x]['ResultOfEvaluation'] = obj.getField('ResultOfEvaluation').get(obj)

            client = obj.getClient()
            print(client)
            if client and hasattr(client, 'title'):
                items[x]['Client'] = client.Title()

        return items

    def getStringified(self, elements):
        if not elements:
            return ''

        elements_list = []
        for element in elements:
            elements_list.append(element.title)

        elements_string = ', '.join(map(str, elements_list))
        return elements_string
