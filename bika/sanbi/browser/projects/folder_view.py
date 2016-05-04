from Products.CMFCore.utils import getToolByName
from zope.interface.declarations import implements
from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.sanbi.permissions import AddProject, ManageProjects


class ProjectsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ProjectsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Project',
                              'sort_on': 'sortable_title'}

        self.context_actions = {}
        self.title = self.context.translate(_("Projects"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/container_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'client_name': {'title': _('Client'),
                            'toggle': True},
            'type_study': {'title': _('Study Type'),
                           'toggle': True}
        }
        self.review_states = []

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddProject, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Project',
                'icon': '++resource++bika.lims.images/add.png'
            }

        if mtool.checkPermission(ManageProjects, self.context):
            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'

        return super(ProjectsView, self).__call__()

    def folderitems(self, full_objects = False):
        pass
