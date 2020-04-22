from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from baobab.lims.config import PROJECTNAME
from baobab.lims import bikaMessageFactory as _
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from baobab.lims.interfaces import IKitTemplates


class KitTemplatesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(KitTemplatesView, self).__init__(context, request)

        request.set('disable_plone.rightcolumn', 1)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'KitTemplate',
                              'sort_on': 'sortable_title',
                              'sort_order': 'reverse',
                              #'path': {"query": "/", "level": 0},
                              'inactive_state': 'active',
                              }

        self.context_actions = {}

        if self.context.portal_type == "KitTemplates":
            self.request.set('disable_border', 1)

        if self.view_url.find("kittemplates") == -1:
            self.view_url = self.view_url + "/kittemplates"

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.form_id = "kittemplates"

        self.icon = self.portal_url + "/++resource++bika.lims.images/product_big.png"
        self.title = self.context.translate(_("Kit Templates"))
        self.description = ""

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        self.columns = {
            'Title': {'title': _('Title')},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True}
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             #'contentFilter': {'sort_on':'created', 'sort_order': 'reverse'},
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': [
                 'Title',
                 'Description'
             ]},
        ]

    def folderitems(self):
        """
        """
        items = super(KitTemplatesView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

    def __call__(self, *args, **kwargs):
        """
        """
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission("Modify portal content", self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=KitTemplate',
                'icon': '++resource++bika.lims.images/add.png'
            }
            self.review_states.append(
                {'id':'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': ['Title',]})
            self.review_states.append(
                {'id': 'All',
                 'title': _('All'),
                 'contentFilter': {},
                 'transitions':[{'id':'empty'}],
                 'columns': [
                     'Title',
                 ]})
            stat = self.request.get("%s_review_state"%self.form_id, 'default')
            self.show_select_column = stat != 'all'

        return super(KitTemplatesView, self).__call__()


schema = ATFolderSchema.copy()

class KitTemplates(ATFolder):
    implements(IKitTemplates)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(KitTemplates, PROJECTNAME)
