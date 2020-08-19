*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.3
Library         String
Resource        keywords.txt
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***
    

*** Test Cases ***

Baobab LIMS Setup Manual
    [Documentation]  BAOBAB LIMS demo setup as specified in https://baobab-lims.readthedocs.io/en/latest/ 
    # Login  Lab  secret
    Enable autologin as  LabManager
    Add Supplier
    Add Products
    Add Instrument Types
    Add Department
    Add Instruments
    Add Storage Types
    Add Storage
    Set up your stock items for unmanaged storage
    
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
    Select From List By Label  name=InstrumentType  Automated cell counter
    Select From List By Label  name=Supplier  ACME Reference Samples (supplier)
    Click Button  Save
    wait until page contains  Changes saved.
    # Calibration
    # Instrument Interface

Add Department
    Go to  ${PLONEURL}/bika_setup/bika_departments
    Wait Until Page Contains  Add
    Click link  Add
    Wait Until Page Contains  Add Department
    Input Text   title  Biobank
    Click Button  Save
    wait until page contains  Changes saved.
Add Products
    Go to  ${PLONEURL}/bika_setup/bika_products
    Click link  Add
    wait until page contains element  css=#title
    Input Text  title  Distilled water
    Input Text  Quantity  10
    Select checkbox  xpath=//td[1]/input
    Click element  css=#fieldsetlegend-price > span
    Input Text  Price  22
    Input Text  VAT  15
    Click element  id=product-base-edit
    Click Button  Save
    wait until page contains  Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_products

Add Supplier
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    Wait Until Page Contains  Add
    Click link  Add
    Wait Until Page Contains  Add Supplier
    Input Text  Name  ACME Reference Samples (supplier)
    Click Button  Save
    wait until page contains  Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_suppliers

Add Storage Types
    Go to  ${PLONEURL}/bika_setup/bika_storagetypes
    Wait Until Page Contains  Add
    Click link                        Add
    Wait Until Page Contains  Add Storage Type
    Input Text  title  LN tank storage
    Input Text  description   Stored in liquid nitrogen freezer
    Click Button  Save
    wait until page contains          Changes saved.

Add Storage  
    Go to  ${PLONEURL}/storage
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Room
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Click element  id=units_department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.

    Click Link  Room 1
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Freezer
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Input text  units_nr_items  2
    Click element  id=units_department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.

    Click Link  Freezer 1
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Shelf
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Input text  units_nr_items  6
    Click element  id=units_department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.
    Click Link  Shelf 1
    Wait until page contains element  css=.expandedBlockCollapsible
    Input text  units-prefix-text  Box
    Click element  name=units_type
    Click element  css=#ui-active-menuitem .cg-DivItem:nth-child(1)
    Input text  units_nr_items  2
    Click element  id=units_department
    Click element  add_units_submitted
    Wait until page contains  Storage units created.
    Add Managed Storage
    Add Unmanaged Storage

    
Add Managed Storage
    # Replace with go
    #Go to  ${PLONEURL}/Room-1/Freezer-1/Shelf-1/Box-1
    Click Link  Box 1
    Wait until page contains  Managed storage
    Click element  css=#fieldsetlegend-managed > span
    # Create Storage units and managed/unmanaged storages
    Input text  managed-prefix-text  Box
    Input text  managed-nr-items  1
    Input text  managed-positions  10
    Input text  managed-y  2
    Input text  managed-x  5
    Click element  addstorage_managed_submitted
    Wait until page contains  Box 1
    # Shelves
    Click Link  Box 1
    Table cell should contain  xpath=//div[@id='stats']/table  1  1  Total Positions
    Table cell should contain  xpath=//div[@id='stats']/table  1  2  10
    Table cell should contain  xpath=//div[@id='stats']/table  3  1  Available
    Table cell should contain  xpath=//div[@id='stats']/table  3  2  10
    Table cell should contain  xpath=//div[@id='stats']/table  5  1  Reserved
    Table cell should contain  xpath=//div[@id='stats']/table  5  2  0
    Table cell should contain  xpath=//div[@id='stats']/table  6  1  Occupied
    Table cell should contain  xpath=//div[@id='stats']/table  6  2  0

    Select checkbox  xpath=//td[1]/input
    Click element  id=reserve_transition
    Wait until page contains  Changes saved.
    Table cell should contain  xpath=//div[@id='stats']/table  3  1  Available
    Table cell should contain  xpath=//div[@id='stats']/table  3  2  9
    Table cell should contain  xpath=//div[@id='stats']/table  5  1  Reserved
    Table cell should contain  xpath=//div[@id='stats']/table  5  2  1
    Select checkbox  xpath=//td[1]/input
    Click element  id=liberate_transition
    Table cell should contain  xpath=//div[@id='stats']/table  1  1  Total Positions
    Table cell should contain  xpath=//div[@id='stats']/table  1  2  10
    Table cell should contain  xpath=//div[@id='stats']/table  3  1  Available
    Table cell should contain  xpath=//div[@id='stats']/table  3  2  10
    Table cell should contain  xpath=//div[@id='stats']/table  5  1  Reserved
    Table cell should contain  xpath=//div[@id='stats']/table  5  2  0
    # TODO: department/facility

Add Unmanaged Storage
    Click Link  Room 1
    Click element  css=.collapsibleHeader > span
    Wait until page contains  Unmanaged storage
    Click element  css=#fieldsetlegend-unmanaged > span
    input text  unmanaged-prefix-text  Shelf
    input text  unmanaged-nr-items  3
    click element  addstorage_unmanaged_submitted
    Wait until page contains  Shelf-3

Set up your stock items for unmanaged storage
    Go to  ${PLONEURL}/bika_setup/bika_suppliers/supplier-1/base_edit
    Wait Until Page Contains  Orders
    Click link  Orders
    Click link  Add
    Input text  //*[@id="order_edit"]/table[2]/tbody/tr[1]/td[6]/input  10
    Click Button  Save
    Element should contain  css=#content-core > form > table > tbody > tr:nth-child(4) > td.currency > span.total  253.00
    # Click element  //*[@id="workflow-transition-advanced"]
    
    

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}