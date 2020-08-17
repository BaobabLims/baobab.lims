# import this to create messages in the bika domain.
from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('baobab.lims')

from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore.utils import ContentInit, ToolInit, getToolByName

from baobab.lims.config import *
from baobab.lims.permissions import ADD_CONTENT_PERMISSION, ADD_CONTENT_PERMISSIONS
import logging
logger = logging.getLogger('BAOBAB')
import pkg_resources

__version__ = pkg_resources.get_distribution("baobab.lims").version


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from content.shipment import Shipment
    from content.shipments import Shipments

    from content.kittemplate import KitTemplate
    from content.biospectype import BiospecType
    from content.biospecimen import Biospecimen
    from content.multimage import Multimage
    from content.storagetype import StorageType
    from content.kit import Kit
    from content.kits import Kits
    from content.project import Project
    from content.projects import Projects
    from content.biospecimens import Biospecimens
    from content.inventoryorder import InventoryOrder
    from content.inventoryorderfolder import InventoryOrderFolder
    from content.product import Product
    from content.stockitem import StockItem
    from content.storageunit import StorageUnit
    from content.storageunits import StorageUnits
    from content.managedstorage import ManagedStorage
    from content.unmanagedstorage import UnmanagedStorage
    from content.storageposition import StoragePosition
    from content.donor import SampleDonor
    from content.donors import SampleDonors
    from content.disease_ontology import DiseaseOntology
    from content.disease_ontologies import DiseaseOntologies

    from content.sampleshipment import SampleShipment
    from content.sampleshipments import SampleShipments

    from content.samplebatch import SampleBatch
    from content.samplebatches import SampleBatches

    from controlpanel.bika_kittemplates import KitTemplates
    from controlpanel.bika_biospectypes import BiospecTypes
    from controlpanel.bika_storagetypes import StorageTypes
    from controlpanel.bika_products import Products
    from controlpanel.bika_stockitems import StockItems
    from content.auditlog import AuditLog
    from content.auditlogs import AuditLogs
    from content.sample_pooling import SamplePooling
    from content.sample_poolings import SamplePoolings
    from content.inputsample import InputSample
    from content.inputsamples import InputSamples
    from content.resultsample import ResultSample
    from content.resultsamples import ResultSamples
    from content.centrifugation import Centrifugation
    from content.centrifugations import Centrifugations
    from content.sample_kingdom import SampleKingdom
    from content.sample_kingdoms import SampleKingdoms
    from content.conformity import Conformity
    from content.conformities import Conformities
    from content.collection_request import CollectionRequest
    from content.collection_requests import CollectionRequests
    from content.strain import Strain
    from content.strains import Strains
    from content.human_sample_request import HumanSampleRequest
    from content.human_sample_requests import HumanSampleRequests
    from content.microbe_sample_request import MicrobeSampleRequest
    from content.microbe_sample_requests import MicrobeSampleRequests
    from content.sample_package import SamplePackage
    from content.sample_packages import SamplePackages
    from content.culture_medium import CultureMedium
    from content.culture_mediums import CultureMediums
    from content.transport import Transport
    from content.transports import Transports
    from content.culturing import Culturing
    from content.culturings import Culturings
    from content.reculturing import ReCulturing
    from content.reculturings import ReCulturings

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    # Register each type with it's own Add permission
    # use ADD_CONTENT_PERMISSION as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (PROJECTNAME, atype.portal_type)
        perm = ADD_CONTENT_PERMISSIONS.get(atype.portal_type,
                                           ADD_CONTENT_PERMISSION)
        ContentInit(kind,
                    content_types      = (atype,),
                    permission         = perm,
                    extra_constructors = (constructor,),
                    fti                = ftis,
                    ).initialize(context)
