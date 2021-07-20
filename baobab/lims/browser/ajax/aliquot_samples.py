from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError
from DateTime import DateTime

from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation

from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor

import json
import plone

from operator import itemgetter

from baobab.lims.interfaces import IUnmanagedStorage, IStoragePosition, \
    IManagedStorage

#
# class AliquotSamplesView(BrowserView):
#     # index = ViewPageTemplateFile("templates/aliquot_samples.pt")
#     template = ViewPageTemplateFile("templates/aliquot_samples.pt")
#
#     def __init__(self, context, request):
#         # IV.__init__(self, context, request)
#         BrowserView.__init__(self, context, request)
#         self.context = context
#         self.request = request
#
#     def __call__(self):
#         return self.template()


class ajaxGetSamples(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetSamples, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # plone.protect.CheckAuthenticator(self.request)
        rows = []

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="Sample")

        for sample in brains:
            rows.append({
                sample.UID: sample.Title
            })

        return json.dumps(rows)

# class ajaxGetVirusSamples(BrowserView):
#     """ Drug vocabulary source for jquery combo dropdown box
#     """
#
#     def __init__(self, context, request):
#         super(ajaxGetSamples, self).__init__(context, request)
#         self.context = context
#         self.request = request
#
#     def __call__(self):
#         # plone.protect.CheckAuthenticator(self.request)
#         rows = []
#
#         pc = getToolByName(self.context, 'portal_catalog')
#         brains = pc(portal_type="VirusSample")
#
#         for sample in brains:
#             rows.append({
#                 sample.UID: sample.Title
#             })
#
#         return json.dumps(rows)


class ajaxGetSampleDetails(BrowserView):

    def __init__(self, context, request):
        super(ajaxGetSampleDetails, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')

    def __call__(self):

        sample = self.get_sample(self.request.form['sample_uid'])

        if sample:
            try:
                storage = sample.getField('StorageLocation').get(sample).getHierarchy()
            except Exception as e:
                storage = ''

            result_dict = {
                'title': sample.Title(),
                'uid': sample.UID(),
                'storage': storage,
                'volume': sample.getField('Volume').get(sample),
                'unit': sample.getField('Unit').get(sample),
            }

            result = json.dumps(result_dict)
            return result


        return json.dumps({
            'title': '',
            'uid': '',
            'storage': '',
            'volume': '',
            'unit': '',
        })

    def get_sample(self, sample_uid):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=sample_uid)
            return brains[0].getObject()
        except Exception as e:
            return None



class ajaxGetStorageUnits(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetStorageUnits, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        rows = []

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="StorageUnit")

        for storage_unit in brains:
            storage_unit = storage_unit.getObject()

            rows.append({
                storage_unit.UID(): storage_unit.getHierarchy()
            })

        return json.dumps(rows)


    def get_sample(self, sample_uid):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=sample_uid)
            return brains[0].getObject()
        except Exception as e:
            return None


class ajaxGetBoxes(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetBoxes, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        rows = []

        storage_unit = self.request.form['storage_unit']

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="StorageUnit", UID=storage_unit)

        storage_unit = brains[0].getObject()
        boxes = storage_unit.getBoxes()

        for box in boxes:

            rows.append({
                box.UID(): box.getHierarchy()
            })

        return json.dumps(rows)


class ajaxGetStoragePositions(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetStoragePositions, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        rows = []

        storage_uid = self.request.form['storage_uid']
        storage_type = self.request.form['storage_type']

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type=storage_type, UID=storage_uid)

        storage = brains[0].getObject()

        positions = storage.get_positions()

        for position in positions:
            if position.available():

                rows.append({
                    position.UID(): position.getHierarchy()
                })

        return json.dumps(rows)


