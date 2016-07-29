import json

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import tmpID
from bika.sanbi import bikaMessageFactory as _


class BiospecimensView(BikaListingView):
    template = ViewPageTemplateFile('templates/biospecimens.pt')
    table_template = ViewPageTemplateFile("templates/biospecimens_table.pt")
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
            'StockItem': {
                'title': _('Stock Item'),
                'toggle': True
            },
            'Barcode': {
                'title': _('Barcode'),
                'toggle': True
            },
            'Location': {
                'title': _('Location'),
                'toggle': True
            },
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'receive'}],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'StockItem',
                         'Barcode',
                         'Location']},

            {'id': 'due',
             'title': _('Due'),
             'contentFilter': {'review_state': 'due',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'receive'}],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'StockItem',
                         'Barcode',
                         'Location']},

            {'id': 'received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'received',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'store'}],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'StockItem',
                         'Barcode',
                         'Location']},

            {'id': 'stored',
             'title': _('Stored'),
             'contentFilter': {'review_state': 'stored',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'StockItem',
                         'Barcode',
                         'Location']},

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
                         'StockItem',
                         'Barcode',
                         'Location']},

            {'id': 'all',
             'title': _('All'),
             'contentFilter': {'sort_on': 'created',
                               'sort_order': 'ascending'},
             'columns': ['Title',
                         'Type',
                         'Volume',
                         'SubjectID',
                         'StockItem',
                         'Barcode',
                         'Location']},
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
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Type'] = obj.getType().Title()
            items[x]['Volume'] = obj.getVolume()
            items[x]['SubjectID'] = obj.getSubjectID()
            items[x]['StockItem'] = obj.getKitStockItem()
            items[x]['Barcode'] = obj.getBarcode()
            items[x]['Location'] = obj.getStorageLocation().Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

        return items


class AjaxAvailablePositions:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        uc = getToolByName(self.context, 'uid_catalog')
        brains = uc(UID=form['uid'])
        box = brains[0].getObject()
        positions = box.getPositions()
        workflow = getToolByName(self.context, 'portal_workflow')
        free = 0
        for position in positions:
            state = workflow.getInfoFor(position, 'review_state')
            if state == 'position_free':
                free += 1

        return json.dumps({'free': free})


class CreateBiospecimens:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        biospecimens = json.loads([key for key in form][0])
        project = self.context.aq_parent
        uc = getToolByName(project, 'uid_catalog')
        bsc = getToolByName(project, 'bika_setup_catalog')
        kit = uc(UID=biospecimens[0]['kit'])[
            0].getObject() if biospecimens else None
        for b in biospecimens:
            if b['type'] == 'None':
                message = 'type should be specified!'
                return json.dumps({'error': message})
            type = uc(UID=b['type'])[0].getObject()
            if b['box'] == 'Box':
                message = 'Position should be specified!'
                return json.dumps({'error': message})
            box = uc(UID=b['box'])[0].getObject()
            positions = box.get_free_positions()
            if not positions:
                message = "No free position available for \"%s\" in Storage " \
                          "\"%s\"" % (
                b['title'], box.id)
                return json.dumps({'error': message})

            # Create biospecimen
            biospecimen = _createObjectByType('Biospecimen', project, tmpID())
            biospecimen.edit(
                title=b['title'],
                Type=type,
                SubjectID=b['subject'],
                Volume=b['volume'],
                KitStockItem=b['stockitem'],
                Barcode=b['barcode'],
                kit=kit,
                StorageLocation=positions[0]
            )
            biospecimen.unmarkCreationFlag()
            renameAfterCreation(biospecimen)
            biospecimen.reindexObject()
            biospecimen.at_post_create_script()

        return json.dumps({'success': 'Aliquots Created'})
