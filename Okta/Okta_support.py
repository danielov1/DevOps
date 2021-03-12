#!/usr/bin/env python

import botocore
import asyncio
import boto3
import requests
import json
import time
import sys
from tkinter import messagebox
import tkinter as tk

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


def create_window():
    window = tk.Toplevel(root)


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
            'Authorization': 'SSWS '+ apiKey.get() +'',
            }

        response = requests.get('https://dev-45738533.okta.com/api/v1/authorizationServers', headers=headers)
        if response.status_code == 200:
            messagebox.showinfo("Info","The application is running...")
            stack_exist_check()
        else:
            messagebox.showerror("Info","Okta API token is invalid")
    except botocore.exceptions.ClientError:
        messagebox.showerror("Info","AWS credentials are invalid")


## Check if stack exist on CloudFormation

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
            'ParameterValue': "'"+ metadataURL +"'",
            'UsePreviousValue': True
        },
        ],
        TimeoutInMinutes=123,
        Capabilities=[
            'CAPABILITY_NAMED_IAM'
        ],
    )


    ## Check if the task was created succefully

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
        time.sleep(10)
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
            root = tk.Tk()
            root.mainloop()
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
        print("Stack create is failed, please check on AWS CF events")
        messagebox.showerror("Info","Stack create is failed, please check on AWS CF events")
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

## Create AWS Application on Okta

def startFunc():
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





