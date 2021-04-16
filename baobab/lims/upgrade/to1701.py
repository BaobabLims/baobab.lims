# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import api
from bika.lims import logger


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Delete unsed folder links
    delete_unsed_link_folders(portal)

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-baobab.lims:default',
                                   'propertiestool')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'typeinfo')

    return True


def delete_unsed_link_folders(portal):
    """Delete folders VirusSamples, VirusAliquots, and ExtractGenomicMaterials
    """
    virus_samples_folder = api.search(
            {"portal_type": "VirusSamples"})
    if virus_samples_folder:
        v_obj = virus_samples_folder[0].getObject()
        api.get_parent(v_obj).manage_delObjects([v_obj.getId()])
        logger.info("Deleted VirusSamples folder")
    aliquots = api.search(
            {"portal_type": "VirusAliquots"})
    if aliquots:
        a_obj = aliquots[0].getObject()
        api.get_parent(a_obj).manage_delObjects([a_obj.getId()])
        logger.info("Deleted VirusAliquots folder")
    extracts = api.search(
            {"portal_type": "ExtractGenomicMaterials"})
    if extracts:
        e_obj = extracts[0].getObject()
        api.get_parent(e_obj).manage_delObjects([e_obj.getId()])
        logger.info("Deleted ExtractGenomicMaterials folder")
