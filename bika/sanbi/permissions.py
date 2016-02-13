"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplate = 'SANBI: Add kit template'
AddSupplyEx = 'SANBI: Add SupplyEx'

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'KitTemplate': AddKitTemplate,
    'SupplyEx': AddSupplyEx,
}

ManagePackages = "SANBI: Manage Packages"
ManageKitTemplates = "SANBI: Manage KitTemplates"