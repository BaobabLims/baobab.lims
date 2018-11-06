from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims import bikaMessageFactory as _


class BatchesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'SampleBatch',
            'sort_on': 'sortable_title',
            'sort_order': 'ascending'
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Biospecimen Batches"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/biospectype_big.png"
        #self.contrifugation_date = context.getCfgDateTime().strftime("%Y/%m/%d %H:%M")
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        self.columns = {
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title'
            },
            'Project': {
                'title': _('Project'),
                'index': 'sortable_title'
            },
            'ParentBiospecimen': {
                'title': _('Parent ID'),
                # 'index': 'sortable_title'
            },
            'BatchType': {
                'title': _('Batch Type'),
                'toggle': True,
            },
            'SerumColour': {
                'title': _('Colour'),
            },
            'ContrifugationDate': {
                'title': _('Centrifuge/Formalin Start Time'),
                'toggle': True,
            }
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {'inactive_state': 'active'},
                'transitions': [],
                'columns': [
                    'Title',
                    'Project',
                    'ParentBiospecimen',
                    'BatchType',
                    'ContrifugationDate',
                    'SerumColour',

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
                    'ParentBiospecimen',
                    'BatchType',
                    'ContrifugationDate',
                    'SerumColour',
                ]
            },
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(AddPortalContent, self.context):
            self.show_select_row = True
            self.show_select_column = True
            self.context_actions = {
                _('Add'): {
                    'url': 'createObject?type_name=SampleBatch',
                    'icon': '++resource++bika.lims.images/add.png'
                }
            }

        return BikaListingView.__call__(self)

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self)
        ret = []
        for x, item in enumerate(items):
            if not items[x].has_key('obj'):
                continue
            obj = item['obj']
            # item['BatchType'] = obj.getBatchType()
            item['BatchType'] = obj.getField('BatchType').get(obj)
            item['replace']['Title'] = \
                "<a href='%s'>%s</a>" % (item['url'], item['Title'])
            try:
                parent_title = obj.getParentBiospecimen().Title()
            except Exception as e:
                parent_title = ''
            item['ParentBiospecimen'] = parent_title
            item['Project'] = obj.getField('Project').get(obj).Title()
            item['SerumColour'] = obj.getField('SerumColour').get(obj)
            # item['ContrifugationDate'] = obj.CfgDateTime().strftime("%Y/%m/%d %H:%M")
            item['ContrifugationDate'] = obj.getField('CfgDateTime').get(obj)
            ret.append(item)
        return ret
