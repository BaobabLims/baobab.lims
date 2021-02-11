*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.3
Library         String
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
    Load Setup Data
    Add Analysis to Project
    Add AnalysisRequest with Human Sample
    # Add Organism
    # Add VirusSample
    # Add AnalysisRequest with VirusSample Sample
    
*** Keywords ***
Load Setup Data
    Go To   ${PLONEURL}/import
    Wait Until Page Contains  Load
    Click element  css=#fieldsetlegend-setupdata > span
    Select From List By Value  name=existing  baobab.lims:test
    Click element  name=setupexisting
    Wait until page contains  Changes saved


Add Analysis to Project
    Go To   ${PLONEURL}/projects
    Click Link  Green Goblin Project
    Click Link  Edit
    Click element  css=tr:nth-child(1) > .cat_header
    Sleep  4
    Select checkbox  name=uids:list
    Click Button  Save


Add AnalysisRequest with Human Sample
    Go To  ${PLONEURL}/clients/client-1/project-1/analysisrequests
    Click element  id=analysisrequests
    Click element  css=.context_action_link > span

    # select contact
    Click element  id=Contact-0
    Sleep  1
    Click element  css=.cg-DivItem:nth-child(2)
    Click element  css=tr:nth-child(2) .copybutton

    # select human sample
    Click element  id=Sample-0
    Sleep  1
    Click element  css=.cg-DivItem:nth-child(1)
    Click element  css=tr:nth-child(5) .copybutton

    # select analysis
    Click element  css=tr:nth-child(1) > .cat_header
    Sleep  4
    Select checkbox  name=uids:list
    Wait until element contains  xpath=//*[@id="analysisrequest_edit_form"]/div[1]/table/tfoot/tr[1]/td[2]/span  10.00
    # Click element  css=#analysisrequest_edit_form > div:nth-child(12) > span > div > input
    Click element  css=.context:nth-child(13)
    Sleep  5
    Wait until page contains  created
    

Add Organism
    Go To   ${PLONEURL}/organisms
    Wait Until Page Contains  Add
    Click Link  Add
    Wait Until Page Contains  Add Organism
    Input Text  title  Organism 1
    Click Button  Save
    wait until page contains  Changes saved.


Add VirusSample
    Go To  ${PLONEURL}/biospecimens
    Click Link  Add Virus Sample 
    Click element  id=Project
    Click element  css=.cg-DivItem:nth-child(1)
    Click element  id=SampleType
    Click element  css=.cg-DivItem:nth-child(1)
    Click element  id=SpecimenCollectorSampleID
    Input Text  id=SpecimenCollectorSampleID  John Doe
    Input Text  id=SampleCollectedBy  Clint East Wood
    Input Text  id=SampleReceivedDate  2021-02-10
    Select from list by index  Organism:list  0
    Input Text  id=SampleReceivedDate  2021-02-10
    Input Text  id=Isolate  Isolate
    Click Button  Save
    Click element  css=.state-sample_registered:nth-child(2)
    Sleep  1
    Click element  css=#workflow-transition-sample_due > .subMenuTitle
    Click element  css=.state-sample_due:nth-child(2)
    Sleep  1
    Click element  css=#workflow-transition-receive > .subMenuTitle


Add AnalysisRequest with VirusSample Sample
    Go To  ${PLONEURL}/clients/client-1/project-1/analysisrequests
    Click element  id=analysisrequests
    Click element  css=.context_action_link > span
    Click element  id=Contact-0
    Sleep  1
    Click element  css=.cg-DivItem:nth-child(2)
    Sleep  1
    Click element  css=tr:nth-child(2) .copybutton

    # select virus sample
    Click element  id=Sample-0
    Click element  xpath=//div[6]/div
    Click element  css=tr:nth-child(5) .copybutton

    Sleep  10
    # select analysis
    Click element  css=tr:nth-child(1) > .cat_header
    Sleep  4
    Select checkbox  name=uids:list
    # Click element  css=#analysisrequest_edit_form > div:nth-child(12) > span > div > input
    Click Button  Save
    Sleep  4
    Wait until page contains  R04 were successfully created.
    

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}
