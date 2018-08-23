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
import time


class BiospecimensView(BikaListingView):

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
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
            'DateReceived': {
                'title': _('Date Received'),
                #'index': 'review_state'
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
                    'state_title',
                    'DateReceived',
                    # 'Location'
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
                    'state_title',
                    'DateReceived',
                    # 'Location'
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
                    {'id': 'cancel'},
                    {'id': 'dispose'}
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
                    'state_title',
                    'DateReceived',
                    # 'Location'
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
                    {'id': 'cancel'},
                    {'id': 'dispose'}
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
                    'state_title',
                    'DateReceived',
                    # 'Location'
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
                    'state_title',
                    'DateReceived',
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
                    'DateReceived',
                    # 'Location'
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
            #get the sample type


            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            if not ISample.providedBy(obj):
                continue

            items[x]['Type'] = obj.getSampleType() and obj.getSampleType().Title() or ''
            insufficient_volume, volume = self.get_insufficient_volume(obj, items[x]['review_state'])

            if insufficient_volume:
                items[x]['replace']['Volume'] = volume
            else:
                items[x]['Volume'] = volume

            # try:
            #     sample_type = obj.getSampleType()
            #     if float(obj.getField('Volume').get(obj)) < float(sample_type.getMinimumVolume().split()[0])\
            #             and items[x]['review_state'] == "sample_received":
            #         items[x]['replace']['Volume'] = \
            #             '<span title="less than %s" style="color:red">%s</span>' % (str(sample_type.getMinimumVolume()), obj.getField('Volume').get(obj))
            #     else:
            #         items[x]['Volume'] = obj.getField('Volume').get(obj)
            #
            # except Exception as e:
            #     items[x]['Volume'] = obj.getField('Volume').get(obj)



            # items[x]['Unit'] = VOLUME_UNITS[0]['ResultText']
            items[x]['Unit'] = obj.getField('Unit').get(obj)
            items[x]['SubjectID'] = obj.getField('SubjectID').get(obj)
            items[x]['DateReceived'] = str(obj.getField('DateReceived').get(obj))[:16]
            # if items[x]['DateReceived']:
            #     print('Not date received')
            #     items[x]['DateReceived'] = ''
            kit = obj.getField('Kit').get(obj)
            project = obj.getField('Project').get(obj)
            items[x]['Kit'] = kit
            items[x]['Project'] = project

            if project:
                items[x]['replace']['Project'] = \
                    '<a href="%s">%s</a>' % (project.absolute_url(),
                                             project.Title())
            if kit:
                items[x]['replace']['Kit'] = \
                    '<a href="%s">%s</a>' % (kit.absolute_url(), kit.Title())

                # TODO: IF STATUS IS RECEIVED EXECUTE THIS
                # items[x]['replace']['Type'] = \
                #     '<a href="%s">%s</a>' % (obj.getSampleType().absolute_url(),
                #                              obj.getSampleType().Title())
            items[x]['Barcode'] = obj.getField('Barcode').get(obj)
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            # TODO: SPECIFY OBJ STATES WHERE USER CAN EDIT BARCODE
            if self.allow_edit and isActive(self.context) and \
                    getSecurityManager().checkPermission(ModifyPortalContent, obj):
                if items[x]['review_state'] == "sample_registered":
                    items[x]['allow_edit'] = ['Type', 'Barcode']
                    items[x]['choices']['Type'] = biospecimen_types
                elif items[x]['review_state'] == "sample_due":
                    items[x]['allow_edit'] = ['SubjectID', 'Volume', 'Unit',]

                    if not items[x]['Unit']:
                        items[x]['choices']['Unit'] = VOLUME_UNITS
            ret.append(item)

        return ret

    def get_insufficient_volume(self, obj, review_state):
        """
        This function determines whether or not the sample volume is less than the minimum allowed volume.
        If it is it returns True plus a highligted version of the sample volume.  Otherwise it returns False
        along with unhighligted volume
        :param obj:
        :param review_state:
        :return:
        """

        try:
            # print('-------')
            # print(obj)

            sample_type = obj.getSampleType()
            sample_type_unit = sample_type.getMinimumVolume().split()[1]
            minimum_volume = sample_type.getMinimumVolume().split()[0]
            sample_unit = obj.getField('Unit').get(obj)
            sample_volume = obj.getField('Volume').get(obj)

            # check to see if both units are measuring the same thing
            if not (set([sample_unit, sample_type_unit]).issubset(['g', 'mg', 'ug', 'g', 'mg', 'ug']) \
                    or set([sample_unit, sample_type_unit]).issubset(['ml', 'ul', 'ml', 'ul'])):
                return True, '<span title="Sample and sample type units differ (%s and %s)." style="color:orange">%s</span>' % (sample_unit, sample_type_unit, sample_volume)

            if review_state != "sample_received":
                return False, sample_volume

            converted_minimum_volume = self.convert_units(minimum_volume, sample_type_unit)

            converted_sample_volume = self.convert_units(sample_volume, sample_unit)

            if converted_sample_volume < converted_minimum_volume:
                return True, '<span title="less than %s %s" style="color:red">%s</span>' % (str(minimum_volume), sample_type_unit, sample_volume)
            return False, sample_volume

        except Exception as e:
            return False, sample_volume

    def convert_units(self, volume, unit):
        """
        This function will:
         take gram, milligram, microgram and convert it to gram
         take ml, ul and convert it to ml
        :param volume:
        :param unit:
        :return: gram or ml
        """

        if unit in ('g', 'ml'):
            return float(volume) / 1.0

        if unit in ('mg', 'ul'):
            return float(volume) / 1000.0

        if unit in ('ug'):
            return float(volume) / 1000000.0
