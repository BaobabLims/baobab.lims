"""All permissions are defined here.
They are also defined in permissions.zcml.
The two files must be kept in sync.

"""
from bika.lims.permissions import ADD_CONTENT_PERMISSION

AddKitTemplates = 'SANBI: Add kit template'

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'KitTemplates': AddKitTemplates,
}

ManageKitTemplates = "SANBI: Manage KitTemplates"