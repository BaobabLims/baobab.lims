from Products.CMFCore.utils import getToolByName
from bika.lims.utils import to_utf8


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
            # 'Accreditation Logo',
        ]

        return headings


# class LabDepartmentsExporter(object):
#     """ This class packages all the samples info into a list of dictionaries and then returns it.
#     """
#
#     def __init__(self, context):
#         self.context = context
#
#     def export(self):
#         list_of_lab_departments= []
#
#         pc = getToolByName(self.context, 'portal_catalog')
#         lab_department_brains = pc(portal_type="LabDepartment")
#         print('===brains========')
#
#         for brain in lab_department_brains:
#             lab_department = brain.getObject()
#             # print('-------------------')
#             # print(sample.__dict__)
#             dict = {}
#             dict['Title'] = lab_department.Title()
#             dict['Description'] = lab_department.Description()
#             # dict['RetentionPeriod'] = sample_type.getField('RetentionPeriod').get(sample_type)
#             dict['Hazardous'] = sample_type.getField('Hazardous').get(sample_type)
#             dict['Prefix'] = sample_type.getField('Prefix').get(sample_type)
#             dict['MinimumVolume'] = sample_type.getField('MinimumVolume').get(sample_type)
#
#             dict['UID'] = sample_type.UID()
#             try:
#                 dict['Parent_UID'] = sample_type.aq_parent.UID()
#             except:
#                 dict['Parent_UID'] = ''
#
#             list_of_sample_types.append(dict)
#
#         return self.get_headings(), list_of_sample_types
#
#     def get_headings(self):
#         headings = [
#             'Title',
#             'Description',
#             # 'RetentionPeriod',
#             'Hazardous',
#             'Prefix',
#             'MinimumVolume',
#             'UID',
#             'Parent_UID',
#         ]
#
#         return headings



class LabContactsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_lab_contacts = []

        pc = getToolByName(self.context, 'portal_catalog')
        lab_contact_brains = pc(portal_type="LabContact")
        print('===lab contact brains========')
        print(lab_contact_brains)

        for brain in lab_contact_brains:
            print('--------')

            lab_contact = brain.getObject()
            print(lab_contact.__dict__)
            dict = {}
            # dict['Title'] = 'This is a title'   #lab_contact.Title()
            # dict['Description'] = lab_contact.Description()
            dict['Salutation'] = lab_contact.getField('Salutation').get(lab_contact)
            dict['Firstname'] = lab_contact.getField('Firstname').get(lab_contact)
            dict['Surname'] = lab_contact.getField('Surname').get(lab_contact)
            dict['EmailAddress'] = lab_contact.getField('EmailAddress').get(lab_contact)
            dict['BusinessPhone'] = lab_contact.getField('BusinessPhone').get(lab_contact)
            dict['BusinessFax'] = lab_contact.getField('BusinessFax').get(lab_contact)
            dict['HomePhone'] = lab_contact.getField('HomePhone').get(lab_contact)
            dict['MobilePhone'] = lab_contact.getField('MobilePhone').get(lab_contact)
            dict['JobTitle'] = str(lab_contact.getField('JobTitle').get(lab_contact))
            # dict['Department'] = lab_contact.getField('Department').get(lab_contact)
            # dict['Username'] = lab_contact.getField('Username').get(lab_contact)
            # dict['Password'] = lab_contact.getField('Password').get(lab_contact)
            # dict['Groups'] = lab_contact.getField('Groups').get(lab_contact)
            # dict['Roles'] = lab_contact.getField('Roles').get(lab_contact)
            # dict['Signature'] = lab_contact.getField('Signature').get(lab_contact)
            dict['PhysicalAddress'] = self.getAddress(lab_contact.getField('PhysicalAddress').get(lab_contact))
            # dict['PhysicalCity'] = lab_contact.getField('PhysicalCity').get(lab_contact)
            # dict['PhysicalState'] = lab_contact.getField('PhysicalState').get(lab_contact)
            # dict['Physical_Zip'] = lab_contact.getField('Physical_Zip').get(lab_contact)
            # dict['Physical_Country'] = lab_contact.getField('Physical_Country').get(lab_contact)
            dict['PostalAddress'] = self.getAddress(lab_contact.getField('PostalAddress').get(lab_contact))

            # dict['Postal_City'] = lab_contact.getField('Postal_City').get(lab_contact)
            # dict['Postal_State'] = lab_contact.getField('Postal_State').get(lab_contact)
            # dict['Postal_Zip'] = lab_contact.getField('Postal_Zip').get(lab_contact)
            # dict['Postal_Country'] = lab_contact.getField('Postal_Country').get(lab_contact)
            # dict[''] = lab_contact.getField('').get(lab_contact)

            list_of_lab_contacts.append(dict)

        return self.get_headings(), list_of_lab_contacts

    def getAddress(self, address):

        out_address = ', '.join(str(x) for x in address.values())
        return out_address

    def get_headings(self):
        headings = [
            # 'Title',
            # 'Description',
            'Salutation',
            'Firstname',
            'Surname',
            'EmailAddress',
            'BusinessPhone',
            'BusinessFax',
            'HomePhone',
            'MobilePhone',
            'JobTitle',
            # 'Department',
            # 'Username',
            # 'Password',
            # 'Groups',
            # 'Roles',
            # 'Signature',
            'PhysicalAddress',
            # 'Physical_City',
            # 'Physical_State',
            # 'Physical_Zip',
            # 'Physical_Country',
            'PostalAddress',
            # 'Postal_City',
            # 'Postal_State',
            # 'Postal_Zip',
            # 'Postal_Country',
        ]

        return headings


class AnalysisCategoriesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_analysis_categories = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        analysis_category_brains = bsc(portal_type="AnalysisCategory")
        print('===brains========')

        for brain in analysis_category_brains:
            analysis_category = brain.getObject()
            # print('-------------------')
            # print(analysis_category.__dict__)
            dict = {}
            dict['Title'] = analysis_category.Title()
            dict['Description'] = analysis_category.Description()
            dict['Comments'] = analysis_category.getField('Comments').get(analysis_category)

            department = analysis_category.getField('Department').get(analysis_category)
            try:
                dict['Department'] = department.Title()
            except:
                dict['Department'] = ''

            dict['UID'] = analysis_category.UID()
            try:
                dict['Parent_UID'] = analysis_category.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_analysis_categories.append(dict)

        return self.get_headings(), list_of_analysis_categories

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'Comments',
            'Department',
            'UID',
            'Parent_UID',
        ]

        return headings

class AnalysisServicesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_analysis_services = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        analysis_service_brains = bsc(portal_type="AnalysisService")
        print('===brains========')

        for brain in analysis_service_brains:
            analysis_service = brain.getObject()
            # print('-------------------')
            # print(analysis_category.__dict__)
            dict = {}
            dict['Title'] = analysis_service.Title()
            dict['Description'] = analysis_service.Description()
            dict['ShortTitle'] = analysis_service.getField('ShortTitle').get(analysis_service)
            dict['Keyword'] = analysis_service.getField('Keyword').get(analysis_service)
            dict['PointOfCapture'] = analysis_service.getField('PointOfCapture').get(analysis_service)
            dict['Category'] = analysis_service.getField('Category').get(analysis_service)
            department = analysis_service.getField('Department').get(analysis_service)
            try:
                dict['Department'] = department.Title()
            except:
                dict['Department'] = ''
            dict['ReportDryMatter'] = analysis_service.getField('ReportDryMatter').get(analysis_service)
            dict['AttachmentOption'] = analysis_service.getField('AttachmentOption').get(analysis_service)
            dict['Unit'] = analysis_service.getField('Unit').get(analysis_service)
            dict['Precision'] = analysis_service.getField('Precision').get(analysis_service)
            dict['ExponentialFormatPrecision'] = analysis_service.getField('ExponentialFormatPrecision').get(analysis_service)
            dict['LowerDetectionLimit'] = analysis_service.getField('LowerDetectionLimit').get(analysis_service)
            dict['UpperDetectionLimit'] = analysis_service.getField('UpperDetectionLimit').get(analysis_service)
            dict['DetectionLimitSelector'] = analysis_service.getField('DetectionLimitSelector').get(analysis_service)
            dict['MaxTimeAllowed'] = analysis_service.getField('MaxTimeAllowed').get(analysis_service)
            dict['Price'] = analysis_service.getField('Price').get(analysis_service)
            dict['BulkPrice'] = analysis_service.getField('BulkPrice').get(analysis_service)
            # dict['VatAmount'] = analysis_service.getField('VatAmount').get(analysis_service)
            dict['TotalPrice'] = analysis_service.getField('TotalPrice').get(analysis_service)
            dict['Price'] = analysis_service.getField('Price').get(analysis_service)
            dict['BulkPrice'] = analysis_service.getField('BulkPrice').get(analysis_service)
            # dict['Vat'] = analysis_service.getField('Vat').get(analysis_service)
            dict['TotalPrice'] = analysis_service.getField('TotalPrice').get(analysis_service)
            dict['ManualEntryOfResults'] = analysis_service.getField('ManualEntryOfResults').get(analysis_service)
            #
            dict['Instruments'] = analysis_service.getField('Instruments').get(analysis_service)
            #
            dict['Methods'] = analysis_service.getField('Methods').get(analysis_service)

            dict['ScientificName'] = analysis_service.getField('ScientificName').get(analysis_service)
            dict['AllowManualDetectionLimit'] = analysis_service.getField('AllowManualDetectionLimit').get(analysis_service)
            dict['ReportDryMatter'] = analysis_service.getField('ReportDryMatter').get(analysis_service)
            dict['AttachmentOption'] = analysis_service.getField('AttachmentOption').get(analysis_service)
            dict['InstrumentEntryOfResults'] = analysis_service.getField('InstrumentEntryOfResults').get(analysis_service)
            #
            # dict['_Method'] = analysis_service.getField('_Method').get(analysis_service)
            dict['CalculationTitle'] = analysis_service.getField('CalculationTitle').get(analysis_service)
            dict['DuplicateVariation'] = analysis_service.getField('DuplicateVariation').get(analysis_service)
            dict['Accredited'] = analysis_service.getField('Accredited').get(analysis_service)
            dict['Separate'] = analysis_service.getField('Separate').get(analysis_service)
            # dict['Container'] = analysis_service.getField('Container').get(analysis_service)
            # dict['Preservation'] = analysis_service.getField('Preservation').get(analysis_service)

            # department = analysis_category.getField('Department').get(analysis_category)
            # try:
            #     dict['Department'] = department.Title()
            # except:
            #     dict['Department'] = ''

            dict['UID'] = analysis_service.UID()
            try:
                dict['Parent_UID'] = analysis_service.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_analysis_services.append(dict)

        return self.get_headings(), list_of_analysis_services

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'ShortTitle',
            'Keyword',
            'PointOfCapture',
            'Category',
            'Department',
            'ReportDryMatter',
            'AttachmentOption',
            'Unit',
            'Precision',
            'ExponentialFormatPrecision',
            'LowerDetectionLimit',
            'UpperDetectionLimit',
            'DetectionLimitSelector',
            'MaxTimeAllowed',
            'Price',
            'BulkPrice',
            # 'VatAmount',
            'TotalPrice',
            'Price',
            'BulkPrice',
            # 'Vat',
            'TotalPrice',
            'ManualEntryOfResults',
            #
            'Instruments',
            #
            'Methods',
            'ScientificName',
            'AllowManualDetectionLimit',
            'ReportDryMatter',
            'AttachmentOption',
            'InstrumentEntryOfResults',
            #
            #'_Method',
            'CalculationTitle',
            'DuplicateVariation',
            'Accredited',
            'Separate',
            #'Container',
            #'Preservation',
        ]

        return headings


class SampleTypesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_sample_types = []

        pc = getToolByName(self.context, 'portal_catalog')
        sample_type_brains = pc(portal_type="SampleType")
        print('===brains========')

        for brain in sample_type_brains:
            sample_type = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = sample_type.Title()
            dict['Description'] = sample_type.Description()
            # dict['RetentionPeriod'] = sample_type.getField('RetentionPeriod').get(sample_type)
            dict['Hazardous'] = sample_type.getField('Hazardous').get(sample_type)
            dict['Prefix'] = sample_type.getField('Prefix').get(sample_type)
            dict['MinimumVolume'] = sample_type.getField('MinimumVolume').get(sample_type)

            dict['UID'] = sample_type.UID()
            try:
                dict['Parent_UID'] = sample_type.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_sample_types.append(dict)

        return self.get_headings(), list_of_sample_types

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            # 'RetentionPeriod',
            'Hazardous',
            'Prefix',
            'MinimumVolume',
            'UID',
            'Parent_UID',
        ]

        return headings


class ClientsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_clients = []

        pc = getToolByName(self.context, 'portal_catalog')
        client_brains = pc(portal_type="Client")
        print('===brains========')

        for brain in client_brains:
            client = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = client.Title()
            dict['Description'] = client.Description()
            dict['EmailAddress'] = client.getEmailAddress()
            dict['Phone'] = client.getPhone()
            dict['Fax'] = client.getFax()
            dict['ClientID'] = client.getClientID()
            dict['BulkDiscount'] = client.getBulkDiscount()
            dict['MemberDiscountApplies'] = client.getMemberDiscountApplies()

            dict['UID'] = client.UID()
            try:
                dict['Parent_UID'] = client.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_clients.append(dict)

        return self.get_headings(), list_of_clients

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'EmailAddress',
            'Phone',
            'Fax',
            'ClientID',
            'BulkDiscount',
            'MemberDiscountApplies',
            'UID',
            'Parent_UID',
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
        print('===brains========')

        for brain in project_brains:
            project = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = project.Title()
            dict['Description'] = project.Description()
            dict['StudyType'] = project.getField('StudyType').get(project)
            dict['EthicsFormLink'] = project.getField('EthicsFormLink').get(project)
            dict['AgeHigh'] = project.getField('AgeHigh').get(project)
            dict['AgeLow'] = project.getField('AgeLow').get(project)
            dict['NumParticipants'] = project.getField('NumParticipants').get(project)
            # dict[''] = project.getField('').get(project)
            # dict[''] = project.getField('').get(project)
            # dict['DateCreated'] = project.getField('DateCreated').get(project)
            # dict[''] = project.getField('').get(project)

            # TODO:  Add service and sample typesz

            dict['UID'] = project.UID()
            try:
                dict['Parent_UID'] = project.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_projects.append(dict)

        return self.get_headings(), list_of_projects

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'StudyType',
            'EthicsFormLink',
            'AgeHigh',
            'AgeLow',
            'NumParticipants',
            # '',
            # '',
            # 'DateCreated',
            'UID',
            'Parent_UID',
        ]

        return headings


class SampleBatchesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_sample_batches = []

        bc = getToolByName(self.context, 'bika_catalog')
        sample_batch_brains = bc(portal_type="SampleBatch")
        # print('===brains========')

        for brain in sample_batch_brains:
            sample_batch = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = sample_batch.Title()
            dict['Description'] = sample_batch.Description()
            dict['BatchId'] = sample_batch.getField('BatchId').get(sample_batch)
            project = sample_batch.getField('Project').get(sample_batch)
            try:
                dict['Project'] = project.Title()
            except:
                dict['Project'] = ''

            linked_sample = sample_batch.getField('ParentBiospecimen').get(sample_batch)
            try:
                dict['ParentBiospecimen'] = linked_sample.Title()
            except:
                dict['ParentBiospecimen'] = ''

            storage = sample_batch.getField('StorageLocation').get(sample_batch)

            try:
                dict['StorageLocation'] = storage.getHierarchy()
            except:
                dict['StorageLocation'] = ''

            print_samples = []
            pc = getToolByName(self.context, 'portal_catalog')
            sample_brains = pc(portal_type='Sample', Batch=sample_batch.UID())
            for sample_brain in sample_brains:
                sample = sample_brain.getObject()
                # hack that is needed because stupid Plone cant search for the batch in a sample
                # it returns every bloody sample even though I specify the batch in the search.
                this_sample_batch = sample.getField('Batch').get(sample)
                if this_sample_batch and this_sample_batch.UID() == sample_batch.UID():
                    print('Batch is %s' % sample.getField('Batch').get(sample))
                    print_samples.append(sample.getField('Barcode').get(sample))
            dict['Samples'] = ', '.join(str(x) for x in print_samples)
            dict['DateCreated'] = sample_batch.getField('DateCreated').get(sample_batch)

            dict['UID'] = sample_batch.UID()
            try:
                dict['Parent_UID'] = sample_batch.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            # todo: also get the samples barcodes and publish them

            list_of_sample_batches.append(dict)

        return self.get_headings(), list_of_sample_batches

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'BatchId',
            'Project',
            'ParentBiospecimen',
            'DateCreated',
            # 'StorageLocations'
            'Samples',
            'UID',
            'Parent_UID',
        ]

        return headings


class SamplesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_samples = []

        pc = getToolByName(self.context, 'portal_catalog')
        sample_brains = pc(portal_type="Sample")
        print('===brains========')

        for brain in sample_brains:
            sample = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = sample.Title()
            dict['Description'] = sample.Description()
            project = sample.getField('Project').get(sample)
            try:
                dict['Project'] = project.Title()
            except:
                dict['Project'] = ''
            dict['Volume'] = sample.getField('Volume').get(sample)
            dict['Unit'] = sample.getField('Unit').get(sample)
            dict['AllowSharing'] = sample.getField('AllowSharing').get(sample)
            dict['Kit'] = sample.getField('Kit').get(sample)
            storage = sample.getField('StorageLocation').get(sample)
            try:
                dict['StorageLocation'] = storage.getHierarchy()
            except:
                dict['StorageLocation'] = ''
            dict['SubjectID'] = sample.getField('SubjectID').get(sample)
            dict['Barcode'] = sample.getField('Barcode').get(sample)
            linked_sample = sample.getField('LinkedSample').get(sample)
            try:
                dict['LinkedSample'] = linked_sample.Title()
            except:
                dict['LinkedSample'] = ''
            sample_donor = sample.getField('Donor').get(sample)
            try:
                dict['SampleDonor'] = sample_donor.Title()
            except:
                dict['SampleDonor'] = ''
            disease_ontology = sample.getField('DiseaseOntology').get(sample)
            try:
                dict['DiseaseOntology'] = disease_ontology.Title()
            except:
                dict['DiseaseOntology'] = ''
            dict['AnatomicalSiteTerm'] = sample.getField('AnatomicalSiteTerm').get(sample)
            dict['AnatomicalSiteDescription'] = sample.getField('AnatomicalSiteDescription').get(sample)
            dict['UID'] = sample.UID()
            try:
                dict['Parent_UID'] = sample.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_samples.append(dict)

        return self.get_headings(), list_of_samples

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'Project',
            'Volume',
            'Unit',
            'AllowSharing',
            'Kit',
            'StorageLocation',
            'SubjectID',
            'Barcode',
            'LinkedSample',
            'SampleDonor',
            'DiseaseOntology',
            'AnatomicalSiteTerm',
            'AnatomicalSiteDescription',
            'UID',
            'Parent_UID',
        ]

        return headings

class AnalysisRequestsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_analysis_requests = []

        pc = getToolByName(self.context, 'portal_catalog')
        analysis_request_brains = pc(portal_type="AnalysisRequest")
        print('===brains========')

        for brain in analysis_request_brains:
            analysis_request = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = analysis_request.Title()
            dict['Description'] = analysis_request.Description()
            dict['RequestID'] = analysis_request.getField('RequestID').get(analysis_request)
            project = analysis_request.getField('Project').get(analysis_request)
            try:
                dict['Project'] = project.Title()
            except:
                dict['Project'] = ''

            contact = analysis_request.getField('Contact').get(analysis_request)
            try:
                dict['Contact'] = contact.Title()
            except:
                dict['Contact'] = ''

            cc_contact = analysis_request.getField('CCContact').get(analysis_request)
            try:
                dict['CCContact'] = cc_contact.Title()
            except:
                dict['CCContact'] = ''

            dict['CCEmails'] = analysis_request.getField('CCEmails').get(analysis_request)

            client = analysis_request.getField('Client').get(analysis_request)
            try:
                dict['Client'] = client.Title()
            except:
                dict['Client'] = ''

            sample = analysis_request.getField('Sample').get(analysis_request)
            try:
                dict['Sample'] = sample.Title()
            except:
                dict['Sample'] = ''
            dict['Volume'] = analysis_request.getField('Volume').get(analysis_request)

            specification = analysis_request.getField('Specification').get(analysis_request)
            try:
                dict['Specification'] = specification.Title()
            except:
                dict['Specification'] = ''

            dict['ResultsRange'] = analysis_request.getField('ResultsRange').get(analysis_request)

            publication_specification = analysis_request.getField('PublicationSpecification').get(analysis_request)
            try:
                dict['PublicationSpecification'] = publication_specification.Title()
            except:
                dict['PublicationSpecification'] = ''

            dict['ClientOrderNumber'] = analysis_request.getField('ClientOrderNumber').get(analysis_request)
            dict['ReportDryMatter'] = analysis_request.getField('ReportDryMatter').get(analysis_request)
            dict['InvoiceExclude'] = analysis_request.getField('InvoiceExclude').get(analysis_request)
            dict['DateReceived'] = analysis_request.getField('DateReceived').get(analysis_request)
            dict['DatePublished'] = analysis_request.getField('DatePublished').get(analysis_request)
            dict['Remarks'] = analysis_request.getField('Remarks').get(analysis_request)
            # dict[''] = analysis_request.getField('').get(analysis_request)

            dict['UID'] = sample.UID()
            try:
                dict['Parent_UID'] = sample.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_analysis_requests.append(dict)

        return self.get_headings(), list_of_analysis_requests

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'RequestID',
            'Contact',
            'CCContact',
            'CCEmails',
            'Client',
            'Sample',
            'Volume',
            'Specification',
            'ResultRange',
            'PublicationSpecification',
            'ClientOrderNumber',
            'ReportDryMatter',
            'InvoiceExclude',
            'DateReceived',
            'DatePublished',
            'Remarks',
            'UID',
            'Parent_UID',
        ]

        return headings