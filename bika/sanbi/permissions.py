"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplate = 'SANBI: Add kit template'
AddKit = 'SANBI: Add Kit'
AddStorageManagement = 'SANBI: Add Storage Management'

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'KitTemplate': AddKitTemplate,
    'Kit': AddKit,
    'StorageManagement': AddStorageManagement,
}

ManageStoragePositions = "SANBI: Manage Storage Positions"
ManageKits = "SANBI: Manage Kits"
ManageKitTemplates = "SANBI: Manage KitTemplates"
