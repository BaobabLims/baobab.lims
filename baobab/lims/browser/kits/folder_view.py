from AccessControl import getSecurityManager
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims import bikaMessageFactory as _
from baobab.lims.permissions import ManageKits


class KitsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Kit',
            'sort_on': 'sortable_title',
            'sort_order': 'reverse'
        }
        # Todo: I added these two line to set the sort and the order of kit listing because
        # Todo: the values in self.contentFilter seems have no effect!
        self.sort_on = 'sortable_title'
        self.request.set('list_sort_order', 'reverse')

        self.context_actions = {}
        self.title = self.context.translate(_("Kits"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/kit_big.png"
        self.description = ''

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25

        if self.context.portal_type == 'Kits':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {'title': _('Kit Name')},
            'Project': {'title': _('Project'),
                            'toggle': True},
            'kitTemplate': {'title': _('Kit template'),
                            'toggle': True},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
            'sortable_title':{}
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'receive_kit'},
                    {'id': 'process'},
                    # {'id': 'ship'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                    'state_title'
                ]
            },
            {
                'id': 'shipped',
                'title': _('Shipped'),
                'contentFilter': {
                    'review_state': 'shipped',
                    'sort_on': 'sortable_title',
                    'sort_order': 'reverse'
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'receive_kit'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                    'state_title'
                ]
            },
            {
                'id': 'received',
                'title': _('Received'),
                'contentFilter': {
                    'review_state': 'received',
                    'sort_on': 'sortable_title',
                    'sort_order': 'reverse'
                },
                'transitions': [
                    {'id': 'deactivate'},
                    {'id': 'process'}
                ],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                    'state_title'
                ]
            },
            {
                'id': 'processed',
                'title': _('Processed'),
                'contentFilter': {
                    'review_state': 'processed',
                    'sort_on': 'sortable_title',
                    'sort_order': 'reverse'
                },
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                    'state_title'
                ]
            },
            {
                'id': 'all',
                'title': _('All'),
                'contentFilter': {
                    'sort_on': 'sortable_title',
                    'sort_order': 'reverse'
                },
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                    'state_title'
                ]
            },
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(ManageKits, self.context):
            self.show_select_row = True
            self.show_select_column = True
        return BikaListingView.__call__(self)

    def folderitems(self):
        items = super(KitsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['kitTemplate'] = obj.getKitTemplate() and obj.getKitTemplate().Title() or ''
            items[x]['Project'] = ''
            if obj.aq_parent.portal_type == 'Project':
                items[x]['Project'] = obj.aq_parent.Title()
                items[x]['replace']['Project'] = \
                    '<a href="%s">%s</a>' % (obj.aq_parent.absolute_url(),
                                             obj.aq_parent.Title())

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                            (items[x]['url'], obj.title)


        return items
