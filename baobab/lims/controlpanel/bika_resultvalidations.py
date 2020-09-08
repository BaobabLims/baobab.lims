from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from baobab.lims.interfaces import IResultValidations


class ResultValidationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ResultValidationsView, self).__init__(context, request)
        self.catalog = 'portal_catalog'
        self.contentFilter = {'portal_type': 'ResultValidation',
                              'sort_on': 'sortable_title'}
        self.context_actions = {
                _('Add'): {'url': 'createObject?type_name=ResultValidation',
                           'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Validation of Results"))
        icon_path = "/++resource++bika.lims.images/product_big.png"
        self.icon = self.portal_url + icon_path
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        if self.context.portal_type == 'ResultValidations':
            self.request.set('disable_border', 1)
        self.columns = {
            'Title': {'title': _('Biobank Number'),
                      'index': 'sortable_title',
                      'toggle': True},
            'StrainValidation': {'title': _('Strain Validation'),
                                 'toggle': True},
            'DateOfValidation': {'title': _('Date of Validation'),
                                 'toggle': True},
            'DeliveryOfCerticate': {'title': _('Date of Certificate'),
                                    'toggle': True},
            'DateDelivered': {'title': _('Date Delivered'),
                              'toggle': True},
            'BiobankedStorage': {'title': _('Biobanked Storage'),
                                 'toggle': True},
            'DateStored': {'title': _('Date of Storage'),
                           'toggle': True},
        }
        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                },
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'Title',
                    'StrainValidation',
                    'DateOfValidation',
                    'DeliveryOfCerticate',
                    'DateDelivered',
                    'BiobankedStorage',
                    'DateStored',
                ]
            }
        ]

    def folderitems(self, full_objects=False):

        items = BikaListingView.folderitems(self)

        for x in range(len(items)):

            if 'obj' not in items[x]:
                continue
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                                   (items[x]['url'],
                                                    items[x]['Title'])

        return items


schema = ATFolderSchema.copy()


class ResultValidations(ATFolder):
    implements(IResultValidations)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(ResultValidations, PROJECTNAME)
