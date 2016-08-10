 *** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
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

BioBank High-level Demo
    Enable autologin as  LabManager

    Create Client
    Create Client Contact

    Create Storages

    Create Project
    Create Product Categories
    Create Products
    Create Stock Items

*** Keywords ***

Create Client
    Go to                             ${PLONEURL}/clients
    Click link                        Add
    Wait Until Page Contains Element  Name
    Input Text                        Name                    First Client
    Input Text                        ClientID                CLIENT1
    Click Button                      Save
    Page should contain               Changes saved.

Create Client Contact
    Go to                             ${PLONEURL}/clients/client-1
    Click link                        Contacts
    Click link                        Add
    Wait Until Page Contains Element  Firstname
    Input Text                        Salutation              Mr
    Input Text                        Firstname               Bob
    Input Text                        Surname                 Dobbs
    Input Text                        JobTitle                Slacker
    Click Button                      Save
    Page should contain               Changes saved.

Create Storages
    Create 2 Rooms
    Create 2 Freezers in R1
    Create 2 Shelves in R1/F1
    Create 2 Shelves in R1/F2
    Create 2 Boxes in R1/F1/S1 with type Bio Specimen
    Create 2 Boxes in R1/F1/S2 with type Bio Specimen
    Create 2 Boxes in R1/F2/S1 with type Aliquot
    Create 2 Boxes in R1/F2/S2 with type Aliquot
    Create Unmanaged Cabinet in R2 with type Stock Item
    Create Unmanaged Cabinet in R2 with type Kit

Create ${nr} Rooms
    Go to                             ${PLONEURL}/storage
    input text                        units_titletemplate     Room {id}
    input text                        units_idtemplate        R{id}
    input text                        units_start             1
    input text                        units_nr_items          ${nr}
    input text                        units_temperature       18
    input text                        units_address           Building Address
    click element                     add_units_submitted
    wait until page contains          Storage units created.

Create ${nr} Freezers in ${room}
    Go to                             ${PLONEURL}/storage/${room}
    input text                        units_titletemplate     Freezer {id}
    input text                        units_idtemplate        F{id}
    input text                        units_start             1
    input text                        units_nr_items          ${nr}
    input text                        units_temperature       -80
    click element                     add_units_submitted
    wait until page contains          Storage units created.

Create ${nr} Shelves in ${loc}
    Go to                             ${PLONEURL}/storage/${loc}
    input text                        units_titletemplate     Shelf {id}
    input text                        units_idtemplate        S{id}
    input text                        units_start             1
    input text                        units_nr_items          ${nr}
    click element                     add_units_submitted
    wait until page contains          Storage units created.

Create ${nr} Boxes in ${loc} with type ${type}
    Go to                             ${PLONEURL}/storage/${loc}
    run keyword and ignore error      Click element        css=.collapsedOnLoad
    Click element                     css=#fieldsetlegend-managed
    input text                        managed_titletemplate     ${type} Box {id}
    input text                        managed_idtemplate        B{id}
    input text                        managed_start             A
    input text                        managed_nr_items          2
    input text                        managed_positions         4
    select from list                  managed_storage_types     ${type}
    select from list                  managed_dimension         Second Dimension
    input text                        managed_x                 2
    input text                        managed_y                 2
    click element                     addstorage_managed_submitted
    wait until page contains          Managed storages created

Create Unmanaged Cabinet in ${room} with type ${type}
    Go to                             ${PLONEURL}/storage/${room}
    run keyword and ignore error      Click element        css=.collapsedOnLoad
    Click element                     css=#fieldsetlegend-unmanaged
    input text                        unmanaged_titletemplate     Stock Cabinet {id}
    input text                        unmanaged_idtemplate        SC{id}
    input text                        unmanaged_start             1
    input text                        unmanaged_nr_items          1
    select from list                  unmanaged_storage_types     ${type}
    click element                     addstorage_unmanaged_submitted
    wait until page contains          Unmanaged storages created

Create Project
    Go to                             ${PLONEURL}/projects
    debug

Create Product Categories
    Go to                             ${PLONEURL}/bika_setup/bika_productcategories
    debug

Create Products
    Go to                             ${PLONEURL}/bika_setup/bika_productcategories
    debug

Create Stock Items
    Go to                             ${PLONEURL}/bika_setup/bika_productcategories
    debug

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}

