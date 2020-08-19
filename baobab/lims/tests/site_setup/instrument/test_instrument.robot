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

INSTRUMENT SETUP
    [Documentation]  BAOBAB LIMS demo setup as specified in https://baobab-lims.readthedocs.io/en/latest/ 
    # Login  Lab  secret
    #Enable autologin as  ${USER_ROLE}
    Login    ${USER}    ${PASSWORD}
    Add Valid Supplier
    Add Instrument Types
    Add Instruments    
    
*** Keywords ***
Add Instrument Types
    Go To   ${PLONEURL}/bika_setup/bika_instrumenttypes
    Wait Until Page Contains  Add
    Click Link  Add
    Input Text  title  Automated cell counter
    Click Button  Save
    wait until page contains  Changes saved.

Add Instruments
    Go To   ${PLONEURL}/bika_setup/bika_instruments
    Wait Until Page Contains  Add
    Click Link  Add
    Wait Until Page Contains  Add Instrument
    Input Text  title  Cell Counter
    Select From List By Label  name=InstrumentType    Automated cell counter
    Select From List By Label  name=Supplier    Baobab Test Supplier
    Click Button  Save
    wait until page contains  Changes saved.
    # Calibration
    # Instrument Interface

Start browser
    Open browser    ${PLONEURL}    chrome
    Set selenium speed    ${SELENIUM_SPEED}
