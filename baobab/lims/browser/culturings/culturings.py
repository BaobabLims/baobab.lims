from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class CulturingsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.catalog = 'portal_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Culturing',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=Culturing',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Culturings"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'Culturing':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {
                'title': _('Title'),
                # 'input_width': '10'
            },
            'ProductionBatchNumber': {
                'title': _('Production Batch Number'),
                # 'input_width': '10'
            },
            'BiobankNumber': {
                'title': _('Biobank Number'),
                # 'type': 'choices'
            },
            'DateCollectionRequest': {
                'title': _('Date of Collection Request'),
                # 'type': 'choices'
            },
            'Technician': {
                'title': _('Technician'),
                # 'input_width': '10'
            },
            'DateOfTesting': {
                'title': _('Date Of Testing'),
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
                    'Title',
                    'ProductionBatchNumber',
                    'BiobankNumber',
                    'DateCollectionRequest',
                    'Technician',
                    'DateOfTesting',
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

            items[x]['Title'] = obj.Title()

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'],
                                                    items[x]['Title'])
            items[x]['ProductionBatchNumber'] = obj.getField('ProductionBatchNumber').get(obj)
            items[x]['BiobankNumber'] = obj.getField('BiobankNumber').get(obj)
            items[x]['DateCollectionRequest'] = obj.getField('DateCollectionRequest').get(obj)
            items[x]['Technician'] = self.get_technician_details(obj)
            items[x]['DateOfTesting'] = obj.getField('DateOfTesting').get(obj)

        return items

    def get_technician_details(self, obj):
        try:
            return obj.getField('Technician').get(obj).Title()
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
