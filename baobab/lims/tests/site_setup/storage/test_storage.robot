*** Settings ***
Suite Setup       Start browser
Suite Teardown    Close All Browsers
Library           BuiltIn
Library           Selenium2Library    timeout=5    implicit_wait=0.3
Library           String
Resource          ../../keywords.txt
Resource          ../setup_keywords.txt
Resource          plone/app/robotframework/selenium.robot
Library           Remote    ${PLONEURL}/RobotRemote
Variables         plone/app/testing/interfaces.py
Variables         ../../variables.py
Library           DebugLibrary

*** Variables ***

${USER_ROLE}  LabManager
${USER}  admin
${PASSWORD}    secret    

*** Test Cases ***

STORAGE SETUP
    [Documentation]  BAOBAB LIMS demo setup as specified in https://baobab-lims.readthedocs.io/en/latest/ 
    # Login  Lab  secret
    #Enable autologin as  ${USER_ROLE}
    Login    ${USER}    ${PASSWORD}
    Add Valid Storage Types
    Add Valid Storage
    #Add InValid Storage   
    
*** Keywords ***
Add Valid Storage  
    Add Valid Department
    Go to  ${PLONEURL}/storage
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Room
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Click element  name=units_department
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    #Select From List By Label  id=units_department  My Test Department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.

    Click Link  Room 1
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Freezer
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Input text  units_nr_items  2
    #Click element  id=units_department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.

    Click Link  Freezer 1
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Shelf
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Input text  units_nr_items  6
    #Click element  id=units_department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.
    Click Link  Shelf 1
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Box
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Input text  units_nr_items  2
    #Click element  id=units_department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.
    Add Managed Storage
    Add Unmanaged Storage
   