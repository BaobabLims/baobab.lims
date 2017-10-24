from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView

from baobab.lims.browser.projects import ProjectsView


class ClientProjectsView(ProjectsView):
    """This is displayed in the "Projects" tab on each client
    """

    def __init__(self, context, request):
        ProjectsView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.context.setConstrainTypesMode(0)
        self.contentFilter['path'] = {
            'query': '/'.join(self.context.getPhysicalPath()),
            'level': 0
        }

        self.columns = {
            'Title': {'title': _('Project'),
                      'index': 'sortable_title'},
            'getStudyType': {'title': _('Study Type'),
                             'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [],
             'columns': ['Title',
                         'getStudyType']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['replace']['Title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['Title'])

        return items
