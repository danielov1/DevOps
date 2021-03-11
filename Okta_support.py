#!/usr/bin/env python

import asyncio
import boto3
import requests
import json
import time
import sys
from tkinter import messagebox

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
            'ParameterValue': 'https://dev-45738533.okta.com/api/v1/apps/0oaar4suuYAHO1mGo5d6/sso/saml/metadata',
            'UsePreviousValue': True
        },
        ],
        TimeoutInMinutes=123,
        Capabilities=[
            'CAPABILITY_NAMED_IAM'
        ],
    )

    cfnr = boto3.resource('cloudformation',  
        aws_access_key_id=keyid.get(),
        aws_secret_access_key=secretKey.get(),
        region_name='us-east-1')

    stack = cfnr.Stack('CLDZE-ROLES')

    i = 0
    STACK_NAME = 'CLDZE-ROLES'
    
    ## Check if the task was created succefully

    while stack.stack_status == 'CREATE_IN_PROGRESS':
        i = i+1
        print("Stack create state is CREATE_IN_PROGRESS")
        if(i>10):
            break
        time.sleep(10)
        stack = cfnr.Stack('CLDZE-ROLES')
        
    if stack.stack_status == 'CREATE_COMPLETE':
        print(" ")
        print(" ")
        print("Stack create completed")
        response = client.list_stack_resources(StackName=STACK_NAME)
        receivedARN = response["StackResourceSummaries"][3]['PhysicalResourceId']

        ## Update Identity Provider ARN for SAML SSO on Okta
        print("Updating " + appNameAWS.get() + " account ARN...")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'SSWS '+ apiKey.get() +''}

        data = '{ "name": "amazon_aws", "label": "' + appNameAWS.get() + '", "settings": { "app": { "identityProviderArn":''"'+ receivedARN +'"'' } } }' #recivedARN value from stack output
        response = requests.put('https://dev-45738533.okta.com/api/v1/apps/'+ appID +'', headers=headers, data=data)

        responseJson = json.loads(response)
        arnCheck = (responseJson['settings']['app']['identityProviderArn'])

        ## Add Finops Group to app

        finOpsGroup = '00gaibifzx5yZB5s35d6' ## Finops Group ID

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'SSWS '+ apiKey.get() +''}
        data = '{ }'
        response = requests.put('https://dev-45738533.okta.com/api/v1/apps/'+ appID +'/groups/' + finOpsGroup + '', headers=headers, data=data)


        ## Check if ARN was updated

        if arnCheck != "":
            print("ARN was updated successfuly")
            print("")
            print("")
            print("Resource created: ")
            print("AWS linked account")
            print("AWS stack on CloudFormation")
            print("ARN configured on '" + appNameAWS.get() + "'")

            ## Next actions which can't be automated
            OKTAuserAccessKey = (stack.outputs[0]['OutputValue'])
            OKTAuserSecretKey = (stack.outputs[2]['OutputValue'])
            print("")
            print("")
            print("Next actions:")
            print("1. configure Provisioning on '" + appNameAWS.get() + "' linked account using the following Access & Secret keys:")
            print("Access key: '" + OKTAuserAccessKey +"' ")
            print("Secret key: '" + OKTAuserSecretKey +"' ")
            print("2. configure MFA Policy on '" + appNameAWS.get() + "' linked account")
        

        else:
            print("ARN update failed")
            messagebox.showerror("Info","ARN update failed")
            print("")
            print("")
            print("Resource created: ")
            print("AWS linked account")
            print("AWS stack on CloudFormation")
            sys.exit()

    else:
        print(" ")
        print(" ")
        print("Stack create is failed, please check on AWS CF events what the reason is")
        messagebox.showerror("Info","Stack create is failed, please check on AWS CF events what the reason is")
        print("")
        print("")
        print("Resource created: ")
        print("AWS linked account")
        sys.exit()


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top

def startFunc():
    ## Create AWS Application on Okta
    print("Creating AWS linked account on Okta...")

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'SSWS '+ apiKey.get() +''}

    data = '{ "name": "amazon_aws", "label": "' + appNameAWS.get() + '", "signOnMode": "SAML_2_0", "visibility":{ "autoSubmitToolbar":true, "hide":{ "iOS":false, "web":false } }, "credentials": { "userNameTemplate": { "template":"${source.email}", "type":"BUILT_IN" } }, "settings": { "app": { "requestIntegration": false, "loginURL": "https://'+accountNum.get()+'.signin.aws.amazon.com/console", "sessionDuration":43200 } } }'
    response = requests.post('https://dev-45738533.okta.com/api/v1/apps', headers=headers, data=data)
    responseOrg = response.text
    sys.stdout.flush()
    
    ## Take metadata URL to variable

    responseJson = json.loads(responseOrg)
    
    metadataURL = (responseJson['_links']['metadata']['href'])
    appID = (responseJson['id'])
    if id != "":
        print("AWS linked account configured succesfully")
    else:
        print("AWS linked account configuration failed")
        messagebox.showerror("Info","AWS linked account configuration failed")
        print("")
        print("")
        print("No reasorce was configured")
        sys.exit()
        
    
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




