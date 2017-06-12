import json

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.sanbi import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class ManagedStorageView(BikaListingView):
    """This is the default view for Managed storage.
    """
    template = ViewPageTemplateFile("templates/managedstorage_view.pt")

    def __init__(self, context, request):
        super(ManagedStorageView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.positions = self.context.objectValues('StoragePosition')
        self.title = self.context.title
        self.icon = self.portal_url + "/++resource++bika.sanbi.images/" \
                    + "managedstorage_big.png"

        StoragePositions = StoragePositionsView(self.context, self.request)
        # self.positions_table = StoragePositions.contents_table(table_only=True)
        self.positions_table = StoragePositions.__call__()

        StorageGraph = StorageGraphView(self.context, self.request)
        self.graph = StorageGraph()

        return self.template()


class StoragePositionsView(BikaListingView):
    """This is the listing that shows Storage Positions at this location.
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StoragePositionsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.catalog = 'bika_setup_catalog'
        path = '/'.join(context.getPhysicalPath())
        self.contentFilter = {'portal_type': 'StoragePosition',
                              'sort_on': 'sortable_title',
                              'path': {'query': path, 'depth': 1, 'level': 0}
                              }
        self.context_actions = {}
        self.title = ''
        self.description = ''
        self.icon = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.columns = {
            'id': {'title': _('ID'), 'index': 'id'},
            'StorageTypes': {'title': _('Storage Types'), 'toggle': True},
            'StoredItem': {'title': _('Stored Item'), 'toggle': True},
            'review_state': {'title': _('State'), 'toggle': True},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, {'id': 'reserve'},],
             'columns': ['id',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},

            {'id': 'available',
             'title': _('Reserved'),
             'contentFilter': {
                    'review_state': 'reserved'
             },
             'transitions': [{'id': 'liberate'}, ],
             'columns': ['id',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},

            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['id',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},
        ]

    def folderitem(self, obj, item, index):
        workflow = getToolByName(self.context, "portal_workflow")
        mtool = getToolByName(self.context, 'portal_membership')
        if not item.has_key('obj'):
            return item
        obj = item['obj']

        item['id'] = obj.getHierarchy()

        storage_titles = [s['title'] for s in obj.getStorageTypes()]
        item['StorageTypes'] = ','.join(storage_titles)

        si = obj.getStoredItem()
        item['StoredItem'] = si.Title() if si else ''

        item['review_state'] = 'occupied' if si else 'available'

        return item

    def __call__(self):
        self._process_request()
        return self.contents_table(table_only=True)


class StorageGraphView(BrowserView):
    """Show graphic layout of available and occupied positions.
    """
    template = ViewPageTemplateFile("templates/managedstorage_graph.pt")
    title = _("Managed storage positions")

    def __init__(self, context, request):
        super(StorageGraphView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.request.set('disable_plone.rightcolumn', 1)

    def __call__(self):
        return self.template()


class PositionsInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        positions = []
        response = {
            'x': self.context.getXAxis(),
            'y': self.context.getYAxis()
        }

        children = self.context.getPositions()
        for position in children:
            aid, name, subject, volume, unit, path, pos = '', '', '', 0, '', '', ''
            if not position.available():
                item = position.getStoredItem()
                path = item.absolute_url_path()
                pos = position.absolute_url_path()
                aid = item.getId()
                name = item.Title()
                if item.portal_type == 'Sample':
                    # volume = item.getVolume()
                    volume = item.getField("Volume").get(item)
                    unit = item.getField("Unit").get(item)
                    subject = item.getField("SubjectID").get(item) and item.getField("SubjectID").get(item) or ''
                elif item.portal_type == 'Aliquot':
                    # volume = item.getVolume()
                    volume = item.getField("Volume").get(item)
                    unit = item.getUnit()
                    subject = item.getBiospecimen().getSubjectID() and \
                              item.getBiospecimen().getSubjectID() or ''

            state = workflow.getInfoFor(position, 'review_state')
            portal_type = position.getStoredItem() and position.getStoredItem().portal_type or ''
            positions.append({
                'portal_type': portal_type,
                'occupied': state == 'occupied',
                'reserved': state == 'reserved',
                'address': position.getHierarchy(),
                'state': state,
                'aid': aid,
                'name': name,
                'subject': subject,
                'volume': volume,
                'unit': unit,
                'path': path,
                'pos': pos
            })
            response['positions'] = positions

        return json.dumps(response)


class SampleInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        id = form['position']
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        brains = catalog.searchResults(portal_type="StorageLocation", id=id)
        sample = brains[0].getObject().getSample()

        ret = {
            'id': sample.getId(),
            'name': sample.Title(),
            'quantity': sample.getQuantity(),
            'volume': sample.getVolume(),
            'path': sample.absolute_url_path()
        }

        return json.dumps(ret)
