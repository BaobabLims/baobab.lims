from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.permissions import *


class KitsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(KitsView, self).__init__(context, request)
        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Kit',
            'sort_on': 'created',
            'sort_order': 'ascending'
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Kits"))
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/kit_big.png"
        self.description = ''

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Kit Name'),
                      'index': 'sortable_title'},
            'Project': {'title': _('Project'),
                            'toggle': True},
            'kitTemplate': {'title': _('Kit template'),
                            'toggle': True},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
                'transitions': [{'id': 'deactivate'},
                                # {'id': 'ship'}
                                ],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                ]
            },
            {
                'id': 'shipped',
                'title': _('Shipped'),
                'contentFilter': {'review_state': 'shipped',
                                  'sort_on': 'created',
                                  'sort_order': 'ascending'},
                'transitions': [{'id': 'deactivate'},
                                {'id': 'receive'}],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                ]
            },
            {
                'id': 'received',
                'title': _('Received'),
                'contentFilter': {'review_state': 'received',
                                  'sort_on': 'created',
                                  'sort_order': 'ascending'},
                'transitions': [{'id': 'deactivate'},
                                {'id': 'process'}],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                ]
            },
            {
                'id': 'processed',
                'title': _('Processed'),
                'contentFilter': {'review_state': 'processed',
                                  'sort_on': 'created',
                                  'sort_order': 'ascending'},
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                ]
            },
            {
                'id': 'all',
                'title': _('All'),
                'contentFilter': {'sort_on': 'created',
                                  'sort_order': 'ascending'},
                'columns': [
                    'Title',
                    'Project',
                    'kitTemplate',
                ]
            },
        ]

    def __call__(self):
        return super(KitsView, self).__call__()

    def folderitems(self):
        items = super(KitsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['kitTemplate'] = obj.getKitTemplate().Title()
            items[x]['Project'] = obj.getProject().Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                            (items[x]['url'], obj.title)
            items[x]['replace']['Project'] = \
                '<a href="%s">%s</a>' % (obj.getProject().absolute_url(),
                                         obj.getProject().Title())

        return items
