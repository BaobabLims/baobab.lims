from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView
from bika.lims.browser.client import ClientAnalysisRequestsView
from bika.lims.controlpanel.bika_analysisservices import AnalysisServicesView
from bika.lims.controlpanel.bika_sampletypes import SampleTypesView
from bika.lims.browser.invoicefolder import InvoiceFolderContentsView
from baobab.lims.browser.analysisrequest import hide_actions_and_columns
from baobab.lims.browser.biospecimens.biospecimens import BiospecimensView
from baobab.lims.browser.kits.folder_view import KitsView
from baobab.lims.browser.shipments.folder_view import ShipmentsView
from baobab.lims import bikaMessageFactory as _


class ProjectAnalysisServicesView(AnalysisServicesView):
    def __init__(self, context, request, uids):
        self.uids = uids
        AnalysisServicesView.__init__(self, context, request)
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.context_actions = {}
        self.allow_edit = False
        self.pagesize = 999999
        self.contentFilter['UID'] = self.uids

        self.show_categories = True
        self.expand_all_categories = True
        self.ajax_categories = False

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title'},
            'Price': {'title': _('Price')},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Price']
             }]

    def folderitems(self):
        items = AnalysisServicesView.folderitems(self)
        out_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Price'] = "%s.%02d" % obj.Price
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % (
                items[x]['url'], items[x]['Title'])
            out_items.append(items[x])

        return out_items


class ProjectBiospecView(SampleTypesView):
    def __init__(self, context, request, uids):
        super(ProjectBiospecView, self).__init__(context, request)
        self.uids = uids
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.context_actions = {}
        self.allow_edit = False
        self.pagesize = 999999
        self.contentFilter['UID'] = self.uids

        self.columns = {
            'Title': {'title': _('Name'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Description']
             },
        ]

    def folderitems(self):
        items = SampleTypesView.folderitems(self)
        out_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            out_items.append(items[x])

        return out_items

    def __call__(self):
        return super(ProjectBiospecView, self).__call__()


class ProjectView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/project_view.pt")
    title = _("Project Registration")

    def __call__(self):
        context = self.context
        request = self.request
        portal = self.portal
        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup

        # __Disable the add new menu item__ #
        context.setLocallyAllowedTypes(())

        # __Collect general data__ #
        self.id = context.getId()
        self.title = context.Title()
        self.description = context.Description()
        self.client = "<a href='%s'>%s</a>" % (
            context.aq_parent.absolute_url(),
            context.aq_parent.Title()
        )
        self.study_type = context.getStudyType()
        self.participants = context.getNumParticipants()
        self.age_interval = str(context.getAgeLow()) + ' - ' + str(
            context.getAgeHigh())

        biospecimen_types = ProjectBiospecView(context, request,
                                           context.getSampleType())
        self.bio_table = biospecimen_types.contents_table()

        uids = [o.UID() for o in context.getService()]
        view = ProjectAnalysisServicesView(context, request, uids)

        self.analyses_table = view.contents_table()
        return self.template()


class ProjectKitsView(KitsView):
    """
    """
    def __init__(self, context, request):
        super(ProjectKitsView, self).__init__(context, request)
        self.context = context
        self.request = request
        # Filter kits by project uid
        self.columns.pop('Project', None)
        path = '/'.join(self.context.getPhysicalPath())
        for state in self.review_states:
            state['contentFilter']['path'] = {'query': path, 'depth': 1}
            state['columns'].remove('Project')

    def folderitems(self, full_objects=False):
        items = KitsView.folderitems(self)

        return items


class ProjectShipmentsView(ShipmentsView):
    """ Shipments view from project view.
    """
    def __init__(self, context, request):
        super(ProjectShipmentsView, self).__init__(context, request)
        self.context = context
        self.request = request
        # Filter shipments by project uid
        self.columns.pop('Project', None)
        path = '/'.join(self.context.getPhysicalPath())
        for state in self.review_states:
            state['contentFilter']['path'] = {'query': path, 'depth': 1}
            state['columns'].remove('Project')

    def folderitems(self, full_objects=False):
        items = ShipmentsView.folderitems(self)

        return items


class ProjectBiospecimensView(BiospecimensView):
    """ Biospecimens veiw from project view.
    """
    def __init__(self, context, request):
        BiospecimensView.__init__(self, context, request)
        self.context = context
        self.context_actions = {}

        # Filter biospecimens by project uid
        self.columns.pop('Project', None)
        # path = '/'.join(self.context.getPhysicalPath())
        for state in self.review_states:
            # state['contentFilter']['path'] = {'query': path, 'depth': 1}
            state['contentFilter']['getProjectUID'] = self.context.UID()
            state['contentFilter']['sort_on'] = 'sortable_title'
            state['columns'].remove('Project')

    def folderitems(self, full_objects=False):
        items = BiospecimensView.folderitems(self)

        return items


class InvoiceCreate(InvoiceFolderContentsView):
    """List project's invoices
    """

    def __init__(self, context, request):
        super(InvoiceCreate, self).__init__(context, request)
        self.context = context
        self.columns['service'] = {'title': _('Service')}

        # Add column 'service' to the lising table columns
        for state in self.review_states:
            state['columns'].insert(state['columns'].index('start'), 'service')


class ProjectAnalysisRequestsView(ClientAnalysisRequestsView):
    """Show ARs of this project.
    """

    def __init__(self, context, request):
        ClientAnalysisRequestsView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.contentFilter = {
            'portal_type': 'AnalysisRequest',
            'sort_on': 'created',
            'sort_order': 'reverse',
            'cancellation_state': 'active',
        }
        hide_actions_and_columns(self)

    def folderitem(self, obj, item, index):
        ClientAnalysisRequestsView.folderitem(self, obj, item, index)
        field = obj.getField('Project')
        project = field.get(obj)
        if project == self.context:
            return item

        return None
