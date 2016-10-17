from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from bika.lims.utils import isActive
from AccessControl import getSecurityManager
from bika.sanbi.config import VOLUME_UNITS
from bika.sanbi.permissions import ManageAliquots, AddProject


class BiospecimensView(BikaListingView):
    # template = ViewPageTemplateFile('templates/biospecimens.pt')
    # table_template = ViewPageTemplateFile("templates/biospecimens_table.pt")
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(BiospecimensView, self).__init__(context, request)
        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Biospecimen',
            'sort_on': 'created',
            'sort_order': 'ascending'
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Biospecimen"))
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/biospecimen_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'Biospecimens':
            self.request.set('disable_border', 1)
            
        self.columns = {
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title'
            },
            'Type': {
                'title': _('Type'),
                'toggle': True,
                'type': 'choices'
            },
            'Volume': {
                'title': _('Volume'),
                'toggle': True,
                'input_width': '7'
            },
            'Unit': {
                'title': _('Unit'),
                'toggle': True
            },
            'SubjectID': {
                'title': _('Subject ID'),
                'allow_edit': True,
                'input_class': 'text',
                'input_width': '10',
                'toggle': True
            },
            'Kit': {
                'title': _('Kit'),
                'index': 'sortable_title'
            },
            'Barcode': {
                'title': _('Barcode'),
                'allow_edit': True,
                'input_class': 'text',
                'input_width': '10',
                'toggle': True
            },
            'Project': {
                'title': _('Project'),
                'index': 'sortable_title'
            },
            # 'Location': {
            #     'title': _('Location'),
            #     'toggle': True
            # },
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'sort_on': 'created',
                    'sort_order': 'ascending'
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'complete_biospecimen'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'Kit',
                    'Type',
                    'SubjectID',
                    'Barcode',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            },

            {
                'id': 'completed',
                'title': _('Completed'),
                'contentFilter': {
                    'review_state': 'completed',
                    'sort_on': 'created',
                    'sort_order': 'reverse'
                },
                'transitions': [
                    {'id': 'deactivate'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'Kit',
                    'Type',
                    'SubjectID',
                    'Barcode',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            },

            {
                'id': 'inactive',
                'title': _('Deactivated'),
                'contentFilter': {
                    'inactive_state': 'inactive',
                    'sort_on': 'created',
                    'sort_order': 'ascending'
                },
                'transitions': [
                    {'id': 'activate'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'Kit',
                    'Type',
                    'SubjectID',
                    'Barcode',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            },

            {
                'id': 'all',
                'title': _('All'),
                'contentFilter': {
                    'sort_on': 'created',
                    'sort_order': 'ascending'
                },
                'columns': [
                    'Title',
                    'Project',
                    'Kit',
                    'Type',
                    'SubjectID',
                    'Barcode',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            },
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(AddProject, self.context):
            self.show_select_row = True
            self.show_select_column = True

        return super(BiospecimensView, self).__call__()

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type='BiospecType', inactive_state='active')
        biospecimen_types = [
            {
                'ResultValue': brain.UID,
                'ResultText': brain.title
            }
            for brain in brains
        ]
        for x, item in enumerate(items):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Type'] = obj.getType() and obj.getType().Title() or ''
            items[x]['Volume'] = obj.getVolume()
            items[x]['Unit'] = VOLUME_UNITS[0]['ResultText']
            items[x]['SubjectID'] = obj.getSubjectID()
            items[x]['Kit'] = obj.getKit()
            items[x]['Project'] = obj.getKit().aq_parent
            if obj.getKit():
                items[x]['replace']['Kit'] = \
                    '<a href="%s">%s</a>' % (obj.getKit().absolute_url(), obj.getKit().Title())
                items[x]['replace']['Project'] = \
                    '<a href="%s">%s</a>' % (obj.getKit().aq_parent.absolute_url(),
                                             obj.getKit().aq_parent.Title())
            items[x]['Barcode'] = obj.getBarcode()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            # items[x]['choices']['Type'] = biospecimen_types
            # TODO: SPECIFY OBJ STATES WHERE USER CAN EDIT BARCODE
            if self.allow_edit and isActive(self.context) and \
                   getSecurityManager().checkPermission(ManageAliquots, obj) and \
                   items[x]['review_state'] == "to_complete":
                items[x]['allow_edit'] = ['Type', 'SubjectID', 'Barcode', 'Volume', 'Unit']
                items[x]['choices']['Type'] = biospecimen_types
                items[x]['choices']['Unit'] = VOLUME_UNITS

        return items
