from zope.interface import Interface
from bika.lims.interfaces import IStorageType

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

class IAliquot(Interface):
    """Interface for a aliquot"""

class IAliquots(Interface):
    """Interface for aliquots"""

class IStockItemStorage(IStorageType):
    """A StorageLocation or StorageLevel that can store StockItems must
    provide this interface"""

class IBioSpecimenStorage(IStorageType):
    """A StorageLocation or StorageLevel that can store BioSpecimen objects
     must provide this interface"""

class IAliquotStorage(IStorageType):
    """A StorageLocation or StorageLevel that can store Aliquots must
    provide this interface"""

class IKitStorage(IStorageType):
    """A StorageLocation or StorageLevel that can store Kits must
    provide this interface"""
