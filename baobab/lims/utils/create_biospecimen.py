from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation


def create_sample(context, request, values):
    obj = _createObjectByType('Sample', context, tmpID())

    # st_loc_list = pc(portal_type='StoragePosition', Title=values.get('StorageLocation'))
    # storage_location = st_loc_list and st_loc_list[0].getObject() or None

    obj.edit(
        title=values['title'],
        description=values['description'],
        Project=values['Project'],
        AllowSharing=values['AllowSharing'],
        SampleType=values['SampleType'],
        StorageLocation=values['StorageLocation'],
        SubjectID=values['SubjectID'],
        Barcode=values['Barcode'],
        Volume=values['Volume'],
        Unit=values['Unit'],
        LinkedSample=values['LinkedSample'],
        DateCreated=values['DateCreated'],
    )

    obj.unmarkCreationFlag()
    renameAfterCreation(obj)

    if values.has_key('APISource'):
        obj.api_source = values['APISource']

    from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
    ObjectInitializedEventHandler(obj, None)

    return obj


def create_virus_sample(context, values):
    folder = context.virus_samples
    obj = _createObjectByType('VirusSample', folder, tmpID())

    # st_loc_list = pc(portal_type='StoragePosition', Title=values.get('StorageLocation'))
    # storage_location = st_loc_list and st_loc_list[0].getObject() or None

    virus_sample = values['LinkedSample']

    obj.edit(
        title=values['title'],
        description=values['description'],
        Project=values['Project'],
        AllowSharing=values['AllowSharing'],
        SampleType=values['SampleType'],
        StorageLocation=values['StorageLocation'],
        SubjectID=values['SubjectID'],
        Barcode=values['Barcode'],
        Volume=values['Volume'],
        Unit=values['Unit'],
        DateCreated=values['DateCreated'],
        SpecimenCollectorSampleID=virus_sample.getField('SpecimenCollectorSampleID').get(virus_sample),
        SampleCollectedBy=virus_sample.getField('SampleCollectedBy').get(virus_sample),
        SampleCollectionDate=virus_sample.getField('SampleCollectionDate').get(virus_sample),
        SampleReceivedDate=virus_sample.getField('SampleReceivedDate').get(virus_sample),
        Organism=virus_sample.getOrganism(),
        Isolate=virus_sample.getField('Isolate').get(virus_sample),
        InstrumentType=virus_sample.getInstrumentType()
    )

    obj.unmarkCreationFlag()

    return obj