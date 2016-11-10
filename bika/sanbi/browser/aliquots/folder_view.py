import json

from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from bika.lims.utils import isActive
from AccessControl import getSecurityManager

from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IAliquot
from bika.sanbi.permissions import *
from bika.sanbi.config import VOLUME_UNITS

class AliquotsView(BikaListingView):

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AliquotsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on': 'sortable_title'}

        self.context_actions = {}
        self.title = self.context.translate(_("Aliquots"))
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/aliquot_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50
        request.set('disable_plone.rightcolumn', 1)
        self.allow_edit = True

        if self.context.portal_type == 'Aliquots':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {
                'title': _('Aliquot'),
                'index': 'sortable_title'
            },
            'Biospecimen': {
                'title': _('Biospecimen'),
                'toggle': True
            },
            'AliquotType': {
                'title': _('Aliquot Type'),
                'toggle': True
            },
            'Volume': {
                'title': _('Volume'),
                'toggle': True,
                'input_width': '7'
            },
            'Unit': {
                'title': _('Unit'),
                'toggle': True,
                'input_width': '15'
            },
            'Project': {
                'title': _('Project'),
                'index': 'sortable_title'
            },
            'state_title': {
                'title': _('State'),
                'index': 'review_state'
            },
            # 'Location': {'title': _('Location'),
            #              'toggle': True},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'cancellation_state': 'active',
                    'sort_on': 'created',
                    'sort_order': 'ascending'
                },
                'transitions': [
                    {'id': 'cancel'},
                    {'id': 'receive'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'Biospecimen',
                    'AliquotType',
                    'Volume',
                    'Unit',
                    'state_title',
                    # 'Location'
                ]
            },
            {
                'id': 'completed',
                'title': _('Completed'),
                'contentFilter': {
                    'review_state': 'completed'
                },
                'transitions': [
                    {'id': 'deactivate'},
                ],
                'columns': [
                    'Title',
                    'Project',
                    'Biospecimen',
                    'AliquotType',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            },
            {
                'id': 'inactive',
                'title': _('Deactivated'),
                'contentFilter': {
                    'inactive_state': 'inactive'
                },
                'transitions': [
                    {'id': 'activate'},
                ],
                'columns': [
                    'Title',
                    'Project',
                    'Biospecimen',
                    'AliquotType',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            },
            {
                'id': 'all',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'Title',
                    'Project',
                    'Biospecimen',
                    'AliquotType',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            }
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(ManageAliquots, self.context):
            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'

        return super(AliquotsView, self).__call__()

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type='SampleType', inactive_state='active')
        aliquot_types = [
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
            if not IAliquot.providedBy(obj):
                continue
            items[x]['Biospecimen'] = obj.getLinkedSample().Title()
            items[x]['AliquotType'] = obj.getSampleType() and obj.getSampleType().Title() or ''
            items[x]['Volume'] = items[x]['Volume'] = obj.getField('Volume').get(obj)
            items[x]['Unit'] = VOLUME_UNITS[0]['ResultText']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            if self.context.portal_type == 'Aliquots':
                items[x]['replace']['Project'] = \
                    '<a href="%s">%s</a>' % (obj.aq_parent.absolute_url(),
                                             obj.aq_parent.Title())

            if self.allow_edit and isActive(self.context) and \
                    getSecurityManager().checkPermission("Modify portal content", obj) and \
                    items[x]['review_state'] == "sample_due":
                items[x]['allow_edit'] = ['AliquotType', 'Volume', 'Unit']
                items[x]['choices']['AliquotType'] = aliquot_types
                items[x]['choices']['Unit'] = VOLUME_UNITS
            ret.append(item)

        return ret

