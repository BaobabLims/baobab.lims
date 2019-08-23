from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from baobab.lims.utils.audit_logger import AuditLogger


def ObjectInitializedEventHandler(instance, event):
	"""called an object is created
	"""
	if instance.portal_type == 'Project':
		audit_logger = AuditLogger(instance, 'Project')
		audit_logger.perform_simple_audit(instance, 'New')