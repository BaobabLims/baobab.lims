import os
# import cgi, cgitb, jinja2
# import urllib.request

import datetime

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.lib import constraintypes

from Products.CMFCore.utils import getToolByName

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

from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime


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
        upload_directory = '/static/uploads'
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

        self.ethics_form = "<a href='%s'>%s</a>" % (
            context.getEthicsFormLink(),
            context.getEthicsFormLink()
        )

        self.client = "<a href='%s'>%s</a>" % (
            context.aq_parent.absolute_url(),
            context.aq_parent.Title()
        )

        self.study_type = context.getStudyType()
        self.participants = context.getNumParticipants()
        self.age_interval = str(context.getAgeLow()) + ' - ' + str(
            context.getAgeHigh())

        # self.project_upload_file = context.portal_url() + upload_directory + '/' + context.getProjectUploadFile()
        self.project_upload_file = context.getProjectUploadFile()

        biospecimen_types = ProjectBiospecView(context, request,
                                           context.getSampleType())
        self.bio_table = biospecimen_types.contents_table()

        uids = [o.UID() for o in context.getService()]
        view = ProjectAnalysisServicesView(context, request, uids)

        self.analyses_table = view.contents_table()
        return self.template()

class ProjectEdit(BrowserView):
    template = ViewPageTemplateFile('templates/project_edit.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

        if 'submitted' in request:
            audit_logger = AuditLogger(self.context, 'Project')
            context.setConstrainTypesMode(constraintypes.DISABLED)
            # This following line does the same as precedent which one is the
            #  best?

            # context.aq_parent.setConstrainTypesMode(constraintypes.DISABLED)
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            is_new = False

            if context.getId() == '':
                is_new = True
            else:
                is_new = False
                self.perform_project_audit(context, request)

            file_name = self.get_the_file()
            context.processForm()
            obj_url = context.absolute_url_path()

            if is_new:
                audit_logger.perform_simple_audit(context, 'New')

            context.getField('ProjectUploadFile').set(context, file_name)
            context.reindexObject()

            request.response.redirect(obj_url)

            return

        return self.template()

    def get_project_upload_file(self):

        context = self.context
        return context.getProjectUploadFile()
        # project_upload_name = context.getField('ProjectUploadFile').get(context)
        # return project_upload_name

    def get_the_file(self):
        _UPLOADS = 'static/uploads/'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_dir = self.get_directory_name(base_dir)
        uploads_directory = os.path.join(base_dir, _UPLOADS)

        if 'fileUpload' in self.request.form:
            form_file = self.request.form['fileUpload']

            if form_file.filename != '':
                current_date = str(datetime.datetime.now().date()) + '_' + \
                           str(datetime.datetime.now().time()).replace(':', '.')

                file_name = "%s_%s" % (current_date, form_file.filename)
                uploaded_file_path = os.path.join(uploads_directory, os.path.basename(file_name))

                file_content = form_file.read()
                self.get_directory_name(base_dir)

                with open(uploaded_file_path, "w") as file_write:
                    file_write.write(file_content)

                return file_name

    def get_directory_name(self, directory):
        browser = directory[-8:]

        if browser == '/browser':
            s = directory.rfind('/browser')
            directory = directory[:s]

        return directory



    def perform_project_audit(self, project, request):
        audit_logger = AuditLogger(self.context, 'Project')
        pc = getToolByName(self.context, "portal_catalog")

        if project.getField('StudyType').get(project) != request.form['StudyType']:
            audit_logger.perform_simple_audit(project, 'StudyType', project.getField('StudyType').get(project),
                                              request.form['StudyType'])

        if project.getField('EthicsFormLink').get(project) != request.form['EthicsFormLink']:
            audit_logger.perform_simple_audit(project, 'EthicsFormLink', project.getField('EthicsFormLink').get(project),
                                              request.form['EthicsFormLink'])

        # audit age high
        current_age_high = project.getField('AgeHigh').get(project)
        if not current_age_high:
            current_age_high = ''
        else:
            current_age_high = str(project.getField('AgeHigh').get(project))

        if current_age_high != request.form['AgeHigh']:
            request.form['AgeHigh']
            audit_logger.perform_simple_audit(project, 'AgeHigh', current_age_high,
                                              request.form['AgeHigh'])

        # audit age low
        current_age_low = project.getField('AgeLow').get(project)
        if not current_age_low:
            current_age_low = ''
        else:
            current_age_low = str(current_age_low)

        if current_age_low != request.form['AgeLow']:
            request.form['AgeLow']
            audit_logger.perform_simple_audit(project, 'AgeLow', current_age_low,
                                              request.form['AgeLow'])

        # audit number of participants
        num_participants = project.getField('NumParticipants').get(project)
        if not num_participants:
            num_participants = ''
        else:
            num_participants = str(num_participants)

        if num_participants != request.form['NumParticipants']:
            request.form['NumParticipants']
            audit_logger.perform_simple_audit(project, 'NumParticipants', num_participants,
                                              request.form['NumParticipants'])

        audit_logger.perform_multi_reference_list_to_list_audit(project, 'SampleType', project.getField('SampleType').get(project),
                                             pc, request.form['SampleType'])

        # perform auditing on analysis services
        analysis_service_uids = []
        if 'uids' in request.form:
            analysis_service_uids = request.form['uids']
        audit_logger.perform_multi_reference_list_to_list_audit(project, 'Service',
                                                   project.getField('Service').get(project),
                                                   pc, analysis_service_uids)
        

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields


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
        self.catalog = "bika_catalog"

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
