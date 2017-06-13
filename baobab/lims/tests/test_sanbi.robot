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
    ${dept_micro_uid}=    Create object  bika_setup/bika_departments  Department   department-1  title=Micro-biology  Manager=${contact_andrew_uid}
    ${dept_metals_uid}=   Create object  bika_setup/bika_departments  Department   department-2  title=Metals         Manager=${contact_andrew_uid}
    ${dept_storage_uid}=  Create object  bika_setup/bika_departments  Department   department-3  title=Storage        Manager=${contact_robert_uid}
    ${dept_invent_uid}=   Create object  bika_setup/bika_departments  Department   department-4  title=inventory      Manager=${contact_robert_uid}
    ${cat_micro_uid}=   Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  category-1  title=Micro-biology
    ${cat_metals_uid}=  Create Object  bika_setup/bika_analysiscategories  AnalysisCategory  category-2  title=Metals
    ${ecoli_uid}=    Create Object   bika_setup/bika_analysisservices  AnalysisService  service-1  title=Ecoli    Keyword=ecoli    Category=${cat_micro_uid}
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
    wait until page contains          Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_manufacturers

    # Create suppliers
    ${supplier1}=  Create object      bika_setup/bika_suppliers    Supplier   supplier-1   title=ACME Lab Supplies (supplier)
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    wait until page contains element  css=#deactivate_transition
    Click link                        Add
    wait until page contains element  css=#Name
    Input Text                        css=#Name  ACME Reference Samples (supplier)
    Click Button                      Save
    wait until page contains          Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_suppliers

    # Create Product Categories
    ${productcategory1}=  Create object    bika_setup/bika_productcategories    ProductCategory   productcategory-1   title=Glass containers    Prefix=GLS
    ${productcategory2}=  Create object    bika_setup/bika_productcategories    ProductCategory   productcategory-2   title=Reference samples   Prefix=REF
    Go to  ${PLONEURL}/bika_setup/bika_productcategories
    wait until page contains element       css=#deactivate_transition
    Click link                             Add
    wait until page contains element       css=#title
    Input Text                             title  Sampling kits
    Input Text                             description   Completed sampling kits
    Input Text                             Prefix   KIT
    Click Button                           Save
    wait until page contains               Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_productcategories

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
    wait until page contains       Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_products

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
    wait until page contains          Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_storagetypes

    # Configure Storage Levy
    go to  ${PLONEURL}/bika_setup/edit
    Click link                        css=#fieldsetlegend-accounting
    wait until page contains          Levy Amount
    Input text                        LevyAmount       10
    Click Button                      Save
    wait until page contains          Changes saved.

    # Configure Storage Type Prices
    go to  ${PLONEURL}/bika_setup/edit
    Click link                       css=#fieldsetlegend-storage
    wait until page contains         Storage Pricing
    select from dropdown             css=#StoragePricing-storage_type-0    freezer
    Input Text                       css=#StoragePricing-price-0           5.50
    click element                    css=#StoragePricing_more
    select from dropdown             css=#StoragePricing-storage_type-1    fridge
    input text                       css=#StoragePricing-price-1           10.10
    click element                    css=#StoragePricing_more
    select from dropdown             css=#StoragePricing-storage_type-2    Room temperature
    input text                       css=#StoragePricing-price-2           1.10
    click element                    css=#StoragePricing_more
    select from dropdown             css=#StoragePricing-storage_type-3    tank
    input text                       css=#StoragePricing-price-3           30.50
    click element                    css=#StoragePricing_more
    Click Button                     Save
    wait until page contains         Changes saved.
    go to  ${PLONEURL}/bika_setup/edit
    Click link                        css=#fieldsetlegend-storage
    Textfield value should be         css=#StoragePricing-price-0        1.10
    Textfield value should be         css=#StoragePricing-price-1        10.10
    Textfield value should be         css=#StoragePricing-price-2        30.50
    Textfield value should be         css=#StoragePricing-price-3        5.50

    # Create pricelist for storage types
    go to  ${PLONEURL}/pricelists
    click link                        Add
    wait until page contains element  css=#title
    input text                        title      Storage pricelist
    select from list                  css=#edit_form_effectiveDate_0_year      2016
    select from list                  css=#edit_form_effectiveDate_0_month     September
    select from list                  css=#edit_form_effectiveDate_0_day       1
    select from list                  css=#Type    Sample Storage
    Click Button                      Save
    wait until page contains          Changes saved.
    go to  ${PLONEURL}/pricelists

    # Create Storage units and managed/unmanaged storages
    # R1 Room 1
    #    - F1 Freezer 1
    #        - S1 Shelf 1
    #            - storage box biospecimen (managed)
    #            - storage box aliquot (managed)
    #        - S1 Shelf 2
    #            - storage box biospecimen (managed)
    #            - storage box aliquot (managed)
    Go to  ${PLONEURL}/storage
    run keyword and ignore error      click element    css=.collapsedBlockCollapsible
    wait until page contains element  css=.expandedBlockCollapsible
    wait until element is visible     units_titletemplate
    input text                        units_titletemplate     Room {id}
    input text                        units_idtemplate        room-{id}
    input text                        units_start             1
    input text                        units_nr_items          1
    input text                        units_temperature       18
    input text                        units_address           Building Address
    select from dropdown              units_department        Storage
    click element                     add_units_submitted
    wait until page contains          Storage units created.
    # Create Freezers
    Go to  ${PLONEURL}/storage/room-1
    run keyword and ignore error      click element    css=.collapsedBlockCollapsible
    wait until element is visible     units_titletemplate
    input text                        units_titletemplate     Freezer {id}
    input text                        units_idtemplate        freezer-{id}
    input text                        units_start             1
    input text                        units_nr_items          2
    input text                        units_temperature       -80
    select from dropdown              units_type              freezer
    click element                     add_units_submitted
    wait until page contains          Storage units created.
    # Shelves
    ${shelf11}=  Create object    storage/room-1/freezer-1    StorageUnit   shelf-1   title=Shelf 1
    Go to  ${PLONEURL}/storage/room-1/freezer-2
    run keyword and ignore error      click element    css=.collapsedBlockCollapsible
    wait until element is visible     units_titletemplate
    input text                        units_titletemplate     Shelf {id}
    input text                        units_idtemplate        shelf-{id}
    input text                        units_start             1
    input text                        units_nr_items          2
    click element                     add_units_submitted
    wait until page contains          Storage units created.
    # Boxes (managed storages)
    Go to  ${PLONEURL}/storage/room-1/freezer-1/shelf-1
    wait until page contains          Create new storages
    run keyword and ignore error      Click element        css=.collapsedBlockCollapsible
    Click element                     css=#fieldsetlegend-managed
    wait until element is visible     managed_titletemplate
    input text                        managed_titletemplate     BioSpecimen Box bb{id}
    input text                        managed_idtemplate        bb{id}
    input text                        managed_start             a
    input text                        managed_nr_items          2
    input text                        managed_positions         4
    select from list                  managed_storage_types     Bio Specimen
    input text                        managed_x                 2
    input text                        managed_y                 2
    click element                     addstorage_managed_submitted
    wait until page contains          Managed storages created
    Go to  ${PLONEURL}/storage/room-1/freezer-1/shelf-1
    wait until page contains          Create new storages
    run keyword and ignore error      Click element        css=.collapsedBlockCollapsible
    Click element                     css=#fieldsetlegend-managed
    wait until element is visible     managed_titletemplate
    input text                        managed_titletemplate     Aliquot Box aa{id}
    input text                        managed_idtemplate        aa{id}
    input text                        managed_start             a
    input text                        managed_nr_items          2
    input text                        managed_positions         4
    select from list                  managed_storage_types     Aliquot
    input text                        managed_x                 2
    input text                        managed_y                 2
    click element                     addstorage_managed_submitted
    wait until page contains          Managed storages created
    # Unmanaged storage for inventory
    Go to  ${PLONEURL}/storage/room-1
    wait until page contains          Create new storages
    run keyword and ignore error      click element    css=.collapsedBlockCollapsible
    Click element                     css=#fieldsetlegend-unmanaged
    wait until page contains element  unmanaged_titletemplate
    input text                        unmanaged_titletemplate     Stock Cabinet {id}
    input text                        unmanaged_idtemplate        stock-cabinet-{id}
    input text                        unmanaged_start             1
    input text                        unmanaged_nr_items          1
    select from list                  unmanaged_storage_types     Stock Item
    click element                     addstorage_unmanaged_submitted
    wait until page contains          Unmanaged storages created
    Go to  ${PLONEURL}/storage/room-1
    wait until page contains          Create new storages
    run keyword and ignore error      click element    css=.collapsedBlockCollapsible
    Click element                     css=#fieldsetlegend-unmanaged
    wait until page contains element  unmanaged_titletemplate
    input text                        unmanaged_titletemplate     Kit Cabinet {id}
    input text                        unmanaged_idtemplate        kit-cabinet-{id}
    input text                        unmanaged_start             1
    input text                        unmanaged_nr_items          1
    select from list                  unmanaged_storage_types     Kit
    click element                     addstorage_unmanaged_submitted
    wait until page contains          Unmanaged storages created

    # Create Kit Templates
    ${kittemplate1}=  Create object    bika_setup/bika_kittemplates   KitTemplate    kittemplate-1   title=Some bottles   description=A 10ml glass bottle and a 50ml glass bottle
    ...     ProductList=[{'product':'10ml glass bottle', 'quantity':1, 'product_uid':'${product1}'},{'product':'50ml glass bottle', 'quantity':1, 'product_uid':'${product2}'}]
    ...     Cost=10    DeliveryFee=20
    go to  ${PLONEURL}/bika_setup/bika_kittemplates
    wait until page contains element  css=#deactivate_transition
    Click link                        Add
    Wait Until Page Contains          Add Kit Template
    Input text                        title  Three bottles
    Input Text                        description   Glass bottles in 10, 50 and 100ml sizes.
    select from dropdown              css=#ProductList-product-0    10ml
    Input text                        css=#ProductList-quantity-0   1
    click element                     css=#ProductList_more
    select from dropdown              css=#ProductList-product-1    50ml
    Input text                        css=#ProductList-quantity-1   1
    click element                     css=#ProductList_more
    select from dropdown              css=#ProductList-product-2    100ml
    Input text                        css=#ProductList-quantity-2   1
    click element                     css=#ProductList_more
    Click Button                      Save
    wait until page contains          Changes saved.
    go to  ${PLONEURL}/bika_setup/bika_kittemplates

    # Create Pricelist for Kit Templates
    go to  ${PLONEURL}/pricelists
    click link                        Add
    wait until page contains element  css=#title
    input text                        title      Prices for kits
    select from list                  css=#edit_form_effectiveDate_0_year      2016
    select from list                  css=#edit_form_effectiveDate_0_month     September
    select from list                  css=#edit_form_effectiveDate_0_day       1
    select from list                  css=#Type     Kits
    Click Button                      Save
    wait until page contains          Changes saved.
    go to  ${PLONEURL}/pricelists

    # Create Biospecimen Types
    Go to  ${PLONEURL}/bika_setup/bika_biospectypes
    run keyword and ignore error      Click element        css=.collapsedBlockCollapsible
    click link                        Add
    wait until page contains element  css=#title
    input text                        title      Human blood
    select checkbox                   css=input[item_title="Calcium"]
    select checkbox                   css=input[item_title="Ecoli"]
    Click Button                      Save
    wait until page contains          Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_biospectypes
    run keyword and ignore error      Click element        css=.collapsedBlockCollapsible
    click link                        Add
    wait until page contains element  css=#title
    input text                        title      Human flesh
    select checkbox                   css=input[item_title="Calcium"]
    select checkbox                   css=input[item_title="Ecoli"]
    Click Button                      Save
    wait until page contains          Changes saved.

    # Create Project
    Go to  ${PLONEURL}/projects
    click link                        Add
    wait until page contains element  css=#title
    input text                        title                    Storage project
    select from dropdown              Client                   Happy Hills
    input text                        StudyType                Storage
    input text                        AgeLow                   10
    input text                        AgeHigh                  20
    input text                        NumParticipants          1000
    select from list                  css=#Biospectypes        Human blood      Human flesh
    select checkbox                   css=input[item_title="Calcium"]
    select checkbox                   css=input[item_title="Ecoli"]
    Click Button                      Save
    wait until page contains          Biospecimen Types

    debug

    go to   ${PLONEURL}/kits
    run keyword and ignore error      Click element        css=.collapsedBlockCollapsible
    wait until element is visible     css=.titletemplate
    input text                        titletemplate        TwoBottle-Kit{id}
    input text                        idtemplate           tbk{id}
    input text                        seq_start            1
    input text                        kit_count            10
    select from dropdown              css=#stockItem       Cabinet
    select from dropdown              css=#Project         Storage
    select from dropdown              css=#KitTemplate     Three
    click element                     addstorage_managed_submitted
    wait until page contains          Managed storages created

    Create Biospecimens

    Create Aliquots from BioSpecimens

    Create AnalysisRequests from Aliquots


*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}