class ajaxCreateAliquots(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxCreateAliquots, self).__init__(context, request)
        self.context = context
        self.request = request
        self.pc = getToolByName(self.context, 'portal_catalog')
        self.sample_results = []

    def __call__(self):
        try:
            aliquots_data = self.request.form['sample_aliquots']
            aliquots_data = json.loads(aliquots_data)
        except:
            return json.dumps(self.sample_results.append('No valid sample aliquots has been send to the server'))

        for sample_uid, new_aliquots in aliquots_data.iteritems():

            try:
                sample = self.get_sample(sample_uid)
                if not sample:
                    self.sample_results.append('Sample with uid %s is not found' % sample_uid)
                    continue
                for aliquot in new_aliquots:
                    if not all(k in aliquot for k in ('volume', 'barcode')):
                        self.sample_results.append('Aliquot for sample %s is missing either barcode or volume' %sample.Title())
                        continue

                    try:
                        storage_brains = self.pc(portal_type='StoragePosition', UID=aliquot['storage'])
                        storage_location = storage_brains and storage_brains[0].getObject() or None
                        new_volume = float(str(sample.getField('Volume').get(sample))) - float(aliquot['volume'])
                        # New aliquot volume too large.  Dont create aliquote.  return a warning.
                        if new_volume < 0:
                            self.sample_results.append('Aliquot %s volume %s exceed remaining sample volume %s for sample %s'
                                                       % (aliquot['barcode'], aliquot['volume'],
                                                          sample.getField('Volume').get(sample), sample.Title()))
                            continue

                        new_aliquot = self.create_aliquot(sample, aliquot)
                        if new_aliquot:
                            # Subtract the new aliquot volume from the parent sample volume
                            sample.getField('Volume').set(sample, str(new_volume))
                            sample.reindexObject()

                            # Set the storage location for the new aliquot
                            new_aliquot.edit(
                                StorageLocation=storage_location
                            )

                            new_aliquot.reindexObject()
                            if storage_location:
                                doActionFor(storage_location, 'occupy')

                            self.sample_results.append('Successfully created aliquot with barcode %s and volume %s for sample %s'
                                                  % (aliquot['barcode'], aliquot['volume'], sample.Title()))

                    except Exception as e:
                        self.sample_results.append("Error creating aliquot with barcode %s and volume %s for sample %s."
                            % (aliquot['barcode'], aliquot['volume'], sample.Title()))
                        continue

            except Exception as e:
                self.sample_results.append('Exception occurred when creating aliquots.  %s' % str(e))
                continue

        return json.dumps(self.sample_results)

    def get_sample(self, sample_uid):
        # pc = getToolByName(self.context, 'portal_catalog')
        try:
            brains = self.pc(UID=sample_uid)
            return brains[0].getObject()
        except Exception as e:
            return None

    def create_aliquot(self, parent_sample,  aliquot):

        try:
            parent = parent_sample.aq_parent
            unit = parent_sample.getField('Unit').get(parent_sample)
            sample_type = parent_sample.getField('SampleType').get(parent_sample)

            obj = _createObjectByType('Sample', parent, tmpID())

            # Only change date created if a valid date created was send from client
            # If date created is there and time create is there as well create a date time object
            date_created = aliquot.get('datecreated', None)
            time_created = aliquot.get('timecreated', None)
            if date_created and time_created:
                date_created = date_created + ' ' + time_created
            if date_created:
                obj.edit(
                    DateCreated=date_created,
                )

            obj.edit(
                title=aliquot['barcode'],
                description='',
                Project=parent,
                DiseaseOntology=parent_sample.getField('DiseaseOntology').get(parent_sample),
                Donor=parent_sample.getField('Donor').get(parent_sample),
                SampleType=sample_type,
                SubjectID=parent_sample.getField('SubjectID').get(parent_sample),
                Barcode=aliquot['barcode'],
                Volume=aliquot['volume'],
                Unit=unit,
                SamplingDate=parent_sample.getField('SamplingDate').get(parent_sample),
                LinkedSample=parent_sample
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            return obj

        except Exception as e:
            return None