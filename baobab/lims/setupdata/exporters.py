from Products.CMFCore.utils import getToolByName
from bika.lims.utils import to_utf8
from baobab.lims.utils.retrieve_objects import *
from baobab.lims.extenders.sample import Sample

class LabDataExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_lab_data = []

        lab = self.context.bika_setup.laboratory
        dict = {}
        dict['Title'] = lab.Title()
        dict['URL'] = lab.getLabURL()
        try:
            dict['Postal Address'] = self.getAddress(lab.getPostalAddress())
        except:
            dict['Postal Address'] = ''
        try:
            dict['Billing Address'] = self.getAddress(lab.getBillingAddress())
        except:
            dict['Billing Address'] = ''
        try:
            dict['Physical Address'] = self.getAddress(lab.getPhysicalAddress())
        except:
            dict['Physical Address'] = ''
        dict['Confidence'] = lab.getConfidence()
        dict['Accredited'] = lab.getLaboratoryAccredited()
        dict['Accreditation Body'] = to_utf8(lab.getAccreditationBody())
        # dict['Accreditation Logo'] = lab.getAccreditationLogo()

        list_of_lab_data.append(dict)
        return self.get_headings(), list_of_lab_data

    def getAddress(self, address):

        out_address = ', '.join(str(x) for x in address.values())
        return out_address

    def get_headings(self):
        headings = [
            'Title',
            'URL',
            'Postal Address',
            'Billing Address',
            'Physical Address',
            'Confidence',
            'Accredited',
            'Accreditation Body',
        ]

        return headings


class ProjectsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_projects = []

        pc = getToolByName(self.context, 'portal_catalog')
        project_brains = pc(portal_type="Project")
        print('----------------projects')
        print(project_brains)
        if project_brains:
            list_of_projects.append(['Title', 'Description', 'StudyType', 'EthicsFormLink', 'AgeHigh', 'AgeLow',
                                     'NumParticipants', 'Biospecimen_Types', 'Client', 'Client_ID',
                                     'Date_Created', 'Project_ID', 'UID', 'Parent_UID', 'URL_path',
                                     'Portal_URL'])

        portal_url = getToolByName(self.context, "portal_url").getPortalObject().absolute_url()
        for brain in project_brains:
            project = brain.getObject()
            if project:
                row = []
                row.append(str(project.Title()))
                row.append(str(project.Description()).rstrip())
                row.append(str(project.getField('StudyType').get(project)))
                row.append(str(project.getField('EthicsFormLink').get(project)))
                row.append(project.getField('AgeHigh').get(project))
                row.append(project.getField('AgeLow').get(project))
                row.append(project.getField('NumParticipants').get(project))
                pc = getToolByName(self.context, 'portal_catalog')
                biospecimen_types = project.getField('SampleType').get(project)
                biospecimen_titles = []
                if biospecimen_types:
                    for sample_type_uid in biospecimen_types:
                        for i in pc(portal_type='SampleType', inactive_state='active'):
                            if i.UID == sample_type_uid:
                                biospecimen_titles.append(i.Title)
                                break
                row.append(str(biospecimen_titles))

                row.append(project.aq_parent.Title() if project.aq_parent.Title() else '')
                row.append(project.getClientID() if project.getClientID() else '')
                row.append(project.getField('DateCreated').get(project).strftime("%Y-%m-%d %H:%M") if project.getField('DateCreated').get(project) else '')

                row.append(str(project.getId()))
                row.append(project.UID())
                row.append(project.aq_parent.UID() if project.aq_parent.UID() else '')
                row.append(brain.getPath() if brain.getPath() else '')
                row.append(portal_url)
                list_of_projects.append(row)

        return list_of_projects

class SamplesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        samples = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="Sample")

        if brains:
            samples.append(['Title', 'Project_Visit_Type', 'Sample_Type','Storage_Location', 'Sampling_Time',
                            'Subject_ID', 'Barcode_Kit_ID', 'Volume', 'Unit', 'Sample_State',
                            'Date_Created', 'SampleID_field',
                            'Sample_ID', 'UID', 'Parent_UID', 'URL_path'])
        for brain in brains:
            try:
                sample = brain.getObject()

                row = []
                row.append(sample.Title())
                project = sample.aq_parent
                row.append(project.Title())
                row.append(sample.getSampleType().Title())
                storage = sample.getField('StorageLocation').get(sample)
                if storage:
                    row.append(storage.getHierarchy())
                else:
                    row.append('')
                row.append(sample.getSamplingDate().strftime("%Y-%m-%d %H:%M") if sample.getSamplingDate() else '')
                row.append(sample.getField('SubjectID').get(sample))
                row.append(sample.getField('Barcode').get(sample))
                row.append(sample.getField('Volume').get(sample))
                row.append(sample.getField('Unit').get(sample))

                row.append(sample.getSampleState())
                row.append(sample.getField('DateCreated').get(sample).strftime("%Y-%m-%d %H:%M") if sample.getField('DateCreated').get(sample) else '')
                row.append(sample.getField('SampleID').get(sample))

                row.append(sample.getId() if sample.getId() else '')
                row.append(sample.UID())
                row.append(sample.aq_parent.UID() if sample.aq_parent.UID() else '')
                row.append(brain.getPath() if brain.getPath() else '')

                samples.append(row)
            except:
                pass
        return samples


class VirusSamplesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        virus_samples = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="VirusSample")

        if brains:
            virus_samples.append(['Title', 'Project', 'Sample_Type',
                            'Storage_Location', 'Subject_ID', 'Barcode', 'Volume', 'Unit',
                            'Anatomical_Material', 'Bio_Sample_Accession','Specimen_Collector_Sample_ID',
                            'Sample_Collected_By', 'Sample_Collection_Date', 'Sample_Received_Date', 'Geo_Loc_Country',
                            'Geo_Loc_State', 'Organism', 'Isolate', 'Purpose_Of_Sampling', 'Collection_Device',
                            'Collection_Protocol', 'Exposure_Event', 'Specimen_Processing', 'Lab_Host', 'Passage_Number',
                            'Passage_Method', 'Host_Subject_ID', 'Host', 'Host_Disease', 'Host_Gender', 'Host_Age',
                            'Host_Age_Unit', 'Exposure_Country', 'Exposure_Event',
                            'Library_ID', 'Instrument_Type', 'Instrument', 'Sequencing_Protocol_Name',
                            'Date_Created', 'Sample_ID', 'UID', 'Parent_UID', 'URL_path'])
        for brain in brains:
            virus_sample = brain.getObject()

            row = []
            row.append(virus_sample.Title())
            project = virus_sample.getField('Project').get(virus_sample)
            row.append(project.Title())
            row.append(virus_sample.getSampleType().Title())
            # disease_ontology = virus_sample.getField('DiseaseOntology').get(virus_sample)
            # if disease_ontology:
            #     row.append(disease_ontology.Title())
            # else:
            #     row.append('')
            #
            # donor = virus_sample.getField('Donor').get(virus_sample)
            # if donor:
            #     row.append(donor.Title())
            # else:
            #     row.append('')

            storage = virus_sample.getField('StorageLocation').get(virus_sample)
            if storage:
                row.append(storage.getHierarchy())
            else:
                row.append('')
            row.append(virus_sample.getField('SubjectID').get(virus_sample))
            row.append(virus_sample.getField('Barcode').get(virus_sample))
            row.append(virus_sample.getField('Volume').get(virus_sample))
            row.append(virus_sample.getField('Unit').get(virus_sample))
            anatomical_material = virus_sample.getAnatomicalMaterial()
            if anatomical_material:
                row.append(anatomical_material.Title())
            else:
                row.append('')

            row.append(virus_sample.getField('BioSampleAccession').get(virus_sample))
            row.append(virus_sample.getField('SpecimenCollectorSampleID').get(virus_sample))
            row.append(virus_sample.getField('SampleCollectedBy').get(virus_sample))
            row.append(virus_sample.getField('SampleCollectionDate').get(virus_sample))
            row.append(virus_sample.getField('SampleReceivedDate').get(virus_sample))
            row.append(virus_sample.getField('GeoLocCountry').get(virus_sample))
            row.append(virus_sample.getField('GeoLocState').get(virus_sample))

            organism = virus_sample.getOrganism()
            if organism:
                row.append(organism.Title())
            else:
                row.append('')

            row.append(virus_sample.getField('Isolate').get(virus_sample))
            row.append(virus_sample.getField('PurposeOfSampling').get(virus_sample))
            collection_device = virus_sample.getCollectionDevice()
            if collection_device:
                row.append(collection_device.Title())
            else:
                row.append('')
            row.append(virus_sample.getField('CollectionProtocol').get(virus_sample))
            row.append(virus_sample.getField('ExposureEvent').get(virus_sample))
            row.append(virus_sample.getField('SpecimenProcessing').get(virus_sample))
            lab_host = virus_sample.getLabHost()
            if lab_host:
                row.append(lab_host.Title())
            else:
                row.append('')
            row.append(virus_sample.getField('PassageNumber').get(virus_sample))
            row.append(virus_sample.getField('PassageMethod').get(virus_sample))
            row.append(virus_sample.getField('HostSubjectID').get(virus_sample))
            host = virus_sample.getHost()
            if host:
                row.append(host.Title())
            else:
                row.append('')
            host_disease = virus_sample.getHostDisease()
            if host_disease:
                row.append(host_disease.Title())
            else:
                row.append('')
            row.append(virus_sample.getField('HostGender').get(virus_sample))
            row.append(virus_sample.getField('HostAge').get(virus_sample))
            row.append(virus_sample.getField('HostAgeUnit').get(virus_sample))
            row.append(virus_sample.getField('ExposureCountry').get(virus_sample))
            row.append(virus_sample.getField('ExposureEvent').get(virus_sample))
            row.append(virus_sample.getField('LibraryID').get(virus_sample))
            instrument_type = virus_sample.getInstrumentType()
            if instrument_type:
                row.append(instrument_type.Title())
            else:
                row.append('')
            instrument = virus_sample.getInstrument()
            if instrument:
                row.append(instrument.Title())
            else:
                row.append('')
            row.append(virus_sample.getField('SequencingProtocolName').get(virus_sample))

            # row.append(sample.getSampleState())
            # row.append(sample.getSamplingDate().strftime("%Y-%m-%d %H:%M") if sample.getSamplingDate() else '')
            row.append(virus_sample.getField('DateCreated').get(virus_sample).strftime("%Y-%m-%d %H:%M") if virus_sample.getField('DateCreated').get(virus_sample) else '')

            row.append(virus_sample.getId() if virus_sample.getId() else '')
            row.append(virus_sample.UID())
            row.append(virus_sample.aq_parent.UID() if virus_sample.aq_parent.UID() else '')
            row.append(brain.getPath() if brain.getPath() else '')

            virus_samples.append(row)
        return virus_samples


