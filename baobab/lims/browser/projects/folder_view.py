from Products.CMFCore.utils import getToolByName

from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import isActive
from baobab.lims import bikaMessageFactory as _
from baobab.lims.permissions import *

import json


class ProjectsView(BikaListingView):
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.contentFilter = {'portal_type': 'Project',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Projects"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/project_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        if self.context.portal_type == 'Projects':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {'title': _('Project'),
                      'index': 'sortable_title'},
            'getClient': {'title': _('Client'),
                          'toggle': True},
            'getStudyType': {'title': _('Study Type'),
                             'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [],
             'columns': ['Title',
                         'getClient',
                         'getStudyType']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        w_tool = getToolByName(self.context, 'portal_workflow')
        active_contacts = [c for c in self.context.objectValues('Contact') if
                           w_tool.getInfoFor(c, 'inactive_state', '') == 'active']
        if isActive(self.context):
            if self.context.portal_type == "Client":
                if not active_contacts:
                    msg = _("Client contact required before request may be submitted")
                    addPortalMessage(msg)
                else:
                    if mtool.checkPermission(AddProject, self.context):
                        self.context_actions[_('Add')] = {
                            'url': 'createObject?type_name=Project',
                            'icon': '++resource++bika.lims.images/add.png'
                        }
        if mtool.checkPermission(ManageProjects, self.context):
            self.review_states[0]['transitions'].append({'id': 'deactivate'})
            self.review_states.append(
                {'id': 'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id': 'activate'}, ],
                 'columns': ['Title',
                             'getClient',
                             'getStudyType']})
            self.review_states.append(
                {'id': 'all',
                 'title': _('All'),
                 'contentFilter': {},
                 'transitions': [{'id': 'empty'}],
                 'columns': ['Title',
                             'getClient',
                             'getStudyType']})
            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'
        return BikaListingView.__call__(self)

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['getClient'] = obj.aq_parent.Title()
            items[x]['getStudyType'] = obj.getStudyType()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

        return items


class AjaxGetChildren:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form

        uc = getToolByName(self.context, 'uid_catalog')
        brains = uc(UID=form['uid'])
        if brains:
            roompath = '/'.join(brains[0].getObject().getPhysicalPath())
        else:
            roompath = ''

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type="StorageManagement",
                     path={'query': roompath, 'depth': 1}
                     )
        ret = []
        for brain in brains:
            ret.append({'uid': brain.UID,
                        'title': brain.title})

        return json.dumps(ret)
