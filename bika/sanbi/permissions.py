"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplate = 'SANBI: Add kit template'
AddKit = 'SANBI: Add Kit'
AddStorageManagement = 'SANBI: Add Storage Management'
AddProject = 'SANBI: Add Project'
AddShipment = 'SANBI: Add Shipment'
AddMultimage = 'BIKA: Add Multimage'
AddAliquot = "BIKA: Add Aliquot"
AddStorageInventory = "BIKA: Add Storage Inventory"
EditFieldBarcode = "BIKA: Edit Field Barcode"
ViewBarcode = "BIKA: View Barcode"

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'KitTemplate': AddKitTemplate,
    'Kit': AddKit,
    'StorageManagement': AddStorageManagement,
    'Project': AddProject,
    'Shipment': AddShipment,
    'Multimage': AddMultimage,
    'Sample': AddAliquot,
    'StorageInventory': AddStorageInventory,
}

ManageStoragePositions = "SANBI: Manage Storage Positions"
ManageKits = "SANBI: Manage Kits"
ManageKitTemplates = "SANBI: Manage KitTemplates"
ManageProjects = 'SANBI: Manage Projects'
ManageShipments= "SANBI: Manage Shipments"
ManageAliquots = "SANBI: Manage Aliquots"
