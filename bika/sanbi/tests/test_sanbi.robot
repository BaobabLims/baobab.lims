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
    ${contact_andrew_uid}=  Create object  bika_setup/bika_labcontacts  LabContact  contact-1  Firstname=Andrew  Surname=Dobson  EmailAddress=asdf1@example.com
    ${contact_robert_uid}=  Create object  bika_setup/bika_labcontacts  LabContact  contact-2  Firstname=Robert  Surname=Roy     EmailAddress=asdf2@example.com
    ${dept_micro_uid}=      Create object  bika_setup/bika_departments  Department   department-1  Title=Micro-biology  Manager=${contact_andrew_uid}
    ${dept_metals_uid}=      Create object  bika_setup/bika_departments  Department   department-2  Title=Metals         Manager=${contact_robert_uid}
    ${cat_micro_uid}=      Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  category-1  title=Micro-biology
    ${cat_metals_uid}=     Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  category-2  title=Metals
    ${service_ecoli_uid}=    Create Object   bika_setup/bika_analysisservices  AnalysisService  service-1  title=EColi  Keyword=ecoli  Category=${cat_micro_uid}
    ${service_calcium_uid}=  Create Object   bika_setup/bika_analysisservices  AnalysisService  service-2  title=Calcium  Keyword=calcium  Category=${cat_metals_uid}
    ${client1_uid}=  Create Object   clients  Client  client-1   title=Happy Hills
    ${client1_uid}=  Create Object   clients  Client  client-2   title=Klaymore
    ${client1_contact1_uid}=  Create object    clients/client-1    Contact   contact-1   Firstname=Contact 1  Surname=Client 1  EmailAddress=CL1CO1@example.com
    ${client1_contact2_uid}=  Create object    clients/client-1    Contact   contact-2   Firstname=Contact 2  Surname=Client 1  EmailAddress=CL1CO2@example.com
    ${client2_contact1_uid}=  Create object    clients/client-2    Contact   contact-1   Firstname=Contact 1  Surname=Client 2  EmailAddress=CL2CO1@example.com
    ${client2_contact2_uid}=  Create object    clients/client-2    Contact   contact-2   Firstname=Contact 2  Surname=Client 2  EmailAddress=CL2CO2@example.com

    Configure Storage Levy
    Configure Storage Type Pricing

    Create Storages

    Create Product Categories
    Create Products

    Create pricelists for kit    # levy is added?    remove discount fields from pricelists
    Create pricelists for storage    # levy is added?    remove discount fields from pricelists

    Create Stock Items

    Create Biospecimen Types
    Create Project

*** Keywords ***

Configure Storage Levy
    go to  ${PLONEURL}/bika_setup/edit
    Click link                        css=#fieldsetlegend-accounting
    debug
    wait until page contains          Storage Levy
    Click Button                      Save
    Page should contain               Changes saved.

Create Storage Unit Types
    go to  ${PLONEURL}/bika_setup/edit
    Click link                        css=#fieldsetlegend-accounting
    debug
    wait until page contains          Storage Pricing
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
    Go to  ${PLONEURL}/storage
    input text                        units_titletemplate     Room {id}
    input text                        units_idtemplate        R{id}
    input text                        units_start             1
    input text                        units_nr_items          ${nr}
    input text                        units_temperature       18
    input text                        units_address           Building Address
    click element                     add_units_submitted
    wait until page contains          Storage units created.

Create ${nr} Freezers in ${room}
    Go to  ${PLONEURL}/storage/${room}
    input text                        units_titletemplate     Freezer {id}
    input text                        units_idtemplate        F{id}
    input text                        units_start             1
    input text                        units_nr_items          ${nr}
    input text                        units_temperature       -80
    click element                     add_units_submitted
    wait until page contains          Storage units created.

Create ${nr} Shelves in ${loc}
    Go to  ${PLONEURL}/storage/${loc}
    input text                        units_titletemplate     Shelf {id}
    input text                        units_idtemplate        S{id}
    input text                        units_start             1
    input text                        units_nr_items          ${nr}
    click element                     add_units_submitted
    wait until page contains          Storage units created.

Create ${nr} Boxes in ${loc} with type ${type}
    Go to  ${PLONEURL}/storage/${loc}
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
    Go to  ${PLONEURL}/storage/${room}
    run keyword and ignore error      Click element        css=.collapsedOnLoad
    Click element                     css=#fieldsetlegend-unmanaged
    input text                        unmanaged_titletemplate     Stock Cabinet {id}
    input text                        unmanaged_idtemplate        SC{id}
    input text                        unmanaged_start             1
    input text                        unmanaged_nr_items          1
    select from list                  unmanaged_storage_types     ${type}
    click element                     addstorage_unmanaged_submitted
    wait until page contains          Unmanaged storages created

Create Biospecimen Types
    Go to  ${PLONEURL}/bika_setup/bika_biospectypes
    Click link                        Add
    Wait Until Page Contains Element  Add Biospecimen Type
    Input Text                        title              BST Blood
    Input Text                        description        Metals and some microbiology
    debug
    Click Button                      Save
    Page should contain               Changes saved.

Create Project
    Go to  ${PLONEURL}/projects
    debug

Create Product Categories
    Go to  ${PLONEURL}/bika_setup/bika_productcategories
    debug

Create Products
    Go to  ${PLONEURL}/bika_setup/bika_productcategories
    debug

Create Stock Items
    Go to  ${PLONEURL}/bika_setup/bika_productcategories
    debug

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}

