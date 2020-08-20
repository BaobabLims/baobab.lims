from zope.interface import Interface

class IKitTemplate(Interface):
    """Comment"""

class IKitTemplates(Interface):
    """Comment"""

class IKits(Interface):
    """Package folder"""

class IKit(Interface):
    """Package Supply"""

class IProject(Interface):
    """Interface for Project"""

class IProjects(Interface):
    """Interface for Projects"""

class IBiospecType(Interface):
    """Interface for Project"""

class IBiospecTypes(Interface):
    """Interface for Projects"""

class IShipments(Interface):
    """Interface for shipments"""

class IShipment(Interface):
    """Interface for a shipment"""

class IBiospecimen(Interface):
    """Interface for a biospecimen"""

class IBiospecimens(Interface):
    """Interface for a biospecimens"""

class IMultimage(Interface):
    """Interface for a multimage"""

class IStockItemStorage(Interface):
    """A StorageLocation or StorageLevel that can store StockItems must
    provide this interface"""

class IBiospecimenStorage(Interface):
    """A StorageLocation or StorageLevel that can store BioSpecimen objects
     must provide this interface"""

class IKitStorage(Interface):
    """A StorageLocation or StorageLevel that can store Kits must
    provide this interface"""

class IStorageType(Interface):
    """Marker interface for StorageType"""

class IStorageTypes(Interface):
    """Marker interface for StorageTypes"""

class IProjectBiospecimenView(Interface):
    """Marker interface for StorageTypes"""

#=======================================================#
#     MODIF STARTS FROM HERE                            #
#=======================================================#

class IStorageTypeRegistration(Interface):
    """
    """

class IProductCategory(Interface):
    """Product Category"""


class IProductCategories(Interface):
    """Product Categories"""

class IStockItem(Interface):
    """
    Interface for StockItem class.
    """

class IStockItems(Interface):
    """
    Interface for StockItems class.
    """

class IProduct(Interface):
    """
    Interface for Product.
    """

class IProducts(Interface):
    """
    Interface for Products.
    """

class IManagedStorage(Interface):
    """Base for all storage types.
    """

class IUnmanagedStorage(Interface):
    """Base for all storage types.
    """

class IStoragePosition(Interface):
    """This is the marker interface applied StorageLocation items.  This is
    only a marker for the StorageLocation type itself, it does not signify
    a 'type' of storage.
    """

class IInventoryOrder(Interface):
    """Interface for Orders for Inventory"""

class IInventoryOrderFolder(Interface):
    """Interface for Order Folder for Inventory"""

class ISampleStorageLocation(Interface):
    """Interface for sample storage location"""

class IStorageUnit(Interface):
    """
    """

class IStorageUnits(Interface):
    """
    """

class ISharableSample(Interface):
    """
    """

class IBatch(Interface):
    """
    """

class IBatches(Interface):
    """
    """

class ISampleDonor(Interface):
    """
    """

class ISampleDonors(Interface):
    """
    """

class IDiseaseOntology(Interface):
    """
    """

class IDiseaseOntologies(Interface):
    """
    """

class ISampleShipment(Interface):
    """
    """

class ISampleShipments(Interface):
    """
    """

class IAuditLog(Interface):
    """
    """

class IAuditLogs(Interface):
    """
    """

class ISamplePooling(Interface):
    """
    """

class ISamplePoolings(Interface):
    """
    """

class IInputSample(Interface):
    """
    """

class IInputSamples(Interface):
    """
    """

class IResultSample(Interface):
    """
    """

class IResultSamples(Interface):
    """
    """

class ICentrifugation(Interface):
    """
    """

class ICentrifugations(Interface):
    """
    """

class IConformity(Interface):
    """
    """

class IConformities(Interface):
    """
    """

class ISampleKingdom(Interface):
    """
    """

class ISampleKingdoms(Interface):
    """
    """

class ICollectionRequest(Interface):
    """
    """

class ICollectionRequests(Interface):
    """
    """

class IStrain(Interface):
    """
    """

class IStrains(Interface):
    """
    """

class IHumanSampleRequest(Interface):
    """
    """

class IHumanSampleRequests(Interface):
    """
    """

class IMicrobeSampleRequest(Interface):
    """
    """

class IMicrobeSampleRequests(Interface):
    """
    """

class ISamplePackage(Interface):
    """
    """

class ISamplePackages(Interface):
    """
    """

class ICultureMedium(Interface):
    """
    """

class ICultureMediums(Interface):
    """
    """

class ITransport(Interface):
    """
    """

class ITransports(Interface):
    """
    """

class ICulturing(Interface):
    """
    """

class ICulturings(Interface):
    """
    """

class IReCulturing(Interface):
    """
    """

class IReCulturings(Interface):
    """
    """


class IMaldiTof(Interface):
    """
    """


class IMaldiTofs(Interface):
    """
    """
