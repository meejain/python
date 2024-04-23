import requests
import re
import json
import sys
import time
import collections
disabledaccesslogsALB=[]
disabledaccesslogsELB=[]

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("Could not import 'boto3', please install this package.")

def list_of_alb(argBPBU,arg_profile):
    for AWS_REGION in argBPBU:
        disabledaccesslogsALB.clear()
        print("For AWS Region - " + AWS_REGION)
        session1 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
        alb = session1.client('elbv2')
        response = alb.describe_load_balancers()
        for lb in response['LoadBalancers']:
            print("-" * 6)
            print("Name:", lb['LoadBalancerName'])
            att = alb.describe_load_balancer_attributes(LoadBalancerArn=lb['LoadBalancerArn'])
            print (att)
            if att['Attributes'][0]['Value'] == "false":
                disabledaccesslogsALB.append(lb['LoadBalancerName'])
                print(att['Attributes'][0]['Value'])
        print("The list of ALB's whose access logs are disabled for the region " + AWS_REGION + " in " + BPBU + " - ")
        print(disabledaccesslogsALB);




def list_of_elb(argBPBU,arg_profile):
    for AWS_REGION in argBPBU:
        disabledaccesslogsELB.clear()
        print("For AWS Region - " + AWS_REGION)
        session2 = boto3.Session(profile_name=arg_profile, region_name=AWS_REGION)
        elb = session2.client('elb')
        response1 = elb.describe_load_balancers()
        for lb in response1['LoadBalancerDescriptions']:
            print("-" * 6)
            print("Name:", lb['LoadBalancerName'])
            att1 = elb.describe_load_balancer_attributes(LoadBalancerName=lb['LoadBalancerName'])
            print(att1['LoadBalancerAttributes']['AccessLog']['Enabled'])
            if att1['LoadBalancerAttributes']['AccessLog']['Enabled'] == "False":
                disabledaccesslogsELB.append(lb['LoadBalancerName'])
        print("The list of ELB's whose access logs are disabled for the region " + AWS_REGION + " in " + BPBU + " - ")
        print(disabledaccesslogsELB);






def main():
    global BPBU
    global AWS_REGION
    BPBU17 = ["us-east-2", "us-east-1", "us-west-1", "us-west-2", "ca-central-1", "sa-east-1"]
    BPBU18 = ["ap-south-1", "ap-northeast-2", "ap-northeast-1", "ap-southeast-2", "ap-southeast-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "ap-northeast-3"]
    BPBU10 = ["us-east-2", "us-east-1", "us-west-1", "us-west-2", "ca-central-1", "sa-east-1","ap-south-1", "ap-northeast-2", "ap-northeast-1", "ap-southeast-2", "ap-southeast-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "ap-northeast-3"]
    BPBU11 = ["us-east-2", "us-east-1", "us-west-1", "us-west-2", "ca-central-1", "sa-east-1","ap-south-1", "ap-northeast-2", "ap-northeast-1", "ap-southeast-2", "ap-southeast-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "ap-northeast-3"]
    print('Enter the BPBU ')
    BPBU = str(input(""))
    if BPBU == "bpbu17":
        profile = 'bpbu17'
        list_of_alb(BPBU17, profile)
        list_of_elb(BPBU17, profile)
    elif BPBU == "bpbu18":
        profile = 'bpbu18'
        list_of_alb(BPBU18,profile)
        list_of_elb(BPBU18, profile)
    elif BPBU == "bpbu10":
        profile = 'bpbu10'
        list_of_alb(BPBU10, profile)
        list_of_elb(BPBU10, profile)
    elif BPBU == "bpbu11":
        profile = 'bpbu11'
        list_of_alb(BPBU11, profile)
        list_of_elb(BPBU11, profile)




main()



