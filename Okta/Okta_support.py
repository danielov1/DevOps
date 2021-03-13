#!/usr/bin/env python
import botocore
import asyncio
import boto3
import requests
import json
import time
from okta.client import Client as OktaClient
import sys
from tkinter import messagebox
from botocore.exceptions import ClientError
from tkinter import *
import ast
import asyncio
import re

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True


def set_Tk_var():
    global appNameAWS
    appNameAWS = tk.StringVar()
    global accountNum
    accountNum = tk.StringVar()
    global keyid
    keyid = tk.StringVar()
    global secretKey
    secretKey = tk.StringVar()
    global apiKey
    apiKey = tk.StringVar()


oktaDomain = 'https://dev-45738533.okta.com'


## Open a new windows for next action plan

def openNewWindow(OKTAuserSecretKey,OKTAuserAccessKey):
    master = Tk() 
    master.geometry("200x200") 
    label = Label(master,  
                text ='The following actions must be configured menually: \n\n1. configure Provisioning on ' + appNameAWS.get() + 'linked account using the following Access & Secret keys(printed on terminal also):\n Access key: ' + OKTAuserAccessKey +'\n Secret key: ' + OKTAuserSecretKey +'\n - Click "Configure API Integration"\n - Enable "Create Users"\n\n 2. configure MFA Policy on ' + appNameAWS.get() + ' linked account\n - Select “Add Rule”- Rule Name: MFA Select Prompt for factor> Once per session Click Save', anchor="e", justify=LEFT, font='freesansbold')
    label.pack(pady = 10)
    master.title('Next actions')
    master.minsize(800,300)
    mainloop()

## Check Credentials on Okta & AWS

def checkCredentials():
    sts = boto3.client('sts',
        aws_access_key_id=keyid.get(),
        aws_secret_access_key=secretKey.get(),
        region_name='us-east-1')

    try:
        sts.get_caller_identity()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'SSWS '+ apiKey.get()}

        response = requests.get(oktaDomain +'/api/v1/authorizationServers', headers=headers)
        if response.status_code == 200:
            
            ## Check application name
            pattern = re.compile("(\w*)-(\d*)")
            appNameCheck = str(pattern.search(appNameAWS.get()))
            if appNameCheck == "None":
                messagebox.showinfo("Info","Application name is invalid, Application name must contains <cust_name>-<account_num>")
            else:
                messagebox.showinfo("Info","The application is running...")
                stack_exist_check()
        else:
            messagebox.showerror("Info","Okta API token is invalid")
    except botocore.exceptions.ClientError:
        messagebox.showerror("Info","AWS credentials are invalid")


## Check if stack exists on CloudFormation

def stack_exist_check():

    client = boto3.client('cloudformation',
    aws_access_key_id=keyid.get(),
    aws_secret_access_key=secretKey.get(),
    region_name='us-east-1')

    try:
        client.describe_stacks(StackName='CLDZE-ROLES')
        messagebox.showinfo("Info","Stack already exist on CloudFormation")
    except botocore.exceptions.ClientError as e:
        if "does not exist" in e.response['Error']['Message']:
            startFunc()
        else:
            raise e
    


## Function Create Stack on CloudFormation

