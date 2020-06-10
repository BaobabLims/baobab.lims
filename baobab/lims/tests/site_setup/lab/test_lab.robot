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
${PATH}    /usr/bin/chromedriver

*** Test Cases ***
LAB SETTINGS
    Set Window Size    1920    1080
    Login    ${USER}    ${PASSWORD}
    LAB Settings Links
    Adding Valid Lab Default Settings
    Adding Invalid Lab Default Settings
    Adding Valid Lab Contact
    Adding InValid Lab Contact
    #@Todo: Password Activation Process
    Add Valid Department
    Add InValid Department
    
*** Keywords ***
LAB Settings Links
    Go to    ${PLONEURL}/@@overview-controlpanel
    wait until page contains   Configuration area for Plone and add-on Products.
    Go to    ${PLONEURL}/bika_setup/laboratory/base_edit    
    wait until page contains   Laboratory
    
    
Default Lab Form Parameters   
    Input Text    TaxNumber    123456777
    Input Text    Phone    0214454441
    Input Text    Fax    0214454442
    #select from dropdown    css=#LaboratorySupervisor    »Lab » Manager
    #Input Text    LaboratoryLicenseID    ID456724RDEE

Adding Valid Lab Default Settings  
    LAB Settings Links
    Input Text    Name    Test Laboratory
    Default Lab Form Parameters
    Click Button    Save
    wait until page contains    Changes saved.
    Go to    ${PLONEURL}/bika_setup/laboratory/base_edit
    
Default Lab Contact Form Parameters
    Input Text    Salutation    Dr
    Input Text    Middleinitial    DD
    Input Text    Middlename    Elizabeth
    Input Text    Surname    Johnson
    Input Text    JobTitle    Technician
    
Adding Valid Lab Contact
    Go to    ${PLONEURL}/bika_setup/bika_labcontacts    
    wait until page contains   Lab Contacts
    Click link    Add
    wait until page contains   Add Lab Contact
    Input Text    Firstname    Dominique    
    Default Lab Contact Form Parameters
    Click Button    Save
    wait until page contains    Changes saved.
    Adding Valid Login Details
    Adding InValid Login Details

Adding InValid Lab Contact
    Go to    ${PLONEURL}/bika_setup/bika_labcontacts    
    wait until page contains   Lab Contacts
    Click link    Add
    wait until page contains   Add Lab Contact
    Input Text    Firstname    ${EMPTY}    
    Default Lab Contact Form Parameters
    Click Button    Save
    wait until page contains    Please correct the indicated errors.

Adding Invalid Lab Default Settings  
    LAB Settings Links
    Input Text    Name    ${EMPTY}
    Default Lab Form Parameters
    Click Button    Save
    wait until page contains    Please correct the indicated errors.
    Go to    ${PLONEURL}/bika_setup/laboratory/base_edit

Login Form Details
    Input Password    password    secretuser
    Input Password    confirm    secretuser
    Input Text    email    dominiqueuser@test.co.za
    Select From List     name=groups    LabManagers

Adding Valid Login Details
    click element    //a[text()='Login details']
    wait until page contains    Login details
    Input Text    username    dominique_user
    Login Form Details
    Click Button    Save
    wait until page contains    SMTP server disconnected.
 
Adding InValid Login Details
    click element    //a[text()='Login details']
    wait until page contains    Login details
    Input Text    username    ${EMPTY}
    Login Form Details
    Click Button    Save
    wait until page contains    username: Input is required but not given.
         
Start browser
    Open browser    ${PLONEURL}    chrome
    Set selenium speed    ${SELENIUM_SPEED}
