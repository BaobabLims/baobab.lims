# import os
# import traceback

from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
# from Products.Archetypes.public import BaseFolder
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.app.content.browser.interfaces import IFolderContentsView
# from plone.app.layout.globals.interfaces import IViewView
# from zope.interface import implements

#from Products.Five.browser import BrowserView
from bika.lims.browser import BrowserView
# from bika.lims.browser.bika_listing import BikaListingView
# from bika.lims.browser.multifile import MultifileView
# from bika.lims.utils import to_utf8
# from baobab.lims import bikaMessageFactory as _
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime


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
        self.project = self.context.getProject().Title()
        self.sample_type = self.context.getSampleType().Title()
        self.volume = "%s %s" % (self.context.getVolume(), self.context.getUnit())
        self.anatomical_material = self.getObjectTitle(self.context.getAnatomicalMaterial())
        self.allow_sharing = self.context.getAllowSharing()
        self.will_return = self.context.getWillReturnFromShipment()
        self.bio_sample_accenssion = self.context.getBioSampleAccession()
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
