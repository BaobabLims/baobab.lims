from AccessControl import ClassSecurityInfo

from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName

from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims import bikaMessageFactory as _


class ProductSuppliersView(BikaListingView):
    def __init__(self, context, request, field_value=[], allow_edit=False):
        super(ProductSuppliersView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'Supplier',
                              'sort_on': 'sortable_title',
                              'inactive_state': 'active'}
        self.context_actions = {}
        self.base_url = context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.allow_edit = allow_edit
        self.form_id = "suppliers"
        self.profile = None

        self.do_cats = False

        self.columns = {
            'Name': {'title': _('Name'),
                     'index': 'sortable_title',
                     'sortable': False,},
            'Website': {'title': _('Website'),
                        'sortable': False,},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Name',
                         'Website',
                         ],
             'transitions': [{'id': 'empty'}, ],
             },
        ]

        self.field_value = field_value
        self.selected = [x.UID() for x in field_value]

    def folderitems(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            suppliers = [a.UID() for a in self.field_value]
            items[x]['selected'] = items[x]['uid'] in suppliers

            items[x]['replace']['Name'] = "<a href='%s'>%s</a>" % \
                                          (items[x]['url'], items[x]['Name'])

            # items[x]['class']['Name'] = 'service_title'
            items[x]['Website'] = obj.getWebsite()
            items[x]['class']['Price'] = 'nowrap'

        return items


class ProductSuppliersWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "baobab_lims_widgets/productsupplierswidget",
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        service_uids = form.get('uids', None)

        return service_uids, {}

    security.declarePublic('Analyses')

    def Suppliers(self, field, allow_edit=False):
        """Print analyses table
        """
        field_value = getattr(field, field.accessor)()
        view = ProductSuppliersView(self,
                                    self.REQUEST,
                                    field_value=field_value,
                                    allow_edit=allow_edit)
        return view.contents_table(table_only=True)


registerWidget(ProductSuppliersWidget,
               title='Product Suppliers selector',
               description=('Product Suppliers selector',),
               )
