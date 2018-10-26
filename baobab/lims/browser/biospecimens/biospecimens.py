from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import isActive
from bika.lims.interfaces import ISample
from baobab.lims.interfaces import ISharableSample

from baobab.lims.config import VOLUME_UNITS
from baobab.lims import bikaMessageFactory as _


class BiospecimensView(BikaListingView):
    """
    Class showing list of biospecimens in a table
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request, content_type=None):
        BikaListingView.__init__(self, context, request)
        self.context = context
        # self.catalog = 'bika_catalog'
        self.catalog = 'portal_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Sample',
            'sort_on': 'sortable_title',
            'sort_order': 'ascending'
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Biospecimens"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/biospecimen_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.allow_edit = True
        self.content_type = content_type
        if self.content_type == 'batch':
            self.pagesize = 1000
        else:
            self.pagesize = 25

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
                'allow_edit': True,
                'input_class': 'text',
                'input_width': '5',
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
            'state_title': {
                'title': _('State'),
                'index': 'review_state'
            },
            'FrozenTime': {
                'title': _('Frozen Time'),
                # 'index': 'review_state'
            },
            'StorageLocation': {
                'title': _('Storage'),
                'toggle': True
            },
            'CFGTime': {
                'title': _('Centrifuge Time'),
                'toggle': True
            },

            'SamplingTime': {
                'title': _('Sampling Time'),
                'toggle': True
            },
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'cancellation_state': 'active',
                    'sort_on': 'sortable_title',
                    'sort_order': 'ascending'
                },
                'transitions': [
                    {'id': 'receive'},
                    {'id': 'sample_due'},
                    {'id': 'cancel'}
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
                    'StorageLocation',
                    'CFGTime',
                    'FrozenTime',
                    'SamplingTime',
                    'state_title',
                ]
            },

            {
                'id': 'sample_registered',
                'title': _('Sample Registered'),
                'contentFilter': {
                    'review_state': 'sample_registered',
                    'cancellation_state': 'active',
                    'sort_on': 'created',
                    'sort_order': 'ascending'
                },
                'transitions': [
                    {'id': 'sample_due'},
                    {'id': 'cancel'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'Kit',
                    'Type',
                    'Barcode',
                    'StorageLocation',
                    'CFGTime',
                    'FrozenTime',
                    'SamplingTime',
                    'state_title',
                ]
            },
            {
                'id': 'sample_due',
                'title': _('Sample Due'),
                'contentFilter': {
                    'review_state': 'sample_due',
                    'cancellation_state': 'active',
                    'sort_on': 'created',
                    'sort_order': 'ascending'
                },
                'transitions': [
                    {'id': 'receive'},
                    {'id': 'cancel'}
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
                    'StorageLocation',
                    'CFGTime',
                    'FrozenTime',
                    'SamplingTime',
                    'state_title',
                ]
            },
            {
                'id': 'sample_shipped',
                'title': _('Sample Shipped'),
                'contentFilter': {
                    'review_state': 'sample_shipped',
                    'cancellation_state': 'active',
                    'sort_on': 'created',
                    'sort_order': 'ascending'
                },
                'transitions': [
                    {'id': 'receive'}
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
                    'StorageLocation',
                    'CFGTime',
                    'FrozenTime',
                    'SamplingTime',
                    'state_title',
                ]
            },
            {
                'id': 'sample_received',
                'title': _('Received'),
                'contentFilter': {
                    'review_state': 'sample_received',
                    'sort_on': 'created',
                    'sort_order': 'reverse'
                },
                'transitions': [
                    {'id': 'cancel'}
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
                    'StorageLocation',
                    'CFGTime',
                    'FrozenTime',
                    'SamplingTime',
                    'state_title',
                ]
            },

            {
                'id': 'cancelled',
                'title': _('Cancelled'),
                'contentFilter':{
                    'cancellation_state': 'cancelled',
                    'sort_order': 'reverse',
                    'sort_on':'created'
                },
                'transitions': [
                    {'id': 'reinstate'},
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
                    'StorageLocation',
                    'CFGTime',
                    'FrozenTime',
                    'SamplingTime',
                    'state_title',
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
                    'StorageLocation',
                    'CFGTime',
                    'FrozenTime',
                    'SamplingTime',
                    'state_title',
                ]
            },
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(AddPortalContent, self.context):
            self.show_select_row = True
            self.show_select_column = True
            self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=Sample',
                                     'icon': '++resource++bika.lims.images/add.png'}}

        return BikaListingView.__call__(self)

    def folderitems(self, full_objects=False):
        # Show only ISharable samples for EMS.  Skip others.
        pm = getToolByName(self.context, 'portal_membership')
        roles = pm.getAuthenticatedMember().getRoles()

        #print roles
        if 'EMS' in roles:
            self.contentFilter['object_provides'] = ISharableSample.__identifier__

        items = BikaListingView.folderitems(self)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type='SampleType', inactive_state='active')
        biospecimen_types = [
            {
                'ResultValue': brain.UID,
                'ResultText': brain.title
            }
            for brain in brains
            ]
        ret = []
        for x, item in enumerate(items):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            if not ISample.providedBy(obj):
                continue
            items[x]['Type'] = obj.getSampleType() and obj.getSampleType().Title() or ''
            items[x]['Volume'] = obj.getField('Volume').get(obj)
            items[x]['Unit'] = obj.getField('Unit').get(obj)
            items[x]['SubjectID'] = obj.getField('SubjectID').get(obj)
            kit = obj.getField('Kit').get(obj)
            project = obj.getField('Project').get(obj)
            items[x]['Kit'] = kit
            items[x]['Project'] = project
            storage_location = obj.getField('StorageLocation').get(obj)
            if storage_location:
                items[x]['StorageLocation'] = storage_location.Title()
            if project:
                items[x]['replace']['Project'] = \
                    '<a href="%s">%s</a>' % (project.absolute_url(),
                                             project.Title())
            if kit:
                items[x]['replace']['Kit'] = \
                    '<a href="%s">%s</a>' % (kit.absolute_url(), kit.Title())


            items[x]['Barcode'] = obj.getField('Barcode').get(obj)
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            frozen_time = obj.getField('FrozenTime').get(obj)
            if frozen_time:
                items[x]['FrozenTime'] = frozen_time.strftime("%Y%m%d %H:%M")
                # items[x]['FrozenTime'] = frozen_time.strftime("%Y%m%d %H:%M:%S")

            batch = obj.getField('Batch').get(obj)

            try:
                items[x]['CFGTime'] = batch.getField('CfgDateTime').get(batch)
            except:
                items[x]['CFGTime'] = ''

            items[x]['SamplingTime'] = obj.getField('SamplingDate').get(obj)

            if self.allow_edit and isActive(self.context) and \
                    getSecurityManager().checkPermission(ModifyPortalContent, obj):
                if items[x]['review_state'] == "sample_registered":
                    items[x]['allow_edit'] = ['Type', 'Barcode', 'FrozenTime']
                    items[x]['choices']['Type'] = biospecimen_types
                elif items[x]['review_state'] == "sample_due":
                    items[x]['allow_edit'] = ['SubjectID', 'Volume', 'Unit']

                    if not items[x]['Unit']:
                        items[x]['choices']['Unit'] = VOLUME_UNITS
                elif items[x]['review_state'] == "sample_shipped":
                    items[x]['allow_edit'] = ['SubjectID', 'Volume']

            ret.append(item)
        return ret
