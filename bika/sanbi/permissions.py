"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplate = 'SANBI: Add KitTemplate'
AddProject = 'SANBI: Add Project'
AddKit = 'SANBI: Add Kit'
AddShipment = 'SANBI: Add Shipment'
AddAliquot = "BIKA: Add Aliquot"
AddMultimage = 'BIKA: Add Multimage'
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
    'Aliquot': AddAliquot,
    'StorageType': AddStorageType,
}

ManageStoragePositions = "SANBI: Manage Storage Positions"
ManageKits = "SANBI: Manage Kits"
ManageKitTemplates = "SANBI: Manage KitTemplates"
ManageProjects = 'SANBI: Manage Projects'
ManageShipments= "SANBI: Manage Shipments"
ManageAliquots = "SANBI: Manage Aliquots"
