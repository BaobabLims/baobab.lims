"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplate = 'BAOBAB: Add KitTemplate'
AddProject = 'BAOBAB: Add Project'
AddKit = 'BAOBAB: Add Kit'
AddShipment = 'BAOBAB: Add Shipment'
AddAliquot = "BAOBAB: Add Aliquot"
AddMultimage = 'BAOBAB: Add Multimage'
EditFieldBarcode = "BAOBAB: Edit Field Barcode"
ViewBarcode = "BAOBAB: View Barcode"
AddStorageType = "BAOBAB: Add Storage Type"
AddStorageUnit = 'BAOBAB: Add Storage Unit'
AddManagedStorage = 'BAOBAB: Add Managed Storage'
AddUnmanagedStorage = 'BAOBAB: Add Unmanaged Storage'
AddStoragePosition = 'BAOBAB: Add Storage Position'


# New or changed permissions
#---------------------------
AddInventoryOrder = 'BAOBAB: Add Inventory Order'
DispatchInventoryOrder = 'BAOBAB: Dispatch Inventory Order'
ReceiveInventoryOrder = 'BAOBAB: Receive Inventory Order'
StoreInventoryOrder = 'BAOBAB: Store Inventory Order'

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'KitTemplate': AddKitTemplate,
    'Kit': AddKit,
    'Project': AddProject,
    'Shipment': AddShipment,
    'Multimage': AddMultimage,
    'Aliquot': AddAliquot,
    'StorageType': AddStorageType,
    'InventoryOrder': AddInventoryOrder,
    'StorageUnit': AddStorageUnit,
    'ManagedStorage': AddManagedStorage,
    'UnmanagedStorage': AddUnmanagedStorage,
    'StoragePosition': AddStoragePosition,
}

ManageStoragePositions = "BAOBAB: Manage Storage Positions"
ManageKits = "BAOBAB: Manage Kits"
ManageKitTemplates = "BAOBAB: Manage KitTemplates"
ManageProjects = 'BAOBAB: Manage Projects'
ManageShipments= "BAOBAB: Manage Shipments"
ManageAliquots = "BAOBAB: Manage Aliquots"

DueSample = 'BAOBAB: Due Sample'
