# -*- coding: utf-8 -*-
import pkgutil

from bika.lims import logger

from baobab.lims.jsonapi import routes

__version__ = 2
__date__ = "2018-01-13"


prefix = routes.__name__ + "."
for importer, modname, ispkg in pkgutil.iter_modules(
        routes.__path__, prefix):
    module = __import__(modname, fromlist=["dummy"])
    logger.info("INITIALIZED BAOBAB JSON API ROUTE ---> %s" % module.__name__)

