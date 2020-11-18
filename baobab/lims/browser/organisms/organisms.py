from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class OrganismsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Organism',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=Organism',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Organism"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'Organisms':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {
                'title': _('Organism'),
                'index': 'sortable_title'
            },
            'Genus': {
                'title': _('Genus'),
                'index': 'sortable_title'
            },
            'Species': {
                'title': _('Species'),
                'index': 'sortable_title'
            },
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
                'transitions': [{'id':'deactivate'},],
                'columns': [
                    'Title',
                    'Genus',
                    'Species',
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

        for x in range(len(items)):

            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            # items[x]['Description'] = items[x]
            items[x]['Genus'] = obj.getField('Genus').get(obj)
            items[x]['Species'] = obj.getField('Species').get(obj)

        return items
