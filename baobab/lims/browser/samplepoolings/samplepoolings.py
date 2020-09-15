from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class SamplePoolingsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'SamplePooling',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=SamplePooling',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Sample Poolings"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/biospecimen_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'SamplePoolings':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {'title': _('Sample Shipment'),
                      'index': 'sortable_title'},
            'DateCreated': {
                'title': _('Samples'),
                'type': 'choices'
            },
            'Analyst': {
                'title': _('Analyst'),
            },
            'PoolingSamples': {
                'title': _('Pooling Samples'),
            },
            'ResultingSamples': {
                'title': _('Resulting Samples'),
            },
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'sort_on': 'sortable_title',
                    # 'sort_order': 'reverse'
                },
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'Title',
                    'DateCreated',
                    'Analyst',
                    'PoolingSamples',
                    'ResultingSamples',
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

            print(obj.absolute_url())
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'], obj.Title())
            items[x]['DateCreated'] = obj.getField('DateCreated').get(obj)
            items[x]['Analyst'] = obj.getField('Analyst').get(obj)

            items[x]['PoolingSamples'] = self.getStringified(obj.get_input_samples())
            items[x]['ResultingSamples'] = self.getStringified(obj.get_result_samples())

        return items



    # --------------------------------------------------------------------------
    def getStringified(self, elements):
        if not elements:
            return ''

        elements_list = []
        for element in elements:
            if element:
                # elements_list.append("<a href='%s'>%s</a>" % (element.absolute_url(), element.Title()))
                elements_list.append(element.Title())

        elements_string = ', '.join(map(str, elements_list))

        return elements_string