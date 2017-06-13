from bika.lims.utils import to_utf8


def _createdby_data(view):
    """ Returns a dict that represents the user who created the ws
        Keys: username, fullmame, email
    """
    username = view.context.getOwner().getUserName()
    return {'username': username,
            'fullname': to_utf8(view.user_fullname(username)),
            'email': to_utf8(view.user_email(username))}

def _printedby_data(view):
    """ Returns a dict that represents the user who prints the ws
        Keys: username, fullname, email
    """
    data = {}
    member = view.context.portal_membership.getAuthenticatedMember()
    if member:
        username = member.getUserName()
        data['username'] = username
        data['fullname'] = to_utf8(view.user_fullname(username))
        data['email'] = to_utf8(view.user_email(username))

        c = [x for x in view.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                data['signature'] = sf.absolute_url() + "/Signature"

    return data

def _lab_data(view):
    """ Returns a dictionary that represents the lab object
        Keys: obj, title, url, address, confidence, accredited,
              accreditation_body, accreditation_logo, logo
    """
    portal = view.context.portal_url.getPortalObject()
    lab = view.context.bika_setup.laboratory
    lab_address = lab.getPostalAddress() \
                  or lab.getBillingAddress() \
                  or lab.getPhysicalAddress()
    if lab_address:
        _keys = ['address', 'city', 'state', 'zip', 'country']
        _list = ["<div>%s</div>" % lab_address.get(v) for v in _keys
                 if lab_address.get(v)]
        lab_address = "".join(_list)
    else:
        lab_address = ''

    return {'obj': lab,
            'title': to_utf8(lab.Title()),
            'url': to_utf8(lab.getLabURL()),
            'address': to_utf8(lab_address),
            'confidence': lab.getConfidence(),
            'accredited': lab.getLaboratoryAccredited(),
            'accreditation_body': to_utf8(lab.getAccreditationBody()),
            'accreditation_logo': lab.getAccreditationBodyLogo(),
            'logo': "%s/logo_print.png" % portal.absolute_url()}