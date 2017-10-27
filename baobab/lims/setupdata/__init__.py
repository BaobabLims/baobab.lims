from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.exportimport.setupdata import WorksheetImporter
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import tmpID
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from bika.lims.interfaces import ISetupDataSetList
from zope.interface import implements
from bika.lims.idserver import renameAfterCreation

from pkg_resources import *


def get_project_multi_items(context, string_elements, portal_type, portal_catalog):

    if not string_elements:
        return []

    pc = getToolByName(context, portal_catalog)

    items = []
    file_items = [x.strip() for x in string_elements.split(';')]

    for file_item in file_items:
        item_list = pc(portal_type=portal_type, Title=file_item)
        if item_list:
            items.append(item_list[0].getObject().UID())

    return items

class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname="baobab.lims")


class Kit_Components(WorksheetImporter):
    """ This class is called from Kit_Templates and not from LoadSetupData class
    """
    def __init__(self, lsd, workbook, dataset_project, dataset_name, template_name, catalog):
        self.lsd = lsd
        self.workbook = workbook
        self.dataset_project = dataset_project
        self.dataset_name = dataset_name
        self.template_name = template_name
        self.catalog = catalog
        self.product_list = []

        WorksheetImporter.__call__(self, self.lsd, self.workbook, self.dataset_project, self.dataset_name)

    def Import(self):
        rows = self.get_rows(3)
        product_obj = None
        for row in rows:
            if self.template_name == row.get('templateName'):
                product_name = row.get('componentName')

                brains = self.catalog.searchResults({'portal_type': 'Product', 'title': product_name})
                if brains and len(brains) == 1:
                    product_obj = brains[0].getObject()
                    self.product_list.append({
                        'product': product_name,
                        'product_uid': product_obj.UID(),
                        'value': '',
                        'quantity': row.get('quantity')
                    })

    def get_product_list(self):
        """ This method is called after Import to get computed product_list
        """
        return self.product_list


class Kit_Templates(WorksheetImporter):
    """ Kit_Templates worksheet contains only Kit Template without components. Components are listed in another
        worksheet (see Kit_Components class).
    """
    def Import(self):
        folder = self.context.bika_setup.bika_kittemplates
        rows = self.get_rows(3)
        template_name = ''
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        for row in rows:
            template_name = row.get('templateName')
            kit_component = Kit_Components(self, self.workbook, self.dataset_project, self.dataset_name, template_name, catalog)
            product_list = kit_component.get_product_list()
            # category = self.get_object(catalog, 'ProductCategory', title=row.get('category'))
            obj = _createObjectByType('KitTemplate', folder, tmpID())
            obj.edit(
                title=template_name,
                ProductList=product_list,
                Quantity=row.get('quantity')
            )
            # obj.setCategory(category)

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Products(WorksheetImporter):
    """ Import test products
    """
    def Import(self):
        folder = self.context.bika_setup.bika_products
        rows = self.get_rows(3)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        suppliers = [o.getObject() for o in bsc(portal_type="Supplier")]
        for row in rows:
            title = row.get('Title')
            description = row.get('description', '')
            obj = _createObjectByType('Product', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                Hazardous=self.to_bool(row.get('Hazardous', '')),
                Quantity=self.to_int(row.get('Quantity', 0)),
                Unit=row.get('Unit', ''),
                Price=str(row.get('Price', '0.00'))
            )

            for supplier in suppliers:
                if supplier.Title() == row.get('Suppliers', ''):
                    obj.setSupplier(supplier)
                    break

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Storage_Types(WorksheetImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.bika_setup.bika_storagetypes
        rows = self.get_rows(3)
        for row in rows:
            title = row.get('title')
            description = row.get('description', '')
            obj = _createObjectByType('StorageType', folder, tmpID())
            obj.edit(
                title=title,
                description=description
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Projects(WorksheetImporter):
    """ Import projects
    """
    def Import(self):

        pc = getToolByName(self.context, 'portal_catalog')

        rows = self.get_rows(3)
        for row in rows:
            # get the client object
            client_list = pc(portal_type="Client", Title=row.get('Client'))

            folder = client_list and client_list[0].getObject() or None
            if not folder: continue

            s_types = row.get('SampleTypes')
            a_services = row.get('AnalysisServices')
            st_objects = get_project_multi_items(self.context, s_types, 'SampleType', 'bika_setup_catalog')
            as_objects = get_project_multi_items(self.context, a_services, 'AnalysisService', 'bika_setup_catalog')

            obj = _createObjectByType('Project', folder, tmpID())
            obj.edit(
                title=row.get('title'),
                description=row.get('description'),
                StudyType=row.get('StudyType', ''),
                AgeHigh=self.to_int(row.get('AgeHigh', 0)),
                AgeLow=self.to_int(row.get('AgeLow', 0)),
                NumParticipants=self.to_int(row.get('NumParticipants', 0)),
                SampleType=st_objects,
                Service=as_objects,
                DateCreated=row.get('DateCreated', ''),
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
