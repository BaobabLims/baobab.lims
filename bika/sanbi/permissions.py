"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplate = 'SANBI: Add KitTemplate'
AddProject = 'SANBI: Add Project'
AddKit = 'SANBI: Add Kit'
AddShipment = 'SANBI: Add Shipment'
AddAliquot = "SANBI: Add Aliquot"
AddMultimage = 'SANBI: Add Multimage'
EditFieldBarcode = "SANBI: Edit Field Barcode"
ViewBarcode = "SANBI: View Barcode"
AddStorageType = "SANBI: Add Storage Type"
AddStorageUnit = 'SANBI: Add Storage Unit'
AddManagedStorage = 'SANBI: Add Managed Storage'
AddUnmanagedStorage = 'SANBI: Add Unmanaged Storage'
AddStoragePosition = 'SANBI: Add Storage Position'


# New or changed permissions
#---------------------------
AddInventoryOrder = 'SANBI: Add Inventory Order'
DispatchInventoryOrder = 'SANBI: Dispatch Inventory Order'
ReceiveInventoryOrder = 'SANBI: Receive Inventory Order'
StoreInventoryOrder = 'SANBI: Store Inventory Order'

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

ManageStoragePositions = "SANBI: Manage Storage Positions"
ManageKits = "SANBI: Manage Kits"
ManageKitTemplates = "SANBI: Manage KitTemplates"
ManageProjects = 'SANBI: Manage Projects'
ManageShipments= "SANBI: Manage Shipments"
ManageAliquots = "SANBI: Manage Aliquots"

DueSample = 'SANBI: Due Sample'
