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

STORAGE TYPE SETUP
    [Documentation]  BAOBAB LIMS demo setup as specified in https://baobab-lims.readthedocs.io/en/latest/ 
    # Login  Lab  secret
    #Enable autologin as  ${USER_ROLE}
    Login    ${USER}    ${PASSWORD}
    Add Valid Storage Types
    Add InValid Storage Types

*** Keywords ***

Add InValid Storage Types
    Go to  ${PLONEURL}/bika_setup/bika_storagetypes
    Wait Until Page Contains  Add
    Click link                        Add
    Wait Until Page Contains  Add Storage Type
    Input Text  title  ${EMPTY}
    Input Text  description   Stored in liquid nitrogen freezer
    Click Button  Save
    wait until page contains    Please correct the indicated errors.
