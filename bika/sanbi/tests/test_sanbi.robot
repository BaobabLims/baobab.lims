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

Bio Bank Demo
    Enable autologin as  LabManager
    ${contact_andrew_uid}=  Create object  bika_setup/bika_labcontacts  LabContact  contact-1  Firstname=Andrew  Surname=Dobson  EmailAddress=asdf1@example.com
    ${contact_robert_uid}=  Create object  bika_setup/bika_labcontacts  LabContact  contact-2  Firstname=Robert  Surname=Roy     EmailAddress=asdf2@example.com
    ${dept_micro_uid}=      Create object  bika_setup/bika_departments  Department   department-1  Title=Micro-biology  Manager=${contact_andrew_uid}
    ${dept_metals_uid}=      Create object  bika_setup/bika_departments  Department   department-2  Title=Metals         Manager=${contact_robert_uid}
    ${cat_micro_uid}=      Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  category-1  title=Micro-biology
    ${cat_metals_uid}=     Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  category-2  title=Metals
    ${ecoli_uid}=    Create Object   bika_setup/bika_analysisservices  AnalysisService  service-1  title=EColi  Keyword=ecoli  Category=${cat_micro_uid}
    ${calcium_uid}=  Create Object   bika_setup/bika_analysisservices  AnalysisService  service-2  title=Calcium  Keyword=calcium  Category=${cat_metals_uid}
    ${client1_uid}=  Create Object   clients  Client  client-1   title=Happy Hills
    ${client1_uid}=  Create Object   clients  Client  client-2   title=Klaymore
    ${client1_contact1_uid}=  Create object    clients/client-1    Contact   contact-1   Firstname=Contact 1  Surname=Client 1  EmailAddress=CL1CO1@example.com
    ${client1_contact2_uid}=  Create object    clients/client-1    Contact   contact-2   Firstname=Contact 2  Surname=Client 1  EmailAddress=CL1CO2@example.com
    ${client2_contact1_uid}=  Create object    clients/client-2    Contact   contact-1   Firstname=Contact 1  Surname=Client 2  EmailAddress=CL2CO1@example.com
    ${client2_contact2_uid}=  Create object    clients/client-2    Contact   contact-2   Firstname=Contact 2  Surname=Client 2  EmailAddress=CL2CO2@example.com

    # Create Manufacturers
    ${manufacturer1}=  Create object           bika_setup/bika_manufacturers    Manufacturer   manufacturer-1   title=ACME lab supplies
    Go to  ${PLONEURL}/bika_setup/bika_manufacturers
    wait until page contains element  css=#deactivate_transition
    Click link                        Add
    wait until page contains element  css=#title
    Input Text                        title  ACME reference samples
    Click Button                      Save
    Page should contain               Changes saved.

    # Create suppliers
    ${supplier1}=  Create object           bika_setup/bika_suppliers    Supplier   supplier-1   title=ACME Lab Supplies (supplier)
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    wait until page contains element  css=#deactivate_transition
    Click link                        Add
    wait until page contains element  css=#Name
    Input Text                        css=#Name  ACME Reference Samples (supplier)
    Click Button                      Save
    Page should contain               Changes saved.

    # Create Product Categories
    ${productcategory1}=  Create object    bika_setup/bika_productcategories    ProductCategory   productcategory-1   title=Glass containers   Prefix=GLS
    ${productcategory1}=  Create object    bika_setup/bika_productcategories    ProductCategory   productcategory-1   title=Reference samples   Prefix=REF
    Go to  ${PLONEURL}/bika_setup/bika_productcategories
    wait until page contains element       css=#deactivate_transition
    Click link                             Add
    wait until page contains element       css=#title
    Input Text                             title  Sampling kits
    Input Text                             description   Completed sampling kits
    Input Text                             Prefix   KIT
    Click Button                           Save
    Page should contain                    Changes saved.

    # Create Products
    ${product1}=  Create object    bika_setup/bika_products    Product   product-1   title=10ml glass bottle    Supplier=${supplier1}
    ${product2}=  Create object    bika_setup/bika_products    Product   product-2   title=50ml glass bottle    Supplier=${supplier1}
    ${product3}=  Create object    bika_setup/bika_products    Product   product-3   title=100ml glass bottle   Supplier=${supplier1}
    Go to  ${PLONEURL}/bika_setup/bika_products
    Click link                     Add
    wait until page contains element       css=#title
    Input Text                     title  Distilled water
    Select from list               Category:list               Reference samples
    Select from list               Manufacturer                ACME reference samples
    select checkbox                css=input[selector='bika_suppliers_supplier-2']
    Click Button                   Save
    Page should contain            Changes saved.

    # Create Storage Types
    ${storagetype1}=  Create object    bika_setup/bika_storagetypes    StorageType   storagetype-1   title=Room temperature storage
    ${storagetype2}=  Create object    bika_setup/bika_storagetypes    StorageType   storagetype-2   title=4 deg C refridgerator
    ${storagetype3}=  Create object    bika_setup/bika_storagetypes    StorageType   storagetype-3   title=-80 dec C freezer
    Go to  ${PLONEURL}/bika_setup/bika_storagetypes
    wait until page contains element  css=#deactivate_transition
    Click link                        Add
    wait until page contains element  css=#title
    Input Text                        title          LN tank storage
    Input Text                        description   Stored in liquid nitrogen freezer
    Click Button                      Save
    Page should contain               Changes saved.

    # Configure Storage Levy
    go to  ${PLONEURL}/bika_setup/edit
    Click link                        css=#fieldsetlegend-accounting
    wait until page contains          Levy Amount
    Input text                        LevyAmount       10
    Click Button                      Save
    Page should contain               Changes saved.

    # Configure Storage Type Prices
    go to  ${PLONEURL}/bika_setup/edit
    Click link                        css=#fieldsetlegend-storage
    wait until page contains          Storage Pricing
    click element                     css=#StoragePricing_more
    click element                     css=#StoragePricing_more
    click element                     css=#StoragePricing_more
    click element                     css=#StoragePricing_more
    wait until page contains element  css=#StoragePricing-storage_type-0
    select from dropdown              css=#StoragePricing-storage_type-0    freezer
    select from dropdown              css=#StoragePricing-price-0           5.5
    wait until page contains element  css=#StoragePricing-storage_type-1
    select from dropdown              css=#StoragePricing-storage_type-1    fridge
    select from dropdown              css=#StoragePricing-price-1           10.1
    wait until page contains element  css=#StoragePricing-storage_type-2
    select from dropdown              css=#StoragePricing-storage_type-2    Room temperature
    select from dropdown              css=#StoragePricing-price-2           1.1
    wait until page contains element  css=#StoragePricing-storage_type-3
    select from dropdown              css=#StoragePricing-storage_type-3    tank
    select from dropdown              css=#StoragePricing-price-3           30.5

    # Create pricelist for storage types
    go to  ${PLONEURL}/pricelists
    debug
    wait until page contains          Storage Pricing




    # Create Storages
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

    # Create Kit Templates
    ${kittemplate1}=  Create object    bika_setup/bika_kittemplates   KitTemplate    kittemplate-1   title=Some bottles   description=A 10ml glass bottle and a 50ml glass bottle
    ...     ProductList=[{'product':'10ml glass bottle', 'quantity':1, 'product_uid':'${product1}'},{'product':'50ml glass bottle', 'quantity':1, 'product_uid':'${product2}'}]
    ...     Cost=10    DeliveryFee=20
    go to  ${PLONEURL}/bika_setup/bika_kittemplates
    Click link                        Add
    wait until page contains element  css=#deactivate_transition
    Wait Until Page Contains          Add Kit Template
    Input text                        title  Three bottles
    Input Text                        description   Glass bottles in 10, 50 and 100ml sizes.
    Click Button                      Save
    Page should contain               Changes saved.

    # Create Pricelist for Kit Templates


    # Create stock items to be included in finished kits

    # Create Biospecimen Types
    ${biospectype1}=  Create object    bika_setup/bika_biospectypes   BiospecType    biospectype-1   title=Blood   description=Human blood    Service=${ecoli_uid}
    Go to  ${PLONEURL}/bika_setup/bika_biospectypes
    Click link                        Add
    Wait Until Page Contains Element  Add Biospecimen Type
    Input Text                        title              Flesh
    Input Text                        description        Human flesh
    debug
    Click Button                      Save
    Page should contain               Changes saved.

    # Create Project
    Go to  ${PLONEURL}/projects


    Create Project

    Create Kits

    Create Biospecimens

    Create Aliquots from BioSpecimens

    Create AnalysisRequests from Aliquots


*** Keywords ***



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

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}

