from bika.lims.jsonapi import config

ALLOWED_PORTAL_TYPES_TO_CREATE = {
    'StorageUnit',
    'ManagedStorage',
    'UnmanagedStorage',
    'Project'
}

ALLOWED_PORTAL_TYPES_TO_CREATE.update(config.ALLOWED_PORTAL_TYPES_TO_CREATE)