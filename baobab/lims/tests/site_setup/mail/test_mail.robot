*** Settings ***
Suite Setup       Start browser
Suite Teardown    Close All Browsers
Library           BuiltIn
Library           Selenium2Library    timeout=5    implicit_wait=0.3
Library           String
Resource          ../../keywords.txt
Resource          plone/app/robotframework/selenium.robot
Library           Remote    ${PLONEURL}/RobotRemote
Variables         plone/app/testing/interfaces.py
Variables         ../../variables.py
Library           DebugLibrary

*** Variables ***
${USER_ROLE}  admin
${USER}  admin
${PASSWORD}    secret

*** Test Cases ***
MAIL SETTINGS
    #Enable autologin as     ${USER_ROLE}
    Login    ${USER}    ${PASSWORD}
    Go To Mail Settings
    Valid Email Address
    Invalid Email Address
    
*** Keywords ***
Go To Mail Settings
    Go to    ${PLONEURL}/@@overview-controlpanel
    wait until page contains   Configuration area for Plone and add-on Products.
    Go to    ${PLONEURL}/@@mail-controlpanel 
    wait until page contains    Mail settings


Email Form Parameters   
    Input Text    form.smtp_port    55
    Input Text    form.smtp_userid    test@sanbi.ac.za
    Input Text    form.smtp_pass    123qwesecret
    Input Text    form.email_from_name    Test Postmaster
    Input Text    form.email_from_address    info@testbaoab.org


Valid Email Address  
    Go To Mail Settings
    Input Text    form.smtp_host    smtp.sanbi.ac.za
    Email Form Parameters
    Click Button    Save
    wait until page contains    Changes saved.
    Go to    ${PLONEURL}/@@overview-controlpanel
    

Invalid Email Address
    Go To Mail Settings
    Input Text    form.smtp_host    ${EMPTY}
    Email Form Parameters
    Click Button    Save
    wait until page contains    There were errors
    Go to    ${PLONEURL}/@@overview-controlpanel

Start browser
    Open browser    ${PLONEURL}    chrome
    Set selenium speed    ${SELENIUM_SPEED}

