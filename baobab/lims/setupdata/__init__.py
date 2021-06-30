from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFPlone.utils import _createObjectByType
from plone.app.search.browser import quote_chars
from zope.interface import implements
from zope.interface import alsoProvides
from zope.event import notify

from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.exportimport.setupdata import WorksheetImporter
from bika.lims.interfaces import ISetupDataSetList
from baobab.lims.idserver import renameAfterCreation
from baobab.lims.interfaces import ISampleStorageLocation, IStockItemStorage
from baobab.lims.browser.project import *
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime

def get_project_multi_items(context, string_elements, portal_type, portal_catalog):

    if not string_elements:
        return []

    pc = getToolByName(context, portal_catalog)

    items = []
    file_items = [x.strip() for x in string_elements.split(';')]

    for file_item in file_items:
        item_list = pc(portal_type=portal_type, Title=file_item)
        if item_list:
            items.append(item_list[0].getObject().UID())

    return items


class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname="baobab.lims")


class Products(WorksheetImporter):
    """ Import test products
    """
    def Import(self):
        folder = self.context.bika_setup.bika_products
        rows = self.get_rows(3)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        suppliers = [o.getObject() for o in bsc(portal_type="Supplier")]
        for row in rows:
            title = row.get('Title')
            description = row.get('description', '')
            obj = _createObjectByType('Product', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                Hazardous=self.to_bool(row.get('Hazardous', '')),
                Quantity=self.to_int(row.get('Quantity', 0)),
                Unit=row.get('Unit', ''),
                Price=str(row.get('Price', '0.00'))
            )

            for supplier in suppliers:
                if supplier.Title() == row.get('Suppliers', ''):
                    obj.setSupplier(supplier)
                    break

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Kit_Components(WorksheetImporter):
    """ This class is called from Kit_Templates and not from LoadSetupData class
    """
    def __init__(self, lsd, workbook, dataset_project, dataset_name, template_name, catalog):
        self.lsd = lsd
        self.workbook = workbook
        self.dataset_project = dataset_project
        self.dataset_name = dataset_name
        self.template_name = template_name
        self.catalog = catalog
        self.product_list = []

        WorksheetImporter.__call__(self, self.lsd, self.workbook, self.dataset_project, self.dataset_name)

    def Import(self):
        rows = self.get_rows(3)
        product_obj = None
        for row in rows:
            if self.template_name == row.get('templateName'):
                product_name = row.get('componentName')

                brains = self.catalog.searchResults({'portal_type': 'Product', 'title': product_name})
                if brains and len(brains) == 1:
                    product_obj = brains[0].getObject()
                    self.product_list.append({
                        'product': product_name,
                        'product_uid': product_obj.UID(),
                        'value': '',
                        'quantity': row.get('quantity')
                    })

    def get_product_list(self):
        """ This method is called after Import to get computed product_list
        """
        return self.product_list


