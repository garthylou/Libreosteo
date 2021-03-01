# -*- coding: robot -*-
*** Settings ***
Resource   resources.txt


*** Test Cases ***
Valid Login
  [Documentation]   Valid login a user
  Open Browser To Login Page
  Title Should Be   Identifiez-vous sur LibreOsteo 
  Login With      test  test
  Title Should Be   LibreOsteo
  [TearDown]  Close Browser


Invalid Login
  [Documentation]   Invalid login a user
  Open Browser To Login Page 
  Title Should Be     Identifiez-vous sur LibreOsteo
  Login with      demo   demo
  Title Should Be     Identifiez-vous sur LibreOsteo
  Element Should Be Visible     class:alert-danger
  [TearDown]    Close Browser


*** Keywords ***
Login With
  [Arguments]   ${login}  ${password}
  Input Text    username  ${login}
  Input Text    password    ${password}
  Click Button  login

Logout
  Go To   ${LOGIN_URL}/logout
  Title Should Be     Identifiez-vous sur LibreOsteo
