from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.lib import constraintypes
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.browser.biospecimens.biospecimens import BiospecimensView
from bika.sanbi.controlpanel.bika_biospectypes import BiospecTypesView
from bika.lims.browser import BrowserView
from bika.lims.controlpanel.bika_analysisservices import AnalysisServicesView
from bika.sanbi.browser.aliquots.folder_view import AliquotsView


class ProjectEdit(BrowserView):
    template = ViewPageTemplateFile('templates/project_edit.pt')
    title = _("Project Registration")

    def __init__(self, context, request):
        self.context = context
        self.request = request

        super(ProjectEdit, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/project_big.png"

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        form = self.request.form
        if 'submit' in request:
            context.setConstrainTypesMode(constraintypes.DISABLED)
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

            uc = getToolByName(context, 'uid_catalog')
            brains = uc(UID=form['Client_uid'])
            if brains:
                context.setClient(brains[0].getObject())

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

        return self.template()

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

class ProjectAnalysisServicesView(AnalysisServicesView):
    def __init__(self, context, request, uids):
        self.uids = uids
        super(ProjectAnalysisServicesView, self).__init__(context, request)
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
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Price'] = "%s.%02d" % obj.Price
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % (
                                            items[x]['url'], items[x]['Title'])
            out_items.append(items[x])

        return out_items


class ProjectBiospecView(BiospecTypesView):
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
        items = BiospecTypesView.folderitems(self)
        out_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
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
        self.client = context.getClient().Title()
        self.study_type = context.getStudyType()
        self.participants = context.getNumParticipants()
        self.age_interval = str(context.getAgeLow()) + ' - ' + str(context.getAgeHigh())

        biospec_types = ProjectBiospecView(context, request, context.getBiospectypes())
        self.bio_table = biospec_types.contents_table()

        uids = [o.UID() for o in context.getService()]
        view = ProjectAnalysisServicesView(context, request, uids)

        self.analyses_table = view.contents_table()
        return self.template()


class ProjectBiospecimensView(BiospecimensView):
    def __init__(self, context, request):
        self.context = context
        super(ProjectBiospecimensView, self).__init__(context, request)

    def folderitems(self, full_objects=False):
        items = BiospecimensView.folderitems(self)
        out_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            project = obj.aq_parent
            if project == self.context:
                items[x]['Type'] = obj.getType().Title()
                items[x]['Condition'] = obj.getCondition()
                items[x]['SubjectID'] = obj.getSubjectID()
                items[x]['Volume'] = obj.getVolume()
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                               (items[x]['url'], items[x]['Title'])
                out_items.append(items[x])

        return out_items


class BiospecimenAliquotsView(AliquotsView):
    def __init__(self, context, request):
        self.context = context
        super(BiospecimenAliquotsView, self).__init__(context, request)