class Kit_Templates(WorksheetImporter):
    """ Kit_Templates worksheet contains only Kit Template without components. Components are listed in another
        worksheet (see Kit_Components class).
    """
    def Import(self):
        folder = self.context.bika_setup.bika_kittemplates
        rows = self.get_rows(3)
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        for row in rows:
            template_name = row.get('templateName')
            kit_component = Kit_Components(self, self.workbook, self.dataset_project, self.dataset_name, template_name, catalog)
            product_list = kit_component.get_product_list()
            obj = _createObjectByType('KitTemplate', folder, tmpID())
            obj.edit(
                title=template_name,
                ProductList=product_list
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Kits(WorksheetImporter):
    """ Import projects
    """
    def Import(self):

        pc = getToolByName(self.context, 'portal_catalog')

        rows = self.get_rows(3)
        for row in rows:
            # get the project
            project_list = pc(portal_type="Project", Title=row.get('Project'))
            if project_list:
                project = project_list[0].getObject()
            else:
                continue

            # get the kit template if it exists
            bsc = getToolByName(self.context, 'bika_setup_catalog')
            kit_template_list = bsc(portal_type="KitTemplate", title=row.get('KitTemplate'))
            kit_template = kit_template_list and kit_template_list[0].getObject() or None

            stock_items = []
            try:
                if kit_template:
                    stock_items = self.assign_stock_items(kit_template, row, bsc, pc)
            except ValueError as e:
                continue

            obj = _createObjectByType('Kit', project, tmpID())
            obj.edit(
                title=row.get('title'),
                description=row.get('description'),
                Project=project,
                KitTemplate=kit_template,
                FormsThere=row.get('FormsThere'),
                DateCreated=row.get('DateCreated', ''),
            )

            if kit_template:
                obj.setStockItems(stock_items)
                update_quantity_products(obj, bsc)

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def assign_stock_items(self, template, row, bsc, pc):

        si_storages = row.get('StockItemsStorage').split(',')

        if si_storages:
            si_storage_uids = []
            for storage in si_storages:
                storage_brains = pc(portal_type='UnmanagedStorage', Title=storage)
                storage_obj = storage_brains and storage_brains[0].getObject() or None
                if storage_obj:
                    si_storage_uids.append(storage_obj.UID())

        portal_workflow = getToolByName(self.context, 'portal_workflow')

        stock_items = template_stock_items(template, bsc, pc, portal_workflow, si_storage_uids)
        return stock_items


class Storage_Types(WorksheetImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.bika_setup.bika_storagetypes
        rows = self.get_rows(3)
        for row in rows:
            title = row.get('title')
            description = row.get('description', '')
            Temperature = row.get('Temperature')
            obj = _createObjectByType('StorageType', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                Temperature=Temperature    
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class DiseaseOntology(WorksheetImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.disease_ontologies
        rows = self.get_rows(3)
        for row in rows:
            title = row.get('title')
            description = row.get('description', '')
            version = row.get('Version')
            code = row.get('Code')
            free_text = row.get('FreeText')
            obj = _createObjectByType('DiseaseOntology', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                Version=version,
                Code=code,
                FreeText=free_text
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Donor(WorksheetImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.donors
        rows = self.get_rows(3)

        pc = getToolByName(self.context, 'portal_catalog')

        for row in rows:
            sample_donor_id = row.get('SampleDonorID')
            selected_project = row.get('SelectedProject', '')
            info_link = row.get('InfoLink')
            sex = row.get('Sex')
            age = row.get('Age')
            age_unit = row.get('AgeUnit')
            obj = _createObjectByType('SampleDonor', folder, tmpID())

            # get the project
            project_list = pc(portal_type="Project", Title=selected_project)
            project = project_list and project_list[0].getObject() or None

            obj.edit(
                SampleDonorID=sample_donor_id,
                SelectedProject=project,
                InfoLink=info_link,
                Age=age,
                AgeUnit=age_unit
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Projects(WorksheetImporter):
    """ Import projects
    """
    def Import(self):

        pc = getToolByName(self.context, 'portal_catalog')
        audit_logger = AuditLogger(self.context)
        count = 0

        rows = self.get_rows(3)
        for row in rows:
            # get the client object
            client_list = pc(portal_type="Client", Title=row.get('Client'))

            folder = client_list and client_list[0].getObject() or None
            if not folder: continue

            s_types = row.get('SampleTypes')
            a_services = row.get('AnalysisServices')
            st_objects = get_project_multi_items(self.context, s_types, 'SampleType', 'bika_setup_catalog')
            as_objects = get_project_multi_items(self.context, a_services, 'AnalysisService', 'bika_setup_catalog')

            obj = _createObjectByType('Project', folder, tmpID())
            obj.edit(
                title=row.get('title'),
                description=row.get('description'),
                StudyType=row.get('StudyType', ''),
                AgeHigh=self.to_int(row.get('AgeHigh', 0)),
                AgeLow=self.to_int(row.get('AgeLow', 0)),
                NumParticipants=self.to_int(row.get('NumParticipants', 0)),
                SampleType=st_objects,
                Service=as_objects,
                DateCreated=row.get('DateCreated', ''),
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            count += 1
        audit_logger.perform_simple_audit(None, '%s %s' % ('Project', str(count)))

class Biospecimens(WorksheetImporter):
    """ Import biospecimens
    """

    def Import(self):

        rows = self.get_rows(3)
        for row in rows:
            try:
                self.create_biospecimen(row)
            except:
                continue

    def create_biospecimen(self, row):
        pc = getToolByName(self.context, 'portal_catalog')
        bc = getToolByName(self.context, 'bika_catalog')

        # get the project
        project_list = pc(portal_type="Project", Title=row.get('Project'))
        project = project_list and project_list[0].getObject() or None
        if not project: raise

        sampletype_list = pc(portal_type="SampleType", Title=row.get('SampleType'))
        sample_type = sampletype_list and sampletype_list[0].getObject() or None
        if not sample_type: raise

        linked_sample_list = pc(portal_type="Sample", Title=row.get('LinkedSample', ''))
        linked_sample = linked_sample_list and linked_sample_list[0].getObject() or None

        sample_donor_list = bc(portal_type="SampleDonor", SampleDonorID=row.get('SampleDonor', ''))
        sample_donor = sample_donor_list and sample_donor_list[0].getObject() or None

        disease_ontology_list = bc(portal_type="DiseaseOntology", Title=row.get('DiseaseOntology', ''))
        disease_ontology = disease_ontology_list and disease_ontology_list[0].getObject() or None

        barcode = row.get('Barcode')
        if not barcode:
            raise

        try:
            volume = str(row.get('Volume'))
            float_volume = float(volume)
            if not float_volume:
                raise
        except:
            raise

        obj = _createObjectByType('Sample', project, tmpID())

        st_loc_list = pc(portal_type='StoragePosition', Title=row.get('StorageLocation'))
        storage_location = st_loc_list and st_loc_list[0].getObject() or None

        obj.edit(
            title=row.get('title'),
            description=row.get('description'),
            Project=project,
            DiseaseOntology=disease_ontology,
            AllowSharing=row.get('AllowSharing'),
            Donor=sample_donor,
            SampleType=sample_type,
            StorageLocation=storage_location,
            SubjectID=row.get('SubjectID'),
            Barcode=barcode,
            Volume=volume,
            Unit=row.get('Unit'),
            LinkedSample=linked_sample,
            DateCreated=row.get('DateCreated'),
            AnatomicalSiteTerm=row.get('AnatomicalSiteTerm'),
            AnatomicalSiteDescription=row.get('AnatomicalSiteDescription'),

        )

        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

        from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
        ObjectInitializedEventHandler(obj, None)


class Storage(WorksheetImporter):
    """
    Import storage
    """
    def Import(self):

        rows = self.get_rows(3)
        for row in rows:

            # get the type of storage
            storage_type = row.get('type')
            if storage_type not in ['StorageUnit', 'ManagedStorage', 'UnmanagedStorage']:
                continue

            title = row.get('title')
            # get the parent
            hierarchy = row.get('hierarchy')
            parent = self.get_parent_storage(hierarchy)
            if not parent:
                print "parent not found for %s" % hierarchy
                continue

            storage_obj = _createObjectByType(storage_type, parent, row.get('id'))
            storage_obj.edit(
                title=title,
                )
            
            if storage_type == 'StorageUnit':
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                facilities = bsc(portal_type="Department", title=row.get('Department'))
                facility = facilities and facilities[0].getObject() or None
                storage_types = bsc(portal_type="StorageType", title=row.get('StorageTypes'))
                storage_type = storage_types and storage_types[0].getObject() or None

                temperature = None
                if storage_type:
                    temperature = storage_type.getField('Temperature').get(storage_type)


                storage_obj.edit(
                    Department=facility,
                    UnitType=storage_type,
                    Temperature=temperature,
                )


            if storage_type == 'UnmanagedStorage':
                alsoProvides(storage_obj, IStockItemStorage)
                storage_obj.edit(
                    title=hierarchy,
                )

            if storage_type == 'ManagedStorage':
                storage_obj.edit(
                    XAxis=row.get('Rows'),
                    YAxis=row.get('Columns'),
                )
                alsoProvides(storage_obj, ISampleStorageLocation)

                nr_positions = row.get('NumberOfPoints')
                for p in range(1, nr_positions+1):
                    title = hierarchy + ".{id}".format(id=str(p).zfill(len(str(nr_positions))))
                    position = _createObjectByType('StoragePosition', storage_obj, str(p))
                    position.edit(
                        # title=hierarchy + ".{id}".format(id=p)
                        title=title
                    )
                    alsoProvides(position, ISampleStorageLocation)
                    position.reindexObject()

            storage_obj.unmarkCreationFlag()
            storage_obj.reindexObject()

    def get_parent_storage(self, hierarchy):

        pc = getToolByName(self.context, 'portal_catalog')
        hierarchy_pieces = hierarchy.split('.')

        if len(hierarchy_pieces) <= 1:
            return self.context.storage

        parent_id = hierarchy_pieces[len(hierarchy_pieces) - 2]
        parent_hierarchy = '.'.join(hierarchy_pieces[:-1])
        parent_list = pc(portal_type="StorageUnit", id=parent_id)

        if parent_list:
            for parent_item in parent_list:
                parent_object = parent_item.getObject()
                if parent_object.getHierarchy() == parent_hierarchy:
                    return parent_object


class StockItems(WorksheetImporter):
    """ Import stock items
    """
    def Import(self):
        folder = self.context.bika_setup.bika_stockitems
        rows = self.get_rows(3)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in rows:
            products = bsc(portal_type="Product", title=row.get('Product'))
            product = products and products[0].getObject() or None
            description = row.get('description', '')

            st_loc_list = pc(portal_type='UnmanagedStorage', Title=row.get('StorageLocation'))
            storage_location = st_loc_list and st_loc_list[0].getObject() or None
            
            obj = _createObjectByType('StockItem', folder, tmpID())
            obj.edit(
                Product=product,
                StorageLocation=storage_location,
                description=description,
                Quantity=self.to_int(row.get('Quantity', 0)),
                orderId=row.get('InvoiceNzr', ''),
                batchId=row.get('BatchNr', ''),
                receivedBy=row.get('ReceivedBy'),
                dateReceived=row.get('DateReceived', ''),
            )

            new_quantity = int(product.getQuantity()) + int(row.get('Quantity'))
            product.setQuantity(new_quantity)
            product.reindexObject()

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class SetupImporter(WorksheetImporter):
    def isExistingTitle(self, obj_type, obj_title):

        if self.isNotInTitle(obj_title):
            return self.isExistingNotTitle(obj_type, obj_title)

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type=obj_type, Title=obj_title)

        if len(brains) > 0:
            return True
        return False

    def isNotInTitle(self, string):
        tokens = string.split()
        if 'Not' in tokens:
            return True

        return False

    def isExistingNotTitle(self, obj_type, obj_title):

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type=obj_type, inactive_state='active')

        for brain in brains:
            obj = brain.getObject()
            if obj.Title() == obj_title:
                return True

        return False

class AnatomicalMaterial(SetupImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.anatomical_materials
        rows = self.get_rows(3)
        for row in rows:
            if self.isExistingTitle('AnatomicalMaterial', row.get('title')):
                continue

            title = row.get('title')
            description = row.get('description', '')
            obj = _createObjectByType('AnatomicalMaterial', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class CollectionDevice(SetupImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.collection_devices
        rows = self.get_rows(3)
        for row in rows:
            if self.isExistingTitle('CollectionDevice', row.get('title')):
                continue

            title = row.get('title')
            description = row.get('description', '')
            obj = _createObjectByType('CollectionDevice', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class Host(SetupImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.hosts
        rows = self.get_rows(3)
        for row in rows:
            if self.isExistingTitle('Host', row.get('title')):
                continue

            title = row.get('title')
            description = row.get('description', '')
            obj = _createObjectByType('Host', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class HostDisease(SetupImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.host_diseases
        rows = self.get_rows(3)
        for row in rows:
            if self.isExistingTitle('HostDisease', row.get('title')):
                continue

            title = row.get('title')
            description = row.get('description', '')
            obj = _createObjectByType('HostDisease', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class LabHost(SetupImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.lab_hosts
        rows = self.get_rows(3)
        for row in rows:
            if self.isExistingTitle('LabHost', row.get('title')):
                continue

            title = row.get('title')
            description = row.get('description', '')
            obj = _createObjectByType('LabHost', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class Organism(SetupImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.organisms
        rows = self.get_rows(3)
        for row in rows:
            if self.isExistingTitle('Organism', row.get('title')):
                continue

            title = row.get('title')
            genus = row.get('genus', '')
            species = row.get('species', '')
            obj = _createObjectByType('Organism', folder, tmpID())
            obj.edit(
                title=title,
                Genus=genus,
                Species=species,
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class VirusSample(SetupImporter):
    """ Import biospecimens
    """

    def Import(self):
        self._existing_virus_samples = self.getExistingBarcodes('VirusSample')

        rows = self.get_rows(3)
        for row in rows:

            try:
                if row.get('Barcode') in self._existing_virus_samples:
                    continue

                self.create_virus_sample(row)
            except Exception as e:
                continue

    def create_virus_sample(self, row):

        folder = self.context.virus_samples

        project = self.getObject('Project', row.get('Project'))
        sample_type = self.getObject('SampleType', row.get('SampleType'))
        storage_location = self.getObject('StoragePosition', row.get('StorageLocation'))
        anatomical_material = self.getObject('AnatomicalMaterial', row.get('AnatomicalMaterial'))
        organism = self.getObject('Organism', row.get('Organism'))
        collection_device = self.getObject('CollectionDevice', row.get('CollectionDevice'))
        host = self.getObject('Host', row.get('Host'))
        host_disease = self.getObject('HostDisease', row.get('HostDisease'))
        lab_host = self.getObject('LabHost', row.get('LabHost'))
        instrument_type = self.getObject('InstrumentType', row.get('InstrumentType'))
        instrument = self.getObject('Instrument', row.get('Instrument'))
        host_age = row.get('HostAge', '')

        try:
            volume = str(row.get('Volume'))
            float_volume = str(float(volume))

            if not float_volume:
                raise Exception('Volume %s not found' % row.get('Volume'))
        except Exception as e:
            print('-----Exception in %s' % str(e))

        obj = _createObjectByType('VirusSample', folder, tmpID())

        # st_loc_list = pc(portal_type='StoragePosition', Title=row.get('StorageLocation'))
        # storage_location = st_loc_list and st_loc_list[0].getObject() or None

        obj.edit(
            # title=row.get('title'),
            Project=project,
            SampleType=sample_type,
            StorageLocation=storage_location,
            AllowSharing=row.get('AllowSharing'),
            WillReturnFromShipment=row.get('WillReturnFromShipment'),
            Barcode=row.get('Barcode'),
            Volume=float_volume,
            Unit=row.get('Unit'),
            AnatomicalSiteTerm=row.get('AnatomicalSiteTerm'),
            AnatomicalSiteDescription=row.get('AnatomicalSiteDescription'),
            # Repository Accession Numbers
            BioSampleAccession=row.get('BioSampleAccession'),
            # Sample Collector and Processing
            SpecimenCollectorSampleID=row.get('SpecimenCollectorSampleID'),
            SampleCollectedBy=row.get('SampleCollectedBy'),
            SampleCollectionDate=row.get('SampleCollectionDate'),
            SampleReceivedDate=row.get('SampleReceivedDate'),
            GeoLocDate=row.get('GeoLocDate'),
            GeoLocState=row.get('GeoLocState'),
            Organism=organism,
            Isolate=row.get('Isolate'),
            PurposeOfSampling=row.get('PurposeOfSampling'),
            CollectionDevice=collection_device,
            # hhh
            CollectionProtocol=row.get('CollectionProtocol'),
            SpecimenProcessing=row.get('SpecimenProcessing'),
            LabHost=lab_host,
            PassageNumber=row.get('PassageNumber'),
            PassageMethod=row.get('PassageMethod'),
            AnatomicalMaterial=anatomical_material,
            # Host Information
            HostSubjectID=row.get('HostSubjectID'),
            Host=host,
            HostDisease=host_disease,
            HostGender=row.get('HostGender'),
            HostAge=str(host_age),
            HostAgeUnit=row.get('HostAgeUnit'),
            # Host Exposure Information
            ExposureCountry=row.get('ExposureCountry'),
            ExposureEvent=row.get('ExposureEvent'),
            # Sequencing Information
            LibraryID=row.get('LibraryID'),
            InstrumentType=instrument_type,
            Instrument=instrument,
            SequencingProtocolName=row.get('SequencingProtocolName'),
        )

        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

        from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
        ObjectInitializedEventHandler(obj, None)

    def getExistingBarcodes(self, obj_type='VirusSample'):
        existing_virus_samples = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type=obj_type,)

        for brain in brains:
            try:
                virus_sample = brain.getObject()
                barcode = virus_sample.getField('Barcode').get(virus_sample)
                existing_virus_samples.append(barcode)
            except:
                continue

        return existing_virus_samples

    def getObject(self, obj_type, obj_title):
        if not obj_title:
            return None

        pc = getToolByName(self.context, 'portal_catalog')

        brains = pc(portal_type=obj_type, Title=obj_title)
        object = brains and brains[0].getObject() or None
        if not object:
            # raise Exception('%s %s not found' % (obj_type, obj_title))
            return None

        return object


class Monitoring_Devices(WorksheetImporter):
    """Add some dummy monitoring devices
    """
    def Import(self):
        folder = self.context.monitoring_devices
        rows = self.get_rows(3)
        for row in rows:
            title = row.get('title', '')
            if not title: continue
            description = row.get('description', '')
            obj = _createObjectByType('MonitoringDevice', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                MACAddress=row.get('MACAddress')
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Freezers(WorksheetImporter):
    """Add some dummy monitoring devices
    """
    def Import(self):
        folder = self.context.freezers
        rows = self.get_rows(3)
        pc = getToolByName(self.context, 'bika_catalog')
        for row in rows:
            title = row.get('title', '')
            if not title: continue
            description = row.get('description', '')
            deviceTitle = row.get('MonitoringDevice', '')
            device = pc(portal_type='MonitoringDevice', title=deviceTitle)
            device_obj = device[0].getObject() if device else None
            obj = _createObjectByType('Freezer', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                MonitoringDevice=device_obj,
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Device_Readings(WorksheetImporter):
    """Add some dummy monitoring devices
    """
    def Import(self):
        pc = getToolByName(self.context, 'bika_catalog')
        folder = self.context.freezers
        rows = self.get_rows(3)
        for row in rows:
            if not row['CurrentReading']:
                continue
            deviceTitle = row.get('MonitoringDevice', None)
            mon_device = pc(portal_type='MonitoringDevice', title=deviceTitle)
            dev_obj = mon_device[0].getObject() if mon_device else None
            if not dev_obj: continue
            # Device reading
            de_reading = _createObjectByType('DeviceReading', dev_obj, tmpID())
            de_reading.setCurrentReading(row['CurrentReading'])
            de_reading.setLabel(row['Label'])
            de_reading.setUnit(row['Unit'])
            de_reading.unmarkCreationFlag()
            renameAfterCreation(de_reading)

            # Freezer reading
            freezer = pc(portal_type="Freezer", Title=row.get('Freezer', None))
            fr_obj = freezer[0].getObject() if freezer else None
            fr_reading = _createObjectByType('DeviceReading', fr_obj, tmpID())
            fr_reading.setCurrentReading(row['CurrentReading'])
            fr_reading.setDatetimeRecorded(row['DatetimeRecorded'])
            fr_reading.setLabel(row['Label'])
            fr_reading.setUnit(row['Unit'])
            fr_reading.unmarkCreationFlag()
            fr_reading.unmarkCreationFlag()
            renameAfterCreation(fr_reading)
