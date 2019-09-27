*** Settings ***
Library           OperatingSystem
Library           RequestsLibrary
Library           json

*** Variables ***
${Valet_Host}=     http://10.12.6.165
${Endpoint_API}=   /api/valet/alive
${Endpoint_Ping}=   /api/valet/ping
${Endpoint_Health}=  /api/valet/healthcheck
${Valet_Port} =    8080
${Valet_Url}=      /api/valet
${Create_EP}=      /placement/v1/
${Authorization}=    ${BASIC} ${AUTHVALUE}
${BASIC}=          basic
${AUTHVALUE}=      UWLoPObt6Bb837uJ4jbDYRoQ7zu7svyxeJh4NGY6IT/QjIOOsNA+AaHIGP/G0Bp7dWJLiEytrjPC+NjIGfeRrA==
${Reg_Id}=         aic6
${Vf_Mod_Id}=      vf_module_uuid-006
${Vf_Mod_Name}=    test_stack_006
${Stack_Name}=     test_stack_006
${Vnf_Id}=         vnf_id_test-006
${Create_Group_EP}=    /groups/v1/
${Req_ID}=         GPlcp
${Tenant_ID}=      00000000000000000000000000000000
${Vnf_Name}=       vnf_name_test-006
${Name}=           new_rule_1
${Prior_req_id}=    testrackdiv01
${Type}=           affinity
${Level}=          rack

*** Test Cases ***
HealthCheck API
    [Documentation]    GET Call to confirm that Valet API is running
   
    Create Session   Valet     ${Valet_Host}:${Valet_Port} 
    &{headers}=      Create Dictionary    Content-Type=application/json  
   # ${StepName}    Set Variable    healthcheck
    Log to Console    ******************
    Log to Console    Sending Get Call to check Valet API status
    Log to Console    ${Valet_Host}:${Valet_Port} is URL
    #Log to Console   ${headers}
    ${resp}=     Get Request     Valet    ${Endpoint_API}    headers=${headers}
    Sleep     30s 
    Log to Console     Response from Server ${resp}
    Log to Console     ${resp.status_code}
    Should Be Equal As Integers    ${resp.status_code}    200
    Log to Console     HealthCheck API Test case is Successful
    

HealthCheck Communication
    [Documentation]    GET Call to confirm that the API is running and communicating with Music
     Create Session   Valet     ${Valet_Host}:${Valet_Port} 
    &{headers}=      Create Dictionary    Content-Type=application/json  
   # ${StepName}    Set Variable    healthcheck
    Log to Console    ******************
    Log to Console    Sending Get Call to confirm that the API is running and communicating with Music
   Log to Console    ${Valet_Host}:${Valet_Port} is URL
   # Log to Console    Header is ${headers}
    ${resp}=     Get Request     Valet    ${Endpoint_Ping}    headers=${headers}
    Sleep     30s 
    Log to Console     Response from Server ${resp}
    Log to Console     ${resp.status_code}
    Should Be Equal As Integers    ${resp.status_code}    200
    Log to Console     HealthCheck Communication Test case is Successful

HealthCheck API and Engine       
    [Documentation]    GET Cal to confirm that API and Engine both are running, and able to communicate with each other through Music
     Create Session   Valet     ${Valet_Host}:${Valet_Port} 
    &{headers}=      Create Dictionary    Content-Type=application/json  
   # ${StepName}    Set Variable    healthcheck
    Log to Console    ******************
    Log to Console    Sending Get Call to confirm that the API is running and communicating with Music
    Log to Console    ${Valet_Host}:${Valet_Port} is URL
    #Log to Console    Header is  ${headers}
    ${resp}=     Get Request     Valet    ${Endpoint_Health}    headers=${headers}
    Sleep     30s 
    Log to Console     Response from Server ${resp}
    Log to Console     ${resp.status_code}
    Should Be Equal As Integers    ${resp.status_code}    200
    Log to Console     HealthCheck API and Engine Test case is Successful

