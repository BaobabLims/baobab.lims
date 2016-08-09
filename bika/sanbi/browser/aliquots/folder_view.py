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
from bika.sanbi.permissions import *


class AliquotsView(BikaListingView):
    template = ViewPageTemplateFile('templates/aliquots.pt')
    table_template = ViewPageTemplateFile("templates/aliquots_table.pt")
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AliquotsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'Aliquot',
                              'sort_on': 'sortable_title'}

        self.context_actions = {}
        self.title = self.context.translate(_("Aliquots"))
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/aliquot_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'Title': {'title': _('Aliquot'),
                      'index': 'sortable_title'},
            'Biospecimen': {'title': _('Biospecimen'),
                            'toggle': True},
            'SubjectID': {'title': _('Subject ID'),
                          'toggle': True},
            'AliquotType': {'title': _('Aliquot Type'),
                            'toggle': True},
            'Volume': {'title': _('Volume'),
                       'toggle': True},
            'Quantity': {'title': _('Quantity'),
                         'toggle': True},
            'Location': {'title': _('Location'),
                         'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Pending'),
             'contentFilter': {'inactive_state': 'active',
                               'review_state': 'pending',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'store'}],
             'columns': ['Title',
                         'Biospecimen',
                         'SubjectID',
                         'AliquotType',
                         'Quantity',
                         'Volume',
                         'Location']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        # if mtool.checkPermission(AddAliquot, self.context):
        #     self.context_actions[_('Add')] = {
        #         'url': 'createObject?type_name=Aliquot',
        #         'icon': '++resource++bika.lims.images/add.png'
        #     }

        if mtool.checkPermission(ManageAliquots, self.context):
            self.review_states[0]['transitions'].append({'id': 'deactivate'})
            self.review_states.append(
                {'id': 'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id': 'activate'}, ],
                 'columns': ['Title',
                             'Biospecimen',
                             'SubjectID',
                             'AliquotType',
                             'Quantity',
                             'Volume',
                             'Location']})

            self.review_states.append(
                {'id': 'stored',
                 'title': _('Stored'),
                 'contentFilter': {'review_state': 'stored',
                                   'sort_on': 'created',
                                   'sort_order': 'reverse'},
                 'transitions': [{'id': 'pend'},
                                 {'id': 'deactivate'}],
                 'columns': ['Title',
                             'Biospecimen',
                             'SubjectID',
                             'AliquotType',
                             'Quantity',
                             'Volume',
                             'Location']})

            self.review_states.append(
                {'id': 'all',
                 'title': _('All'),
                 'contentFilter': {},
                 'transitions': [{'id': 'empty'}],
                 'columns': ['Title',
                             'Biospecimen',
                             'SubjectID',
                             'AliquotType',
                             'Quantity',
                             'Volume',
                             'Location']})

            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'

        return super(AliquotsView, self).__call__()

    def folderitems(self):
        items = super(AliquotsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Biospecimen'] = obj.getBiospecimen().Title()
            items[x]['SubjectID'] = obj.getSubjectID()
            items[x]['AliquotType'] = obj.getAliquotType().Title()
            items[x]['Quantity'] = obj.getQuantity()
            items[x]['Volume'] = obj.getVolume()
            items[x][
                'Location'] = obj.getStorageLocation() and \
                              obj.getStorageLocation().Title() or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])

        return items

    def get_biospecimens(self):
        biospecimens = self.context.objectValues('Biospecimen')
        ret = {}
        for biospecimen in biospecimens:
            ret[biospecimen.UID()] = biospecimen.Title()

        return ret


class AjaxSampleTypes:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type='SampleType', inactive_state='active')
        ret = []
        for brain in brains:
            ret.append({'uid': brain.UID,
                        'title': brain.title})

        return json.dumps(ret)


class AjaxGetRooms:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(portal_type='StorageUnit', inactive_state='active')
        ret = []
        for brain in brains:
            ret.append({'uid': brain.UID,
                        'title': brain.title})

        return json.dumps(ret)


class CreateAliquots:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        aliquots = json.loads([key for key in form][0])
        project = self.context.aq_parent
        uc = getToolByName(project, 'uid_catalog')
        bsc = getToolByName(project, 'bika_setup_catalog')
        for s in aliquots:
            biospecimen = uc(UID=s['biospecimen'])[0].getObject()
            type = uc(UID=s['type'])[0].getObject()
            room = uc(UID=s['room'])[0].getObject()
            freezer = uc(UID=s['freezer'])[0].getObject()
            shelf = uc(UID=s['shelf'])[0].getObject()
            box = uc(UID=s['box'])[0].getObject()
            brains = bsc(portal_type='StorageLocation', parent_box_uid=s['box'],
                         review_state='available')
            position = brains[0].getObject() if brains else None
            if not position:
                storage = '.'.join([room.id, freezer.id, shelf.id, box.id])
                message = "No free position available for \"%s\" in Storage " \
                          "\"%s\"" % (
                s['title'], storage)
                return json.dumps({'error': message})

            # create aliquot
            aliquot = _createObjectByType('Aliquot', project, tmpID())
            aliquot.edit(
                title=s['title'],
                Biospecimen=biospecimen,
                SubjectID=biospecimen.getSubjectID(),
                Volume=s['volume'],
                Quantity=1,
                AliquotType=type,
                StorageLocation=position
            )
            aliquot.unmarkCreationFlag()
            renameAfterCreation(aliquot)
            aliquot.reindexObject()
            aliquot.at_post_create_script()

        return json.dumps({'success': 'Aliquots Created'})
