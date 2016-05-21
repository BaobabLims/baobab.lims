from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from zope.i18n.locales import locales


class ProjectAnalysesView(BikaListingView):
    """bika listing to display Analyses table for an project
       and biospecimen.
    """
    def __init__(self, context, request, field_value=[], allow_edit=False):
        super(ProjectAnalysesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title',
                              'inactive_state': 'active'}
        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.allow_edit = allow_edit
        self.form_id = "analyses"
        self.profile = None

        self.do_cats = False

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title',
                      'sortable': False,},
            'Price': {'title': _('Price'),
                      'sortable': False,},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Price',
                         ],
             'transitions': [{'id':'empty'}, ], # none
             },
        ]

        if not self.context.bika_setup.getShowPrices():
            self.review_states[0]['columns'].remove('Price')

        self.field_value = field_value
        self.selected = [x.UID() for x in field_value]

    def folderitems(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            analyses = [a.UID() for a in self.field_value]
            items[x]['selected'] = items[x]['uid'] in analyses

            items[x]['class']['Title'] = 'service_title'

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()

            locale = locales.getLocale('en')
            currency = self.context.bika_setup.getCurrency()
            symbol = locale.numbers.currencies[currency].symbol
            items[x]['Price'] = "%s %s" % (symbol, obj.getPrice())
            items[x]['class']['Price'] = 'nowrap'

            after_icons = ''
            if obj.getAccredited():
                after_icons += "<img\
                    src='%s/++resource++bika.lims.images/accredited.png'\
                    title='%s'>" % (self.context.absolute_url(),
                                    _("Accredited"))
            if obj.getReportDryMatter():
                after_icons += "<img\
                    src='%s/++resource++bika.lims.images/dry.png'\
                    title='%s'>" % (self.context.absolute_url(),
                                    _("Can be reported as dry matter"))
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img\
                    src='%s/++resource++bika.lims.images/attach_reqd.png'\
                    title='%s'>" % (self.context.absolute_url(),
                                    _("Attachment required"))
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img\
                    src='%s/++resource++bika.lims.images/attach_no.png'\
                    title='%s'>" % (self.context.absolute_url(),
                                    _('Attachment not permitted'))
            if after_icons:
                items[x]['after']['Title'] = after_icons


        return items

class ProjectAnalysesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_sanbi_widgets/projectanalyseswidget",
        'helper_js': ("bika_sanbi_widgets/projectanalyseswidget.js",),
        'helper_css': ("bika_sanbi_widgets/projectanalyseswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):

        service_uids = form.get('uids', None)

        # if instance.portal_type == 'BiospecType':
        #     pass
        return service_uids, {}

    security.declarePublic('Analyses')
    def Analyses(self, field, allow_edit=False):
        """Print analyses table
        """
        field_value = getattr(field, field.accessor)()
        view = ProjectAnalysesView(self,
                                   self.REQUEST,
                                   field_value = field_value,
                                   allow_edit = allow_edit)
        return view.contents_table(table_only=True)

registerWidget(ProjectAnalysesWidget,
               title='Project Analyses selector',
               description=('Project Analyses selector',),
               )