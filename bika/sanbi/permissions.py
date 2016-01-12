"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplates = 'SANBI: Add kit template'
AddKitAssembly = 'SANBI: Add kit assembly'

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'Package': AddKitAssembly,
    'KitTemplates': AddKitTemplates
}

ManagePackages = "SANBI: Manage Packages"
ManageKitTemplates = "SANBI: Manage KitTemplates"