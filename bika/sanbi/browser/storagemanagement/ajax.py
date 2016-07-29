import json
import string

import plone
from Products.Archetypes import PloneMessageFactory as PMF
from Products.Archetypes import public as atapi
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode

from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import t, tmpID
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.permissions import AddStorageManagement


def ajax_form_error(errors, field=None, message=None):
    if not message:
        message = t(PMF('Input is required but no input given.'))
    if field:
        error_key = '%s' % field
    else:
        error_key = 'Form error'
    errors[error_key] = message


class StorageManageSubmit:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        plone.protect.PostOnly(form)
        try:
            states = json.loads(form['state'])
        except Exception as e:
            message = t(_("Badely formed state: ${errmsg}",
                          mapping={"errmsg": e.message}))
            ajax_form_error(self.errors, message=message)

            return json.dumps({'errors': self.errors})

        values = {}
        for field, value in states.items():
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

    # TODO: CHECK jsonapi/__init__.py LINE 59 TO FIND AN EXAMPLE HOW TO GET
    # VALUES FOR FIELDS OF AN OBJECT
    # TODO: THIS IS VERY IMPORTANT. CHECK THAT THEY IGNORE VALUES IF FIELD
    # TYPE IS FILE
    def context_to_dict(self):
        context_dict = {}
        for field in self.context.Schema().fields():
            name = field.getName()
            if not isinstance(field, atapi.ComputedField):
                value = field.getRaw(self.context)
                context_dict[name] = value

        return context_dict

    @staticmethod
    def update_children_parent_ref(context):
        for child in context.getChildren():
            child.edit(
                description="Child of " + context.Title()
            )
            # This is helpful for referenceField to not lose there value.
            child.reindexObject()

    def rename_children(self, child, values, index):
        title = self.context.getChildrenTitle() and \
                self.context.getChildrenTitle() + ' ' + index or index
        child.edit(
            title=title,
        )
        # TODO: WE CAN USE HERE renameAfterCreation() method.
        if "Dimension" in values:
            self.context.manage_renameObject(child.id, index)
            child.reindexObject()
        self.update_children_parent_ref(child)

    def create_child(self, portal, values, index):
        """
        """
        title = self.context.getChildrenTitle() and \
                self.context.getChildrenTitle() + ' ' + index or index
        child = _createObjectByType(portal, self.context, tmpID())
        child.edit(
            title=title,
            Type="Other",
            description="Child of " + self.context.Title(),
            Shelves=0,
            Dimension="First",
            # TODO: MAY BE IS MORE TRUE TO PUT THE *Axis = 1?
            XAxis=1,
            YAxis=1,
            ZAxis=1
        )
        child.unmarkCreationFlag()
        renameAfterCreation(child)
        child.reindexObject()

    def create_child_as_location(self, portal, values, index):
        """
        """
        title = self.context.getHierarchy('.') + '.' + index
        location = _createObjectByType(portal, self.context, tmpID())
        # TODO: THINKS LATER TO IMPROVE THIS. 5 BECAUSE WE HAVE THIS HIERARCHY:
        # TODO: room > freezer > shelf > box > position
        assert len(location.getChain()) == 5
        position, box, shelf, freezer, room = [o.Title() for o in
                                               location.getChain()]
        if not position:
            position = index
        location.edit(
            title=title,
            Room=room,
            StorageType=freezer,
            Shelf=shelf,
            Box=box,
            Position=position,
            ParentBox=self.context,
        )
        location.unmarkCreationFlag()
        renameAfterCreation(location)
        location.reindexObject()

    def dimension_representation(self, num_children_add, context_b, values,
                                 num_rows=1, num_cols=1,
                                 num_layers=1, create=False):
        """Compute ids and create children objects.
        """
        alphabet = string.uppercase[:26]

        # TODO: THIS IS A REMARK. THE total_positions SHOULD BE EQUAL TO
        # num_childs_add!
        # total_positions = num_rows * num_cols * num_layers
        total_positions = num_children_add + context_b.get('Shelves', 0)
        num_pos_by_row = total_positions / (num_layers * num_rows)
        num_pos_by_col = total_positions / num_pos_by_row
        num_pos_by_layer = total_positions / num_layers
        if self.context.getStorageLocation():
            children = self.context.getPositions()
        else:
            children = self.context.getChildren()

        # TODO: THIS IS A REMARK. THE num_pos_by_row == num_cols AND
        # num_pos_by_col == num_rows!
        for num in range(total_positions):
            x = num / num_pos_by_row % num_pos_by_col
            y = num % num_pos_by_row
            z = num / num_pos_by_layer
            if self.context.getDimension() == "First":
                if children and num < context_b.get("Shelves", 0):
                    continue
                if values.get('LetterID', False) or context_b.get('LetterID',
                                                                  False):
                    index = alphabet[num]
                else:
                    index = str(y + 1)

            elif self.context.getDimension() == "Second":
                if children and x < context_b.get("XAxis",
                                                  0) and y < context_b.get(
                        "YAxis", 0):
                    continue

                index = alphabet[x] + str(y + 1)

            elif self.context.getDimension() == "Third":
                index = alphabet[z] + str(x + 1) + str(y + 1)

            if create:
                if not self.context.getStorageLocation():
                    self.create_child('StorageManagement', values, index)
                else:
                    self.create_child_as_location('StorageLocation', values,
                                                  index)
            else:
                self.rename_children(children[num], values, index)

        return self.context

    def number_children_add_sub(self, values):
        old_num_items = self.context.getShelves() and \
                        self.context.getShelves() or 0
        new_num_items = values.get('Shelves') and int(values['Shelves']) or 0

        if 'Shelves' not in values.keys():
            return 0, 0

        num_children_add = 0
        num_children_sub = 0
        if new_num_items > old_num_items:
            num_children_add = new_num_items - old_num_items
        elif new_num_items < old_num_items:
            num_children_sub = old_num_items - new_num_items

        return num_children_add, num_children_sub

    def create_storage(self, values):
        """
        Create StorageManagement object or update an existed one.
        :param values: form submit values
        :return: the object created/edited and eventually errors if exist
        """
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        obj_exist = self.context.aq_parent.hasObject(self.context.getId())
        num_rows = values.has_key('XAxis') and values.get('XAxis') and int(
            values['XAxis']) or 1
        num_cols = values.has_key('YAxis') and values.get('YAxis') and int(
            values['YAxis']) or 1
        num_layers = values.has_key('ZAxis') and values.get('ZAxis') and int(
            values['ZAxis']) or 1
        context_b = {}
        if not obj_exist:
            num_add, num_sub = self.number_children_add_sub(values)
            parent_unit = self.context.aq_parent
            # brains = uid_catalog(UID=values['StorageUnit'])
            # if len(brains):
            #     parent_unit = brains[0].getObject()

            # Create the current context in ZODB
            self.context = _createObjectByType('StorageManagement', parent_unit,
                                               tmpID())
            self.context.processForm(REQUEST=self.request, values=values)
            self.context.edit(
                Type=values.get('StorageType') and values[
                    'StorageType'] or "Freeze",
                Dimension=values.get('Dimension') and values[
                    'Dimension'] or "First",
                XAxis=values.get('XAxis') and values['XAxis'] or 1,
                YAxis=values.get('YAxis') and values['YAxis'] or 1,
                ZAxis=values.get('ZAxis') and values['ZAxis'] or 1
            )
            renameAfterCreation(self.context)
            # Increase by 1 the number of children of the parent.
            if parent_unit.portal_type == "StorageManagement":
                parent_unit.setShelves(parent_unit.getShelves() + 1)

            if num_add:
                self.dimension_representation(num_add, context_b, values,
                                              num_rows=num_rows,
                                              num_cols=num_cols,
                                              num_layers=num_layers,
                                              create=True)
        else:
            if not values.get('StorageUnit', ''):
                values['StorageUnit'] = self.context.aq_parent.UID()

            # context before processForm
            context_b = self.context_to_dict()
            num_add, num_sub = self.number_children_add_sub(values)
            self.context.processForm(REQUEST=self.request, values=values)
            if context_b['title'] != self.context.Title():
                self.update_children_parent_ref(self.context)

            if not num_add and (
                    context_b['Dimension'] != self.context.getDimension() or
                    context_b[
                        'ChildrenTitle'] != self.context.getChildrenTitle()):
                self.dimension_representation(len(self.context.getChildren()),
                                              context_b, values,
                                              num_rows=num_rows,
                                              num_cols=num_cols,
                                              num_layers=num_layers,
                                              create=False)

            # In the form edit the type is a normal input element and
            # processForm will not update Type field
            # for this reason we use here values instead of self.context.
            type = values.get('StorageType') and values['StorageType'] or ''
            if type and context_b['Type'] != type:
                self.context.edit(
                    Type=type
                )
                renameAfterCreation(self.context)

            # Create children. The case where the number of items to create
            # pass from 0 to value > 0
            if num_add and context_b['Shelves'] != self.context.getShelves():
                self.dimension_representation(num_add, context_b, values,
                                              num_rows=num_rows,
                                              num_cols=num_cols,
                                              num_layers=num_layers,
                                              create=True)

            if num_sub and context_b['Shelves'] != self.context.getShelves():
                self.delete_children(num_sub, context_b, values)

        return self.context, {}

    def delete_children(self, num_sub, context_b, values):
        """Used in case we drop the number of shelves."""
        is_position = self.context.getStorageLocation()
        if is_position:
            children = self.context.getPositions()
        else:
            children = self.context.getChildren()

        free = True
        if is_position:
            nx = values.get("XAxis", 0)
            ny = values.get("YAxis", 0)
            x = context_b.get("XAxis", 0)
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

            workflow = getToolByName(self.context, 'portal_workflow')
            for i, child in enumerate(children):
                state = workflow.getInfoFor(child, 'review_state')
                if state != 'position_free':
                    free = False
                    break
        else:
            children = children[len(children) - num_sub:]
            for child in children:
                if child.getChildren():
                    free = False
                    break

        if free:
            mt = getToolByName(self.context, 'portal_membership')
            has_perm = mt.checkPermission(AddStorageManagement, self.context)

            if has_perm:
                self.context.manage_delObjects([c.getId() for c in children])

        return ''


class PositionsInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        response = {}
        if self.context.getStorageLocation():
            workflow = getToolByName(self.context, 'portal_workflow')
            positions = []
            response = {'x': self.context.getXAxis(),
                        'y': self.context.getYAxis(),
                        'n': self.context.getShelves()}

            children = self.context.getPositions()
            for c in children:
                aid, name, subject, volume, path, pos = '', '', 0, 0, '', ''
                if c.getIsOccupied() or c.getIsReserved():
                    sample = c.getSample()
                    aid = sample.getId()
                    name = sample.Title()
                    if sample.portal_type == "Biospecimen":
                        subject = sample.getSubjectID()
                    volume = sample.getVolume()
                    path = sample.absolute_url_path()
                    pos = c.absolute_url_path()

                positions.append({
                    'occupied': c.getIsOccupied(),
                    'reserved': c.getIsReserved(),
                    'chain': [o.Title() for o in reversed(c.getChain())],
                    'address': c.Title(),
                    'state': workflow.getInfoFor(c, 'review_state'),
                    'aid': aid,
                    'name': name,
                    'subject': subject,
                    'volume': volume,
                    'path': path,
                    'pos': pos
                })
                response['positions'] = positions

        return json.dumps(response)


class SampleInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        id = form['position']
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        brains = catalog.searchResults(portal_type="StorageLocation", id=id)
        sample = brains[0].getObject().getSample()

        ret = {
            'id': sample.getId(),
            'name': sample.Title(),
            'quantity': sample.getQuantity(),
            'volume': sample.getVolume(),
            'path': sample.absolute_url_path()
        }

        return json.dumps(ret)
