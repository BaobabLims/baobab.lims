from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims import bikaMessageFactory as _


class CentrifugationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context = context
        self.catalog = 'portal_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Centrifugation',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=Centrifugation',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Centrifugations"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/biospecimen_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'Centrifugations':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {
                'title': _('Centrifugations'),
                'index': 'sortable_title'
            },
            'DateCreated': {
                'title': _('Date Create'),
            },
            'SelectedSample': {
                'title': _('Selected Sample'),
            },
            'Analyst': {
                'title': _('Analyst'),
            },
            'Centrifuges': {
                'title': _('Centrifuges'),
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
                    'SelectedSample',
                    'Analyst',
                    'Centrifuges',
                ]
            }
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(AddPortalContent, self.context):
            self.show_select_row = True
            self.show_select_column = True

        return BikaListingView.__call__(self)

    def folderitems(self, full_objects=False):
        print('------Inside the list of Centrifugations')
        items = BikaListingView.folderitems(self)
        print(items)

        for x in range(len(items)):
            print(x)
            if not items[x].has_key('obj'):
                continue

            obj = items[x]['obj']

            print(obj.absolute_url())
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'], obj.Title())
            items[x]['DateCreated'] = obj.getField('DateCreated').get(obj)

            items[x]['SelectedSample'] = self.getSelectedSample(obj)

            items[x]['Analyst'] = self.getAnalyst(obj)
            items[x]['Centrifuges'] = self.getStringified(obj.getCentrifuges())

        return items

    def getSelectedSample(self, obj):
        selected_sample = obj.getField('SelectedSample').get(obj)
        if selected_sample:
            return selected_sample.Title()
        return ''

    def getAnalyst(selfself, obj):
        analyst = obj.getField('Analyst').get(obj)
        if analyst:
            return analyst.Title()
        return ''

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