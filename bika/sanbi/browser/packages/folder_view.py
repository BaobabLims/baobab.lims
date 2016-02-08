from Products.CMFCore.utils import getToolByName
from bika.sanbi import bikaMessageFactory as _
from zope.interface.declarations import implements
from bika.sanbi.permissions import *
from bika.lims.browser.bika_listing import BikaListingView

from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView

class PackagesView(BikaListingView):
    implements(IFolderContentsView, IViewView)
        
    def __init__(self, context, request):
        super(PackagesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'SupplyEx',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Packages"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/container_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'kitID': {'title': _('Kit ID'),
                      'index': 'sortable_title',
                      'toggle': True},
            'kitTemplate': {'title': _('Kit template'),
                       'toggle': True},
            'quantity': {'title': _('Quantity'),
                       'toggle': True},
            'expiryDate': {'title': _('Expiry Date'),
                       'toggle': False},
        }

        self.review_states = [
            {
                'id':'default',
                'title': _('All'),
                'contentFilter':{},
                'columns': ['kitID', 'kitTemplate', 'quantity', 'expiryDate']
            },
            {
                'id': 'pending',
                'title': _('Pending'),
                'contentFilter': {'review_state': 'pending'},
                #'transitions': [{'id':'complete'}, ],
                'columns': ['kitID', 'kitTemplate', 'quantity', 'expiryDate']
            },
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddSupplyEx, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=SupplyEx',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManagePackages, self.context):
            #self.review_states[0]['transitions'].append({'id':'deactivate'})
            self.review_states.append(
                {
                    'id':'completed',
                    'title': _('Completed'),
                     'contentFilter': {'review_state': 'completed'},
                     #'transitions': [{'id':'store'}, ],
                     'columns': ['kitID', 'kitTemplate', 'quantity', 'expiryDate']
                })
            self.review_states.append(
                {
                    'id':'stored',
                    'title': _('Stored'),
                     'contentFilter': {'review_state': 'stored'},
                     #'transitions': '',
                     'columns': ['kitID', 'kitTemplate', 'quantity', 'expiryDate']
                })
            #self.review_states.append() # remove it
            stat = self.request.get("%s_review_state"%self.form_id, 'default')
            self.show_select_column = stat != 'all'
        return super(PackagesView, self).__call__()

    def folderitems(self):
        items = super(PackagesView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['kitTemplate'] = obj.getKitTemplateTitle()
            items[x]['expiryDate'] = self.ulocalized_time(obj.getExpiryDate())
            items[x]['replace']['kitID'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], obj.getKitId())

        return items
