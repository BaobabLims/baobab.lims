from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class SampleShipmentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'SampleShipment',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=SampleShipment',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("SampleShipments"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/biospecimen_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'SampleShipments':
            self.request.set('disable_border', 1)

        self.columns = {
            'SampleShipmentID': {
                'title': _('SampleShipmentID'),
                'input_width': '10'
            },
            'SamplesList': {
                'title': _('Samples'),
                'type': 'choices'
            },
            'Client': {
                'title': _('Client'),
                'type': 'choices'
            },
            # 'CaseControl': {
            #     'title': _('Type'),
            #     'input_width': '20'
            # },
            # 'Sex': {
            #     'title': _('Sex'),
            #     'type': 'choices'
            # },
            # 'Age': {
            #     'title': _('Age'),
            #     'input_width': '10'
            # },
            # 'AgeUnit': {
            #     'title': _('Age Unit'),
            #     'type': 'choices'
            # },
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
                'transitions': [
                ],
                'columns': [
                    'SampleShipmentID',
                    'SamplesList',
                    'Client',
                    # 'Sex',
                    # 'Age',
                    # 'DiseasesList',
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
        # print len(items)
        # print '----------'
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['SampleShipmentID'] = obj.getId()

            items[x]['replace']['SampleShipmentID'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'], obj.getId())

            client = obj.getClient()
            if client:
                items[x]['Client'] = client.Title()

            #items[x]['Age'] = ('%f' % float(obj.getAge())).rstrip('0').rstrip('.') + " " + obj.getAgeUnit()
            items[x]['SamplesList'] = self.getStringified(obj.getSamplesList())

        return items

    # --------------------------------------------------------------------------
    def getStringified(self, elements):
        if not elements:
            return ''

        elements_list = []
        for element in elements:
            elements_list.append(element.title)

        elements_string = ', '.join(map(str, elements_list))

        return elements_string