# class SamplesAliquotExporter(object):
#     """ This class packages all the samples info into a list of dictionaries and then returns it.
#         Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
#     """
#     def __init__(self, context):
#         self.context = context
#
#     def export(self):
#         aliquots = []
#         pc = getToolByName(self.context, 'portal_catalog')
#         brains = pc(portal_type="Sample")
#         if brains:
#             aliquots.append(['Title', 'Sample_Type', 'Subject_ID', 'Barcode', 'Volume',
#                              'Unit', 'Storage', 'Sample_State', 'Sampling_Time',
#                              'Parent_Biospecimen_Kit_ID', 'Batch_ID', 'Date_Created', 'SampleID_field',
#                              'Aliquot_ID', 'UID', 'Parent_ID', 'URL_path'])
#         for brain in brains:
#             sample = brain.getObject()
#             parent_sample = sample.getField('LinkedSample').get(sample)
#             if parent_sample:
#
#                 batch = sample.getField('Batch').get(sample) and sample.getField('Batch').get(sample).Title() or ''
#                 row = []
#                 row.append(sample.Title())
#                 row.append(sample.getSampleType().Title())
#                 row.append(sample.getField('SubjectID').get(sample))
#                 row.append(sample.getField('Barcode').get(sample))
#                 row.append(sample.getField('Volume').get(sample))
#                 row.append(sample.getField('Unit').get(sample))
#
#                 storage = sample.getField('StorageLocation').get(sample)
#                 if storage:
#                     row.append(storage.getHierarchy())
#                 else:
#                     row.append('')
#                 row.append(sample.getSampleState())
#                 row.append(sample.getField('SamplingDate').get(sample).strftime("%Y-%m-%d %H:%M") if sample.getField('SamplingDate').get(sample) else '')
#                 row.append(parent_sample.getField('Barcode').get(parent_sample))
#                 row.append(batch)
#
#                 row.append(sample.getField('DateCreated').get(sample).strftime("%Y-%m-%d %H:%M") if sample.getField('DateCreated').get(sample) else '')
#                 row.append(sample.getField('SampleID').get(sample))
#
#                 # # last_modified_user = sample.getField('ChangeUserName').get(sample)
#                 # last_modified_user = 'last modify user here'
#                 # last_modified_date = ''
#                 # # if sample.getField('ChangeDateTime').get(sample):
#                 # #     last_modified_date = sample.getField('ChangeDateTime').get(sample).strftime("%Y-%m-%d %H:%M")
#                 # row.append(last_modified_user)
#                 # row.append(last_modified_date)
#
#                 row.append(sample.getId() if sample.getId() else '')
#                 row.append(sample.UID())
#                 row.append(sample.aq_parent.UID() if sample.aq_parent.UID() else '')
#                 row.append(brain.getPath() if brain.getPath() else '')
#
#                 aliquots.append(row)
#         return aliquots
#

class SampleShipmentExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        sample_shipments = []
        pc = getToolByName(self.context, 'bika_catalog')
        brains = pc(portal_type="SampleShipment")

        if brains:
            sample_shipments.append(['Title', 'Description', 'Date_Delivered', 'Date_Dispatched',
                                     'Shipping_Date', 'Samples', 'Volume','Weight', 'Shipping_Cost', 'Shipping_Conditions',
                                     'Tracking_URL', 'Courier_Instructions', 'Courier', 'Billing_Address',
                                     'Delivery_Address', 'Client', 'Receiver_Email_Address', 'Sender_Email_Address',
                                     'SampleShipment_ID', 'UID', 'Parent_UID', 'URL_path'])

        for brain in brains:
            shipment = brain.getObject()
            if shipment:
                row = []
                row.append(shipment.Title())
                row.append(str(shipment.Description()).rstrip())
                row.append(shipment.getField('DateDelivered').get(shipment).strftime("%Y-%m-%d %H:%M") if shipment.getField('DateDelivered').get(shipment) else '')
                row.append(shipment.getField('DateDispatched').get(shipment).strftime("%Y-%m-%d %H:%M") if shipment.getField('DateDispatched').get(shipment) else '')
                row.append(shipment.getField('ShippingDate').get(shipment).strftime("%Y-%m-%d %H:%M") if shipment.getField('ShippingDate').get(shipment) else '')
                row.append(str([sample.id for sample in shipment.getField('SamplesList').get(shipment)]) if shipment.getField('SamplesList') else '')
                row.append(str(shipment.getField('Volume').get(shipment)) if shipment.getField('Volume') else '')
                row.append(str(shipment.getField('Weight').get(shipment)) if shipment.getField('Weight') else '')
                row.append(str(shipment.getField('ShippingCost').get(shipment)) if shipment.getField('ShippingCost') else '')
                row.append(str(shipment.getField('ShipmentConditions').get(shipment)) if shipment.getField('ShipmentConditions') else '')
                row.append(str(shipment.getField('TrackingURL').get(shipment)) if shipment.getField('TrackingURL') else '')
                row.append(str(shipment.getField('CourierInstructions').get(shipment)) if shipment.getField('CourierInstructions') else '')
                row.append(str(shipment.getField('Courier').get(shipment)))
                row.append(str(shipment.getField('BillingAddress').get(shipment)) if shipment.getField('BillingAddress') else '')
                row.append(str(shipment.getField('DeliveryAddress').get(shipment)))
                row.append(str(shipment.getField('Client').get(shipment).ClientID))
                row.append(str(shipment.getField('ToEmailAddress').get(shipment)) if shipment.getField('ToEmailAddress') else '')
                row.append(str(shipment.getField('FromEmailAddress').get(shipment)) if shipment.getField('FromEmailAddress') else '')

                # last_modified_user = shipment.getField('ChangeUserName').get(shipment)
                # last_modified_date = ''
                # if shipment.getField('ChangeDateTime').get(shipment):
                #     last_modified_date = shipment.getField('ChangeDateTime').get(shipment).strftime("%Y-%m-%d %H:%M")
                # row.append(last_modified_user)
                # row.append(last_modified_date)

                row.append(shipment.getId() if shipment.getId() else '')
                row.append(shipment.UID())
                row.append(shipment.aq_parent.UID() if shipment.aq_parent.UID() else '')
                row.append(brain.getPath() if brain.getPath() else '')

                sample_shipments.append(row)
        return sample_shipments

class ViralGenomicAnalysisExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        vgas = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="ViralGenomicAnalysis")

        if brains:
            vgas.append(['Title', 'Description', 'Project', 'Date_Created', 'WillExtract',
                                     'WillAliquot', 'WillQuantify','WillViralLoadDetermine',
                                     'WillLibraryPrep', 'VGA_ID', 'UID', 'Parent_UID', 'URL_path'])

        for brain in brains:
            vga = brain.getObject()
            if vga:
                row = []
                row.append(vga.Title())
                row.append(str(vga.Description()).rstrip())
                project = vga.getProject()
                if project:
                    row.append(project.Title())
                else:
                    row.append('')
                row.append(vga.getField('DateCreated').get(vga).strftime("%Y-%m-%d %H:%M") if vga.getField('DateCreated').get(vga) else '')
                row.append(str(vga.getField('WillExtract').get(vga)) if vga.getField('WillExtract') else '')
                row.append(str(vga.getField('WillAliquot').get(vga)) if vga.getField('WillAliquot') else '')
                row.append(str(vga.getField('WillQuantify').get(vga)) if vga.getField('WillQuantify') else '')
                row.append(str(vga.getField('WillViralLoadDetermine').get(vga)) if vga.getField('WillViralLoadDetermine') else '')
                row.append(str(vga.getField('WillLibraryPrep').get(vga)) if vga.getField('WillLibraryPrep') else '')

                row.append(vga.getId() if vga.getId() else '')
                row.append(vga.UID())
                row.append(vga.aq_parent.UID() if vga.aq_parent.UID() else '')
                row.append(brain.getPath() if brain.getPath() else '')

                vgas.append(row)
        return vgas


class ExtractGenomicMaterialExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        egms = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="ViralGenomicAnalysis")

        if brains:
            egms.append(['VGA', 'Title', 'Extraction_Barcode', 'Virus_Sample',
                                     'Heat_Inactivated', 'Method', 'Extraction_Barcode','Volume',
                                     'Unit', 'Was_Kit_Used', 'Kit_Number', 'Notes',])

        for brain in brains:
            vga = brain.getObject()
            extract_genomic_materials = vga.getExtractGenomicMaterial()

            for egm in extract_genomic_materials:

                if egm:
                    row = []
                    row.append(vga.Title())
                    row.append(str(egm['ExtractionBarcode'] if 'ExtractionBarcode' in egm else ''))
                    virus_sample = get_object_from_uid(self.context, egm['VirusSample'])
                    try:
                        row.append(virus_sample.Title())
                    except:
                        row.append('')
                    row.append(str(egm['HeatInactivated'] if 'HeatInactivated' in egm else ''))
                    method = get_object_from_uid(self.context, egm['Method'])
                    try:
                        row.append(method.Title())
                    except:
                        row.append('')
                    row.append(str(egm['ExtractionBarcode'] if 'ExtractionBarcode' in egm else ''))
                    row.append(str(egm['Volume'] if 'Volume' in egm else ''))
                    row.append(str(egm['Unit'] if 'Unit' in egm else ''))
                    row.append(str(egm['WasKitUsed'] if 'WasKitUsed' in egm else ''))
                    row.append(str(egm['KitNumber'] if 'KitNumber' in egm else ''))
                    row.append(str(egm['Notes'] if 'Notes' in egm else ''))

                    # row.append(egm.getId() if egm.getId() else '')
                    # row.append(egm.UID())
                    # row.append(egm.aq_parent.UID() if egm.aq_parent.UID() else '')
                    # row.append(brain.getPath() if brain.getPath() else '')

                    egms.append(row)
        return egms


class GenomeQuantificationExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        gqs = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="ViralGenomicAnalysis")

        if brains:
            gqs.append(['VGA', 'Virus_Sample', 'Fluorimeter_Conc_(ng/ul)',
                        'Nanometer_Conc_(ng/ul)', 'Nanometer Ratio_(260/280)',])

        for brain in brains:
            vga = brain.getObject()
            genome_quantifications = vga.getGenomeQuantification()

            for gq in genome_quantifications:

                if gq:
                    row = []
                    row.append(vga.Title())
                    virus_sample = get_object_from_uid(self.context, gq['VirusSampleRNAorDNA'])
                    try:
                        row.append(virus_sample.Title())
                    except:
                        row.append('')
                    row.append(str(gq['FluorimeterConc'] if 'FluorimeterConc' in gq else ''))
                    row.append(str(gq['NanometerQuantity'] if 'NanometerQuantity' in gq else ''))
                    row.append(str(gq['NanometerRatio'] if 'NanometerRatio' in gq else ''))

                    # row.append(egm.getId() if egm.getId() else '')
                    # row.append(egm.UID())
                    # row.append(egm.aq_parent.UID() if egm.aq_parent.UID() else '')
                    # row.append(brain.getPath() if brain.getPath() else '')

                    gqs.append(row)
        return gqs


class ViralLoadDeterminationExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        vlds = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="ViralGenomicAnalysis")

        if brains:
            vlds.append(['VGA', 'Virus_Sample', 'ctValue', 'Kit_Number',
                         'result', 'Verification', 'AddToReport', 'Notes',])

        for brain in brains:
            vga = brain.getObject()
            viral_load_determinations = vga.getViralLoadDetermination()

            for vld in viral_load_determinations:

                if vld:

                    row = []
                    row.append(vga.Title())
                    virus_sample = get_object_from_uid(self.context, vld['VirusSampleRNAorDNA'])
                    try:
                        row.append(virus_sample.Title())
                    except:
                        row.append('')
                    row.append(str(vld['ctValue'] if 'ctValue' in vld else ''))
                    row.append(str(vld['KitNumber'] if 'KitNumber' in vld else ''))
                    row.append(str(vld['Result'] if 'Result' in vld else ''))
                    row.append(str(vld['Verification'] if 'Verification' in vld else ''))
                    row.append(str(vld['AddToReport'] if 'AddToReport' in vld else ''))
                    row.append(str(vld['Notes'] if 'Notes' in vld else ''))

                    # row.append(egm.getId() if egm.getId() else '')
                    # row.append(egm.UID())
                    # row.append(egm.aq_parent.UID() if egm.aq_parent.UID() else '')
                    # row.append(brain.getPath() if brain.getPath() else '')

                    vlds.append(row)
        return vlds


class SequenceLibraryPrepExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        vlds = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="ViralGenomicAnalysis")

        if brains:
            vlds.append(['VGA', 'Virus_sample', 'Method', 'Kit_Number', 'Notes',])

        for brain in brains:
            vga = brain.getObject()
            sequence_library_preps = vga.getSequencingLibraryPrep()

            for slp in sequence_library_preps:

                if slp:
                    row = []
                    row.append(vga.Title())

                    virus_sample = get_object_from_uid(self.context, slp['VirusSampleRNAorDNA'])
                    try:
                        row.append(virus_sample.Title())
                    except:
                        row.append('')
                    method = get_object_from_uid(self.context, slp['Method'])
                    try:
                        row.append(method.Title())
                    except:
                        row.append('')
                    row.append(str(slp['KitNumber'] if 'KitNumber' in slp else ''))
                    row.append(str(slp['Notes'] if 'Notes' in slp else ''))

                    # row.append(egm.getId() if egm.getId() else '')
                    # row.append(egm.UID())
                    # row.append(egm.aq_parent.UID() if egm.aq_parent.UID() else '')
                    # row.append(brain.getPath() if brain.getPath() else '')

                    vlds.append(row)
        return vlds