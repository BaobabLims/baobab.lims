"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplate = 'SANBI: Add kit template'
AddKit = 'SANBI: Add Kit'
AddProject = 'SANBI: Add Project'
AddShipment = 'SANBI: Add Shipment'
AddMultimage = 'BIKA: Add Multimage'
AddAliquot = "BIKA: Add Aliquot"
EditFieldBarcode = "BIKA: Edit Field Barcode"
ViewBarcode = "BIKA: View Barcode"
AddStorageType = "BIKA: Add Storage Type"

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'KitTemplate': AddKitTemplate,
    'Kit': AddKit,
    'Project': AddProject,
    'Shipment': AddShipment,
    'Multimage': AddMultimage,
    'Sample': AddAliquot,
    'StorageType': AddStorageType,
}

ManageStoragePositions = "SANBI: Manage Storage Positions"
ManageKits = "SANBI: Manage Kits"
ManageKitTemplates = "SANBI: Manage KitTemplates"
ManageProjects = 'SANBI: Manage Projects'
ManageShipments= "SANBI: Manage Shipments"
ManageAliquots = "SANBI: Manage Aliquots"
