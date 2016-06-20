from Products.CMFCore.utils import getToolByName
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.permissions import *
from bika.lims.browser.bika_listing import BikaListingView


class AliquotsView(BikaListingView):
    def __init__(self, context, request):
        super(AliquotsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Aliquot',
                              'sort_on': 'sortable_title'}

        self.context_actions = {}
        self.title = self.context.translate(_("Samples"))
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/sample_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'Title': {'title': _('Sample'),
                      'index': 'sortable_title'},
            'Biospecimen': {'title': _('Biospecimen'),
                            'toggle': True},
            'SubjectID': {'title': _('Subject ID'),
                          'toggle': True},
            'SampleType': {'title': _('Sample Type'),
                           'toggle': True},
            'Volume': {'title': _('Volume'),
                           'toggle': True},
            'Quantity': {'title': _('Quantity'),
                           'toggle': True},
            'Location': {'title': _('Location'),
                           'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Pending'),
             'contentFilter': {'inactive_state': 'active',
                               'review_state': 'pending',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'store'}],
             'columns': ['Title',
                         'Biospecimen',
                         'SubjectID',
                         'SampleType',
                         'Quantity',
                         'Volume',
                         'Location']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddAliquot, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Aliquot',
                'icon': '++resource++bika.lims.images/add.png'
            }

        if mtool.checkPermission(ManageAliquots, self.context):
            self.review_states[0]['transitions'].append({'id': 'deactivate'})
            self.review_states.append(
                {'id': 'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id': 'activate'}, ],
                 'columns': ['Title',
                             'Biospecimen',
                             'SubjectID',
                             'SampleType',
                             'Quantity',
                             'Volume',
                             'Location']})

            self.review_states.append(
                {'id': 'stored',
                 'title': _('Stored'),
                 'contentFilter': {'review_state': 'stored',
                                   'sort_on': 'created',
                                   'sort_order': 'reverse'},
                 'transitions': [{'id': 'pend'},
                                 {'id': 'deactivate'}],
                 'columns': ['Title',
                             'Biospecimen',
                             'SubjectID',
                             'SampleType',
                             'Quantity',
                             'Volume',
                             'Location']})

            self.review_states.append(
                {'id': 'all',
                 'title': _('All'),
                 'contentFilter': {},
                 'transitions': [{'id': 'empty'}],
                 'columns': ['Title',
                             'Biospecimen',
                             'SubjectID',
                             'SampleType',
                             'Quantity',
                             'Volume',
                             'Location']})

            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'
        return super(AliquotsView, self).__call__()

    def folderitems(self):
        items = super(AliquotsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Biospecimen'] = obj.getBiospecimen().Title()
            items[x]['SubjectID'] = obj.getSubjectID()
            items[x]['SampleType'] = obj.getSampleType().Title()
            items[x]['Quantity'] = obj.getQuantity()
            items[x]['Volume'] = obj.getVolume()
            items[x]['Location'] = obj.getStorageLocation() and obj.getStorageLocation().Title() or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

        return items
