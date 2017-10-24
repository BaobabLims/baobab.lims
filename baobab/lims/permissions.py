"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddProject = 'BAOBAB: Add Project'
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

ReceiveShipment = 'BAOBAB: Client Receive Shipment'
ShowSharableSamples = 'BAOBAB: Show Sharable Samples'

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'Project': AddProject,
    'InventoryOrder': AddInventoryOrder,
    'StorageUnit': AddStorageUnit,
    'ManagedStorage': AddManagedStorage,
    'UnmanagedStorage': AddUnmanagedStorage,
    'StoragePosition': AddStoragePosition,
}

ManageStoragePositions = 'BAOBAB: Manage Storage Positions'
ManageProjects = 'BAOBAB: Manage Projects'
ManageKits = 'BAOBAB: Manage Kits'
DueSample = 'BAOBAB: Due Sample'
