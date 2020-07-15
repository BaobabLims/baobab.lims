from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class HumanSampleRequestsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.catalog = 'portal_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'HumanSampleRequest',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=HumanSampleRequest',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Human Sample Requests"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'HumanSampleRequest':
            self.request.set('disable_border', 1)

        self.columns = {
            'Barcode': {
                'title': _('Barcode'),
                'input_width': '30'
            },
            'SampleType': {
                'title': _('Sample Type'),
                'input_width': '30'
            },
            'Volume': {
                'title': _('Volume'),
                'input_width': '10'
            },
            'Unit': {
                'title': _('Unit'),
                'input_width': '10'
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
                    'Barcode',
                    'SampleType',
                    'Volume',
                    'Unit',
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

            # items[x]['SubjectID'] = obj.getField('SubjectID').get(obj)

            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            items[x]['Barcode'] = obj.getField('Barcode').get(obj)

            items[x]['replace']['Barcode'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'],
                                                    items[x]['Barcode'])
            items[x]['SampleType'] = obj.getSampleType() and obj.getSampleType().Title() or ''
            items[x]['Volume'] = obj.getField('Volume').get(obj)
            items[x]['Unit'] = obj.getField('Unit').get(obj)
        return items