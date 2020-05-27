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

${USER_ROLE}  LabManager
${USER}  admin
${PASSWORD}    secret

*** Test Cases ***
SUPPLIER SETTINGS SETUP    
    Login    ${USER}    ${PASSWORD}
    Supplier Settings Links
    Adding Valid Supplier Settings
    Adding InValid Supplier Settings
    Adding Valid Product
    Adding InValid Product
    
*** Keywords ***
Supplier Settings Links
    Go to    ${PLONEURL}/@@overview-controlpanel
    wait until page contains   Configuration area for Plone and add-on Products.
    Go to    ${PLONEURL}/bika_setup/bika_suppliers   
    wait until page contains   Suppliers
    
Default Supplier Form Parameters   
    Input Text    TaxNumber    123456777
    Input Text    Phone    0214454441
    Input Text    Fax    0214454442
    Input Text    Website    http://www.testsupplier.com
    
Adding Valid Supplier Settings  
    Supplier Settings Links
    Click link    Add
    wait until page contains   Add Supplier
    Input Text    Name    Baobab Test Supplier
    Default Supplier Form Parameters
    Click Button    Save
    wait until page contains    Changes saved.
    Go to    ${PLONEURL}/bika_setup/bika_suppliers
    wait until page contains   Baobab Test Supplier
    
    #Todo:
    #Add Address Details
    #Add Bank Details Details
    
Adding InValid Supplier Settings  
    Supplier Settings Links
    Click link    Add
    wait until page contains   Add Supplier
    Input Text    Name    ${EMPTY}
    Default Supplier Form Parameters
    Click Button    Save
    wait until page contains    Please correct the indicated errors.
    #Todo:
    #Add Address Details
    #Add Bank Details Details    

Product Form
    Input Text    description    The Walking Dead
    select checkbox    css=input[id="Hazardous"]
    Input Text    Quantity    2
    Input Text    Unit    ml
    Select checkbox    css=input[item_title="Baobab Test Supplier"] 
 
Adding Valid Product
    Go to    ${PLONEURL}/bika_setup/bika_products
    wait until page contains    Products
    Click link    Add
    wait until page contains   Add Product
    Input Text    title    Test Product
    Product Form
    Click Button    Save
    wait until page contains    Changes saved.
    Go to    ${PLONEURL}/bika_setup/bika_products
    wait until page contains    Test Product

Adding InValid Product
    Go to    ${PLONEURL}/bika_setup/bika_products
    wait until page contains    Products
    Click link    Add
    wait until page contains   Add Product
    Input Text    title    ${EMPTY}
    Product Form
    Click Button    Save
    wait until page contains    Please correct the indicated errors.

Start browser
    Open browser    ${PLONEURL}    chrome
    Set selenium speed    ${SELENIUM_SPEED}
