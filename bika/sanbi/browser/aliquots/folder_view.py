import json

from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from bika.lims.utils import isActive
from AccessControl import getSecurityManager

from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.permissions import *
from bika.sanbi.config import VOLUME_UNITS

class AliquotsView(BikaListingView):
    # template = ViewPageTemplateFile('templates/aliquots.pt')
    # table_template = ViewPageTemplateFile("templates/aliquots_table.pt")
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AliquotsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'Aliquot',
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
                'toggle': True
            },
            'Unit': {
                'title': _('Unit'),
                'toggle': True,
                'input_width': '10'
            },
            # 'Location': {'title': _('Location'),
            #              'toggle': True},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'sort_on': 'created',
                    'sort_order': 'reverse'
                },
                'transitions': [
                    {'id': 'store'}
                ],
                'columns': [
                    'Title',
                    'Biospecimen',
                    'AliquotType',
                    'Volume',
                    'Unit',
                    # 'Location'
                ]
            },
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        # if mtool.checkPermission(AddAliquot, self.context):
        #     self.context_actions[_('Add')] = {
        #         'url': 'createObject?type_name=Aliquot',
        #         'icon': '++resource++bika.lims.images/add.png'
        #     }

        if mtool.checkPermission(ManageAliquots, self.context):
            self.review_states[0]['transitions'].append({'id': 'deactivate'})
            self.review_states.append(
                {
                    'id': 'inactive',
                    'title': _('Dormant'),
                    'contentFilter': {
                        'inactive_state': 'inactive'
                    },
                    'transitions': [
                        {'id': 'activate'},
                    ],
                    'columns': [
                        'Title',
                        'Biospecimen',
                        'AliquotType',
                        'Volume',
                        'Unit',
                        # 'Location'
                    ]
                }
            )

            self.review_states.append(
                {
                    'id': 'all',
                    'title': _('All'),
                    'contentFilter': {},
                    'transitions': [
                        {'id': 'empty'}
                    ],
                    'columns': [
                        'Title',
                        'Biospecimen',
                        'AliquotType',
                        'Volume',
                        'Unit',
                        # 'Location'
                    ]
                }
            )

            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'

        return super(AliquotsView, self).__call__()

    def folderitems(self, full_objects=False):
        items = super(AliquotsView, self).folderitems()
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type='BiospecType', inactive_state='active')
        aliquot_types = [
            {
                'ResultValue': brain.UID,
                'ResultText': brain.title
            }
            for brain in brains
        ]
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Biospecimen'] = obj.getBiospecimen().Title()
            items[x]['AliquotType'] = obj.getAliquotType() and obj.getAliquotType().Title() or ''
            items[x]['Volume'] = obj.getVolume()
            items[x]['Unit'] = obj.getUnit()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

            if self.allow_edit and isActive(self.context) and \
                    getSecurityManager().checkPermission("Modify portal content", obj) and \
                            items[x]['inactive_state'] == "active":
                items[x]['allow_edit'] = ['AliquotType', 'Volume', 'Unit']
                items[x]['choices']['AliquotType'] = aliquot_types
                items[x]['choices']['Unit'] = VOLUME_UNITS

        return items

