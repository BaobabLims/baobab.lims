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

${ADMIN_ROLE}  Site Administrator

*** Test Cases ***
valid_email_address
    Enable autologin as     ${ADMIN_ROLE}
    Go to    ${PLONEURL}/@@overview-controlpanel
    wait until page contains   Configuration area for Plone and add-on Products.
    Go to    ${PLONEURL}/@@mail-controlpanel 
    wait until page contains    Mail settings
    Input Text    form.smtp_host    smtp.sanbi.ac.za
    Input Text    form.smtp_port    55
    Input Text    form.smtp_userid    test@sanbi.ac.za
    Input Text    form.smtp_pass    123qwesecret
    Input Text    form.email_from_name    Test Postmaster
    Input Text    form.email_from_address    info@testbaoab.org
    Click Button    Save
    wait until page contains    Changes saved.
    Go to    ${PLONEURL}/@@overview-controlpanel
    
invalid_email_address
    Enable autologin as     ${ADMIN_ROLE}
    Go to    ${PLONEURL}/@@overview-controlpanel
    wait until page contains   Configuration area for Plone and add-on Products.
    Go to    ${PLONEURL}/@@mail-controlpanel 
    wait until page contains    Mail settings
    Input Text    form.smtp_host    ${EMPTY}
    Input Text    form.smtp_port    55
    Input Text    form.smtp_userid    test
    Input Text    form.smtp_pass    123qwesecret
    Input Text    form.email_from_name    Test Postmaster
    Input Text    form.email_from_address    info@testbaoab.org
    Click Button    Save
    wait until page contains    There were errors
    Go to    ${PLONEURL}/@@overview-controlpanel

*** Keywords ***
Start browser
    Open browser    ${PLONEURL}    chrome
    Set selenium speed    ${SELENIUM_SPEED}

