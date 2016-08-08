from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from bika.lims.utils import isActive
from AccessControl import getSecurityManager
from bika.sanbi.permissions import EditFieldBarcode, ViewBarcode


class BiospecimensView(BikaListingView):
    template = ViewPageTemplateFile('templates/biospecimens.pt')
    # table_template = ViewPageTemplateFile("templates/biospecimens_table.pt")
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(BiospecimensView, self).__init__(context, request)
        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'Biospecimen',
            'sort_on': 'created',
            'sort_order': 'ascending'
        }
        self.context_actions = {
            # _('Add'): {
            #     'url': 'createObject?type_name=Biospecimen',
            #     'icon': '++resource++bika.lims.images/add.png'
            # }
        }
        self.title = self.context.translate(_("Biospecimen"))
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/biospecimen_big.png"
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
            'Type': {
                'title': _('Type'),
                'toggle': True
            },
            'Volume': {
                'title': _('Volume'),
                'toggle': True
            },
            'SubjectID': {
                'title': _('Subject ID'),
                'toggle': True
            },
            'Kit': {
                'title': _('Kit'),
                'toggle': True
            },
            'Barcode': {
                'title': _('Barcode'),
                'toggle': True
            },
            # 'Location': {
            #     'title': _('Location'),
            #     'toggle': True
            # },
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'complete'}],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'Kit',
                         'Barcode',
                         # 'Location'
                         ]},

            {'id': 'uncompleted',
             'title': _('Uncompleted'),
             'contentFilter': {'review_state': 'uncompleted',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'complete'}],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'Kit',
                         'Barcode',
                         # 'Location'
                         ]},

            {'id': 'barcoded',
             'title': _('Barcoded'),
             'contentFilter': {'review_state': 'barcoded',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'}],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'Kit',
                         'Barcode',
                         # 'Location'
                         ]},

            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'Kit',
                         'Barcode',
                         # 'Location'
                         ]},

            {'id': 'all',
             'title': _('All'),
             'contentFilter': {'sort_on': 'created',
                               'sort_order': 'ascending'},
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'Kit',
                         'Barcode',
                         # 'Location'
                         ]},
        ]

    def __call__(self):
        return super(BiospecimensView, self).__call__()

    def get_kit_quantity(self):
        project = self.context
        bc = getToolByName(project, 'bika_catalog')
        qtys = []
        brains = bc(portal_type="Kit")
        for brain in brains:
            o = brain.getObject()
            if o.getProject() == project:
                qtys.append(o.getQuantity)

        return sum(qtys)

    def get_kits(self):
        bc = getToolByName(self.context, 'bika_catalog')
        brains = bc(portal_type='Kit', kit_project_uid=self.context.UID())

        return [brain.getObject() for brain in brains]

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self)
        for x, item in enumerate(items):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Type'] = obj.getType() and obj.getType().Title() or ''
            items[x]['Volume'] = obj.getVolume()
            items[x]['SubjectID'] = obj.getSubjectID()
            items[x]['Kit'] = obj.getKit()
            items[x]['replace']['Kit'] = \
                '<a href="%s">%s</a>' % (obj.getKit().absolute_url(), obj.getKit().Title())
            items[x]['Barcode'] = ''
            # items[x]['Location'] = obj.getStorageLocation().Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

            # TODO: SPECIFY OBJ STATES WHERE USER CAN EDIT BARCODE
            allowed_method_state = 'uncompleted'

            can_edit_biospecimen = self.allow_edit and isActive(self.context) and \
                                   getSecurityManager().checkPermission(EditFieldBarcode, obj) and \
                                   item['review_state'] in allowed_method_state

            can_view_barcodes = getSecurityManager().checkPermission(ViewBarcode, obj)

            if can_view_barcodes:
                if can_edit_biospecimen:
                    barcode_html = '<input id="barcode.%s" style="width: 70px;" value="" />' %(obj.UID())
                    item['after']['Barcode'] = barcode_html
                    # items[x]['allow_edit'].extend(['Barcode'])
                    # items[x]['Barcode'] = 'HHHH'
                    # item['choices']['Barcode'] = [{'ResultValue': 'HB', 'ResultText': 'Hocine Bendou'},
                    #                               {'ResultValue':'TTT', 'ResultText': 'Test User'}]
                else:
                    items[x]['Barcode'] = obj.getBarcode()
            else:
                items[x]['before']['Barcode'] = \
                    '<img width="16" height="16" ' + \
                    'src="%s/++resource++bika.lims.images/to_follow.png"/>' % \
                    (self.portal_url)

        return items