def createStackCF(metadataURL,appID):
    template = "https://s3-eu-west-1.amazonaws.com/cloudzone-external/CLDZE_ROLES.yaml"

    print("Creating a new stack on CloudFormation...")
    
    client = boto3.client('cloudformation',
    aws_access_key_id=keyid.get(),
    aws_secret_access_key=secretKey.get(),
    region_name='us-east-1')

    response = client.create_stack(
        StackName='CLDZE-ROLES',
        TemplateURL=template,
        Parameters=[
        {
            'ParameterKey': 'IDP',
            'ParameterValue': 'CLDZE_OKTA_SAML',
            'UsePreviousValue': True
        },
        {
            'ParameterKey': 'OKTAUSERNAME',
            'ParameterValue': 'CLDZE_OKTA_CF',
            'UsePreviousValue': True
        },
        {
            'ParameterKey': 'Metadata',
            'ParameterValue': metadataURL,
            'UsePreviousValue': True
        },
        ],
        TimeoutInMinutes=123,
        Capabilities=[
            'CAPABILITY_NAMED_IAM'
        ],
    )


    ## Check if the task was created successfully

    stackResource = boto3.resource('cloudformation',  
    aws_access_key_id=keyid.get(),
    aws_secret_access_key=secretKey.get(),
    region_name='us-east-1')

    stack = stackResource.Stack('CLDZE-ROLES')
    i = 0
    while stack.stack_status == 'CREATE_IN_PROGRESS':
        i = i+1
        print("Stack create state is CREATE_IN_PROGRESS")
        if(i>10):
            break
        time.sleep(13)
        stack = stackResource.Stack('CLDZE-ROLES')
        
    if stack.stack_status == 'CREATE_COMPLETE':
        print(" ")
        print(" ")
        print("Stack create completed")
        response = client.list_stack_resources(StackName='CLDZE-ROLES')
        receivedARN = response["StackResourceSummaries"][3]['PhysicalResourceId']

        ## Update Identity Provider ARN for SAML SSO on Okta

        print("Updating " + appNameAWS.get() + " account ARN...")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'SSWS '+ apiKey.get()}

        data = '{ "name": "amazon_aws", "label": "' + appNameAWS.get() + '", "settings": { "app": { "identityProviderArn":''"'+ receivedARN +'"'' } } }' #recivedARN value from stack output
        response = requests.put(oktaDomain +'/api/v1/apps/'+ appID +'', headers=headers, data=data)

        responseJson = json.loads(response)
        arnCheck = (responseJson['settings']['app']['identityProviderArn'])

        ## Add Finops Group to app

        finOpsGroup = '00gaibifzx5yZB5s35d6' ## Finops Group ID

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'SSWS '+ apiKey.get() }
        data = '{ }'
        response = requests.put(oktaDomain +'/api/v1/apps/'+ appID +'/groups/' + finOpsGroup + '', headers=headers, data=data)


        ## Check if ARN was updated

        if arnCheck != "":
            print("ARN was updated successfuly")
            print("")
            print("")
            print("Resource created: ")
            print("AWS linked account")
            print("AWS stack on CloudFormation")
            print("ARN & Finops group were added to" + appNameAWS.get() + " app")

            ## Next actions which can't be automated

            OKTAuserAccessKey = (stack.outputs[0]['OutputValue'])
            OKTAuserSecretKey = (stack.outputs[2]['OutputValue'])
            print("")
            print("")
            print("Access & Secret keys:")
            print("Access key: '" + OKTAuserAccessKey +"")
            print("Secret key: '" + OKTAuserSecretKey +"")
            openNewWindow(OKTAuserAccessKey,OKTAuserSecretKey)

        

        else:
            print("ARN update failed")
            messagebox.showerror("Info","ARN update failed")
            print("")
            print("")
            print("Resource created: ")
            print("AWS linked account")
            print("AWS stack on CloudFormation")

    else:
        print(" ")
        print(" ")
        print("Stack create is failed, please check on AWS CF events")
        messagebox.showerror("Info","Stack create is failed, please check on AWS CF events")
        print("")
        print("")
        print("Resource created: ")
        print("AWS linked account")



def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top


## Function that take metadata & application ID vars

async def skipFunc(oktaDomain):
    configOkta = {
    'orgUrl': oktaDomain,
    'token': apiKey.get()}
    okta_client = OktaClient(configOkta)
    apps, resp, err = await okta_client.list_applications()
    for app in apps:
        appsList = (app.label,app.id)
        for app.label in appsList:
            if app.label == appNameAWS.get():
                strApp = str(app)
                appJson = ast.literal_eval(strApp)
                metadataURL = (appJson['links']['metadata']['href'])
                appID = (appJson['id'])
                createStackCF(metadataURL,appID)
    


## Create AWS Application on Okta

def startFunc():
    print("Creating AWS linked account on Okta...")

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'SSWS '+ apiKey.get()}

    data = '{ "name": "amazon_aws", "label": "' + appNameAWS.get() + '", "signOnMode": "SAML_2_0", "visibility":{ "autoSubmitToolbar":true, "hide":{ "iOS":false, "web":false } }, "credentials": { "userNameTemplate": { "template":"${source.email}", "type":"BUILT_IN" } }, "settings": { "app": { "requestIntegration": false, "loginURL": "https://'+accountNum.get()+'.signin.aws.amazon.com/console", "sessionDuration":43200 } } }'
    response = requests.post(oktaDomain +'/api/v1/apps', headers=headers, data=data)
    responseOrg = response.text
    sys.stdout.flush()
    responseJson = json.loads(responseOrg)
    
    ## Check POST API call response

    if response.status_code != 200:
        errorMessage = responseJson["errorCauses"][0]["errorSummary"]
        messagebox.showinfo("Info",errorMessage)
        print(errorMessage)
        msgBox = tk.messagebox.askquestion ('Info','Proccess anyway and run a Stack on CloudFormation',icon = 'warning')
        if msgBox == 'yes':

            ## Execute function that skip app creation on Okta and take metadata & application ID vars

            loop = asyncio.get_event_loop()
            loop.run_until_complete(skipFunc(oktaDomain))

        else:
            tk.messagebox.showinfo('Return','You will now return to the application screen')
        
    else:
        ## Take metadata URL to variable named metadataURL

        metadataURL = (responseJson['_links']['metadata']['href'])
        appID = (responseJson['id'])
        
        ## Create Stack on CloudFormation

        print("Execute createStackCF function")
        
        createStackCF(metadataURL,appID)

# Function which closes the window.

def destroy_window():    
    global top_level
    top_level.destroy()
    top_level = None

if __name__ == '__main__':
    import Okta
    Okta.vp_start_gui()





