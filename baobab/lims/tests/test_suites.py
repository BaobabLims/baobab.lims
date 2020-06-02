import unittest
import robotsuite
import os
from pkg_resources import resource_listdir
from plone.testing import layered

from baobab.lims.testing import SETUP_MAIL_LAYER
from baobab.lims.testing import SETUP_LAB_LAYER
from baobab.lims.testing import SETUP_SUPPLIER_LAYER


layers = {'mail' : SETUP_MAIL_LAYER, 
          'lab'  : SETUP_LAB_LAYER,
          'supplier': SETUP_SUPPLIER_LAYER}
 
def get_robot_tests(cat):
    tests = []
    dir = os.path.dirname(os.path.abspath(__file__))
    path = "{}/{}".format(dir, cat)
    for item in os.listdir(path):
        if os.path.isdir('{}/{}'.format(path, item)):
             tests.extend(f for f in resource_listdir("baobab.lims.tests.{}".format(cat), item)
                if f.endswith(".robot"))            
    return tests

robots = {'site_setup': get_robot_tests('site_setup'), 
          'user_manual': get_robot_tests('user_manual')}

def test_suite():
    suite = unittest.TestSuite()
    for cat in robots:
        for robot in robots[cat]:            
            rb = robot[:-11] #testsuite name
            suite.addTests([
                layered(robotsuite.RobotTestSuite(robot, package='baobab.lims.tests.{}.{}'.format(cat, rb)),
                        layer=layers[rb]),
            ])   
    return suite
