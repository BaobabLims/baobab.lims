# import os
# import traceback

from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
# from Products.Archetypes.public import BaseFolder
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

#from Products.Five.browser import BrowserView
from bika.lims.browser import BrowserView
# from bika.lims.browser.bika_listing import BikaListingView
# from bika.lims.browser.multifile import MultifileView
# from bika.lims.utils import to_utf8
# from baobab.lims import bikaMessageFactory as _
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime
from baobab.lims.browser.biospecimen.sample import EditView as BEV


class VirusSampleView(BrowserView):
    template = ViewPageTemplateFile('templates/virus_sample_view.pt')

    def __init__(self, context, request):
        super(VirusSampleView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.virus_sample_uid = self.context.UID()
        self.title = self.context.Title()
        self.project = self.context.aq_parent.Title()
        self.sample_type = self.context.getSampleType().Title()
        self.volume = "%s %s" % (self.context.Volume, self.context.Unit)
        self.anatomical_material = self.getObjectTitle(self.context.getAnatomicalMaterial())
        self.allow_sharing = self.context.AllowSharing
        self.will_return = self.context.WillReturnFromShipment
        self.bio_sample_accenssion = self.context.BioSampleAccession
        self.specimen_collector_sample_id = self.context.getSpecimenCollectorSampleID()
        self.sample_collected_by = self.context.getSampleCollectedBy()

        self.sample_collection_date = self.context.getSampleCollectionDate()
        self.sample_received_date = self.context.getSampleReceivedDate()
        # PhysicalAddress,
        self.geo_loc_country = self.context.getGeoLocCountry()
        self.geo_loc_state = self.context.getGeoLocState()
        self.organism = self.getObjectTitle(self.context.getOrganism())
        self.isolate = self.context.getIsolate()
        self.purpose_of_sampling = self.context.getPurposeOfSampling()
        self.collection_device = self.getObjectTitle(self.context.getCollectionDevice())
        self.collection_protocol = self.context.getCollectionProtocol()
        self.specimen_processing = self.context.getSpecimenProcessing()
        self.lab_host = self.getObjectTitle(self.context.getLabHost())
        self.passage_number = self.context.getPassageNumber()
        self.passage_method = self.context.getPassageMethod()
        self.host_subject_id = self.context.getHostSubjectID()
        self.host = self.getObjectTitle(self.context.getHost())
        self.host_disease = self.getObjectTitle(self.context.getHostDisease())
        self.host_gender = self.context.getHostGender()
        self.host_age = self.context.getHostAge()
        self.host_age_unit = self.context.getHostAgeUnit()
        self.exposure_country = self.context.getExposureCountry()
        self.exposure_event = self.context.getExposureEvent()
        # ExposureState,
        self.library_id = self.context.getLibraryID()
        self.instrument_type = self.getObjectTitle(self.context.getInstrumentType())
        self.instrument = self.getObjectTitle(self.context.getInstrument())
        self.sequencing_protocol_name = self.context.getSequencingProtocolName()

        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

    def getObjectTitle(self, obj):
        try:
            return obj.Title()
        except:
            return ''

    def get_fields_with_visibility(self, visibility, schemata, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():

            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:

                if field.schemata == schemata:
                    fields.append(field)

        return fields


class VirusSampleEditView(BEV):

    template = ViewPageTemplateFile('templates/sample_edit.pt')
    def __init__(self, context, request):
        super(VirusSampleEditView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):
        request = self.request
        context = self.context

        if 'submitted' in request:

            audit_logger = AuditLogger(self.context, 'VirusSample')

            from Products.CMFPlone.utils import _createObjectByType
            from bika.lims.utils import tmpID
            pc = getToolByName(context, "portal_catalog")
            folder = pc(portal_type="Project", UID=request.form['Project_uid'])[0].getObject()

            new_sample = False
            if not folder.hasObject(context.getId()):
                sample = _createObjectByType('VirusSample', folder, tmpID())
                new_sample = True
            else:
                sample = context
                self.perform_sample_audit(sample, request)
            form  = request.form

            sample.getField('Project').set(sample, form['Project_uid'])
            sample.getField('AllowSharing').set(sample, form['AllowSharing'])
            sample.getField('Kit').set(sample, form['Kit_uid'])
            sample.getField('StorageLocation').set(sample, form['StorageLocation_uid'])
            # sample.getField('SubjectID').set(sample, form['SubjectID'])
            sample.getField('Barcode').set(sample, form['Barcode'])
            sample.getField('Volume').set(sample, form['Volume'])
            sample.getField('Unit').set(sample, form['Unit'])
            sample.getField('LinkedSample').set(sample, form['LinkedSample_uid'])
            # Virus Sample fields
            sample.getField('AnatomicalMaterial').set(sample, form['AnatomicalMaterial'])
            sample.getField('BioSampleAccession').set(sample, form['BioSampleAccession'])
            sample.getField('SpecimenCollectorSampleID').set(sample, form['SpecimenCollectorSampleID'])
            sample.getField('SampleCollectedBy').set(sample, form['SampleCollectedBy'])
            sample.getField('SampleCollectionDate').set(sample, form['SampleCollectionDate'])
            sample.getField('SampleReceivedDate').set(sample, form['SampleReceivedDate'])
            sample.getField('GeoLocCountry').set(sample, form['GeoLocCountry'])
            # sample.getField('GeoLocState').set(sample, form['GeoLocState'])
            sample.getField('Organism').set(sample, form['Organism'])
            sample.getField('Isolate').set(sample, form['Isolate'])
            sample.getField('PurposeOfSampling').set(sample, form['PurposeOfSampling'])
            sample.getField('CollectionDevice').set(sample, form['CollectionDevice'])
            sample.getField('CollectionProtocol').set(sample, form['CollectionProtocol'])
            sample.getField('SpecimenProcessing').set(sample, form['SpecimenProcessing'])
            sample.getField('LabHost').set(sample, form['LabHost'])
            sample.getField('PassageNumber').set(sample, form['PassageNumber'])
            sample.getField('PassageMethod').set(sample, form['PassageMethod'])
            sample.getField('HostSubjectID').set(sample, form['HostSubjectID'])
            sample.getField('Host').set(sample, form['Host'])
            sample.getField('HostDisease').set(sample, form['HostDisease'])
            sample.getField('HostGender').set(sample, form['HostGender'])
            sample.getField('HostAge').set(sample, form['HostAge'])
            sample.getField('HostAgeUnit').set(sample, form['HostAgeUnit'])
            sample.getField('ExposureCountry').set(sample, form['ExposureCountry'])
            sample.getField('ExposureEvent').set(sample, form['ExposureEvent'])
            sample.getField('LibraryID').set(sample, form['LibraryID'])
            # sample.getField('InstrumentType,').set(sample, form[''])
            # sample.getField('Instrument,').set(sample, form[''])
            sample.getField('SequencingProtocolName').set(sample, form['SequencingProtocolName'])

            sample.edit(
                SampleType=form['SampleType_uid']
            )
            sample_batch = sample.getField('Batch').get(sample)
            sample.processForm()
            sample.getField('Batch').set(sample, sample_batch)

            obj_url = sample.absolute_url_path()

            if new_sample:
                audit_logger.perform_simple_audit(sample, 'New')
            request.response.redirect(obj_url)

            return

        return self.template()


