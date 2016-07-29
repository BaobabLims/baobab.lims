import json
import string

import plone
from Products.Archetypes import PloneMessageFactory as PMF
from Products.Archetypes import public as atapi
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from zope.interface import alsoProvides

from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import t, tmpID
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IInventoryAssignable
from bika.sanbi.permissions import AddStorageInventory


def ajax_form_error(errors, field=None, message=None):
    if not message:
        message = t(PMF('Input is required but no input given.'))
    if field:
        error_key = '%s' % field
    else:
        error_key = 'Form error'
    errors[error_key] = message


class StorageInventorySubmit:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        plone.protect.PostOnly(form)
        try:
            state = json.loads(form['state'])
        except Exception as e:
            message = t(_("Badely formed state: ${errmsg}",
                          mapping={"errmsg": e.message}))
            ajax_form_error(self.errors, message=message)
            return json.dumps({'errors': self.errors})

        values = {}
        for field, value in state.items():
            if field.endswith('_uid') and ',' in value:
                values[field] = value.split(',')
            else:
                values[field] = value

        storage, self.errors = self.create_storage(values)

        # used to redirect to view template (check it in js)
        storage_url = storage.absolute_url_path()
        message = _('Storage ${STO} was successfully created/updated.',
                    mapping={'STO': safe_unicode(storage)})

        return json.dumps({'success': message, 'url': storage_url})

    def create_child(self, portal, values, index):
        """
        """
        title = index
        child = _createObjectByType(portal, self.context, tmpID())
        child.edit(
            title=title,
            description="Child of " + self.context.Title(),
            Type='o',
            NumPositions=0,
            FreezerID=self.context.getFreezerID(),
            ShelfID=self.context.getShelfID(),
            BoxID=self.context.getBoxID(),
            Location=True,
            Dimension='N'
        )
        child.unmarkCreationFlag()
        renameAfterCreation(child)
        child.reindexObject()

        return child

    def number_children_add_sub(self, values):
        old_num_items = self.context.getNumPositions() and \
                        self.context.getNumPositions() or 0
        new_num_items = values.get('NumPositions') and int(
            values['NumPositions']) or 0

        if 'NumPositions' not in values.keys():
            return 0, 0

        num_children_add = 0
        num_children_sub = 0
        if new_num_items > old_num_items:
            num_children_add = new_num_items - old_num_items
        elif new_num_items < old_num_items:
            num_children_sub = old_num_items - new_num_items

        return num_children_add, num_children_sub

    def dimension_representation(self, num_add, context_b, values, rows=0,
                                 cols=0):
        """Compute indices and create children objects
        """
        alphabet = string.uppercase[:26]
        total_positions = num_add + context_b.get('NumPositions', 0)
        num_pos_by_row = total_positions / rows
        num_pos_by_col = total_positions / num_pos_by_row
        last_child = None
        for num in range(total_positions):
            x = num / num_pos_by_row % num_pos_by_col
            y = num % num_pos_by_row
            dimension = self.context.getDimension()
            dimension = dimension and dimension[0] or ''
            if dimension == 'f':
                if num < context_b.get('NumPositions', 0):
                    continue
                index = str(y + 1)
            elif dimension == 's':
                if x < context_b.get('XAxis', 0) and y < context_b.get('YAxis',
                                                                       0):
                    continue
                index = alphabet[x] + str(y + 1)
            else:
                index = ''

            last_child = self.create_child('StorageInventory', values, index)

        if last_child:
            self.context.edit(
                HasChildren=True,
                NumberOfAvailableChildren=total_positions
            )

        return self.context

    def context_to_dict(self):
        context_dict = {}
        for field in self.context.Schema().fields():
            name = field.getName()
            if not isinstance(field, atapi.ComputedField):
                value = field.getRaw(self.context)
                context_dict[name] = value

        return context_dict

    def delete_children(self, num_sub, context_b, values):
        """Used in case we drop the number of positions"""

        free = True
        children = self.context.getChildren()
        dimension = self.context.getDimension()
        dimension = dimension and dimension[0] or ''
        if dimension == 'f':
            children = children[len(children) - num_sub:]
            for child in children:
                if child.getIsOccupied():
                    free = False
                    break
        elif dimension == 's':
            nx = int(values.get('XAxis', 0))
            ny = int(values.get('YAxis', 0))
            x = int(context_b.get("XAxis", 0))
            indices = []

            for i in range(nx):
                for j in range(ny):
                    indices.append(i * x + j)
            positions = []
            for i in range(len(children)):
                if i in indices:
                    continue
                positions.append(children[i])

            children = positions
            for child in children:
                if child.getIsOccupied():
                    free = False
                    break
        if free:
            mt = getToolByName(self.context, 'portal_membership')
            has_perm = mt.checkPermission(AddStorageInventory, self.context)
            if has_perm:
                self.context.manage_delObjects([c.getId() for c in children])

        return self.context

    def create_storage(self, values):
        exist = self.context.aq_parent.hasObject(self.context.getId())
        numr = values.has_key('XAxis') and values.get('XAxis') and int(
            values['XAxis']) or 1
        numc = values.has_key('YAxis') and values.get('YAxis') and int(
            values['YAxis']) or 1
        context_b = {}
        if not exist:
            num_add, num_sub = self.number_children_add_sub(values)

            # Create the current context in ZODB
            self.context = _createObjectByType(
                'StorageInventory', self.context.aq_parent, tmpID())
            self.context.processForm(REQUEST=self.request, values=values)
            self.context.edit(
                XAxis=values.get('XAxis') and values['XAxis'] or 1,
                YAxis=values.get('YAxis') and values['YAxis'] or 1
            )
            renameAfterCreation(self.context)

            self.dimension_representation(num_add, context_b, values, rows=numr,
                                          cols=numc)
            if self.context.getHasChildren():
                alsoProvides(self.context, IInventoryAssignable)
                self.context.reindexObject(idxs=['object_provides'])

        else:

            context_b = self.context_to_dict()
            num_add, num_sub = self.number_children_add_sub(values)
            self.context.processForm(REQUEST=self.request, values=values)

            numr = numr and numr or context_b.get('XAxis', 1)
            numc = numc and numc or context_b.get('YAxis', 1)
            if num_add and context_b[
                'NumPositions'] < self.context.getNumPositions():
                self.dimension_representation(num_add, context_b, values,
                                              rows=numr, cols=numc)

            if num_sub and context_b[
                'NumPositions'] > self.context.getNumPositions():
                self.delete_children(num_sub, context_b, values)

        return self.context, {}


class InventoryPositionsInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        response = {}
        positions = []
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        if self.context.getHasChildren():
            response = {
                'x': self.context.getXAxis(),
                'y': self.context.getYAxis(),
                'n': self.context.getNumPositions()
            }
            children = self.context.getChildren()
            for c in children:
                pos_info = {}
                sid, product, quantity, path = '', '', 0, ''
                if c.getIsOccupied():
                    # get inventory position stock item
                    sid = c.getISID()
                    brains = catalog.searchResults(portal_type="StockItem",
                                                   id=sid)
                    si = brains[0].getObject()
                    product = si.getProductTitle()
                    quantity = si.getProduct().getQuantity()
                    path = si.absolute_url_path()

                positions.append({
                    'id': c.getId(),
                    'occupied': c.getIsOccupied(),
                    'sid': sid,
                    'product': product,
                    'quantity': quantity,
                    'path': path
                })
                response['positions'] = positions

        return json.dumps(response)


class InventoryItemInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        id = form['position']
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        brains = catalog.searchResults(portal_type="StorageInventory", id=id)
        si_id = brains[0].getObject().getStockItemID()
        brains = catalog.searchResults(portal_type="StockItem", id=si_id)
        stockitem = brains[0].getObject()
        return json.dumps({
            'id': stockitem.getId(),
            'product': stockitem.getProductTitle(),
            'quantity': stockitem.getProduct().getQuantity(),
            'path': stockitem.absolute_url_path()
        })
