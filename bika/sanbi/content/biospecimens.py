from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi.config import PROJECTNAME
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IBiospecimens
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from AccessControl import ClassSecurityInfo


class BiospecimensView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(BiospecimensView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {
            'portal_type': 'Biospecimen',
            'sort_on': 'created',
            'sort_order': 'ascending'
        }
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name=Biospecimen',
                'icon': '++resource++bika.lims.images/add.png'
            }
        }
        self.title = self.context.translate(_("Biospecimen"))
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/biospecimen_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title'
            },
            'Description': {
                'title': _('Description'),
                'index': 'description',
                'toggle': True
            },
            'Type': {
                'title': _('Biospecimen Type'),
                'toggle': True
            },
            'Condition': {
                'title': _('Biospecimen Condition'),
                'toggle': True
            },
            'SubjectID': {
                'title': _('Subject ID'),
                'toggle': True
            },
            'Volume': {
                'title': _('Subject ID'),
                'toggle': True
            },
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'Type',
                         'Condition',
                         'SubjectID',
                         'Volume']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'Type',
                         'Condition',
                         'SubjectID',
                         'Volume']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {'sort_on': 'created',
                               'sort_order': 'ascending'},
             'columns': ['Title',
                         'Description',
                         'Type',
                         'Condition',
                         'SubjectID',
                         'Volume']},
        ]

    def __call__(self):
        return super(BiospecimensView, self).__call__()

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Type'] = obj.getType().Title()
            items[x]['Condition'] = obj.getCondition()
            items[x]['SubjectID'] = obj.getSubjectID()
            items[x]['Volume'] = obj.getVolume()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

        return items


schema = ATFolderSchema.copy()


class Biospecimens(ATFolder):
    implements(IBiospecimens)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Biospecimens, PROJECTNAME)