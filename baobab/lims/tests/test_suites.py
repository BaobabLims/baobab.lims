import unittest

import robotsuite
from pkg_resources import resource_listdir
from plone.testing import layered

from baobab.lims.testing import BAOBAB_SITE_SETUP_MAIL_ROBOT_TESTING


robots = [f for f in resource_listdir("baobab.lims.tests.site_setup", "mail")
          if f.endswith(".robot")]

def test_suite():
    suite = unittest.TestSuite()
    for robot in robots:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(robot, package='baobab.lims.tests.site_setup.mail'),
                    layer=BAOBAB_SITE_SETUP_MAIL_ROBOT_TESTING),
        ])   
    
    return suite
