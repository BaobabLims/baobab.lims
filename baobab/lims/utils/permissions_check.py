from plone import api
from Products.CMFCore.utils import getToolByName

def is_administrator(context):
    membership = getToolByName(context, 'portal_membership')
    authenticated_user = membership.getAuthenticatedMember()

    user_roles = api.user.get_roles(user=authenticated_user)
    group_roles = api.group.get_roles(groupname='Administrators')
    # group_roles = api.group.get_roles(groupname='Clients')

    if 'Authenticated' not in user_roles:
        return False

    user_roles.remove('Authenticated')
    for user_role in user_roles:
        if user_role in group_roles:
            return True

    return False

