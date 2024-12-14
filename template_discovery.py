

import boto3
import botocore
import streamlit as st
import base64
from PIL import Image
import io
import json
from misc_functions import parse_xml


config = botocore.config.Config(connect_timeout=500, read_timeout=500)
bedrock = boto3.client('bedrock-runtime' , 'us-east-1', config = config)

def template_to_workflow_details(template_content):



    #setup prompt
    system_prompt=f"""
You are an AWS Solutions Architect. You will be provided a Infrastructure as Code template (CloudFormation or Terraform) of an application or workflow. 
Based on the provided template your goal is to provide a detailed description of the following
    1. Overview of the workflow
    2. Details of each component and service, including which components are container within each other and their relationship to each other
    3. The workflow and data flow of the application, including how components are connected and related to each other
    4. The Key Design Principals that are represented in the template

This should be written from the perspective of the Solutions architect who created the diagram with the goal of documenting how the infrastructure was built
The Details should provide robust but concise information and of the following
     The grouping of each component/service - i.e. AZ 1 contains x,y,z. Public Subnet 1 contains z,y,z etc.
     The responsibility of each component
     The relationship between the groupings and components
     The workflow/data flow of the overall solution

Use the below example as a guide for you output format:
<format_example>

Workflow: Two tier, container based web application hosted on AWS (Amazon Web Services) with high availability and data replication across multiple Availability Zones 

Details:
	1. Web App: This represents the web application that users will interact with.
	2. Internet: The web application is accessible over the internet.
	3. AWS: The web application is hosted on the AWS cloud platform. Within AWS, the architecture consists of the following components:
	• Availability Zones (AZs):
		○ AZ 1: This availability zone contains the following resources:
			§ Public Subnet: A public subnet that allows inbound internet traffic.
				□ EC2 Web App: One or more EC2 instances running the web application, behind the load balancer.
			§ Private Subnet: A private subnet with no direct internet access.
				□ RDS: An Amazon Relational Database Service (RDS) instance, likely used to store and retrieve data for the web application.
				
		○ AZ 2: This is a second availability zone for high availability and fault tolerance. It contains the following resources:
			§ Public Subnet: A public subnet that allows inbound internet traffic.
				□ EC2 Web App: One or more EC2 instances running the web application.
			§ Private Subnet: A private subnet with no direct internet access.
				□ RDS: An Amazon Relational Database Service (RDS) instance.
	• ALB: An Application Load Balancer (ALB) that distributes incoming traffic across the two availability zones (AZ 1 and AZ 2) for high availability and fault tolerance.
	• Replication: There is data replication between the RDS instances in the two availability zones to ensure data consistency and availability in case of a failure in one availability zone.
	
The workflow is as follows:
	1. Users access the web application over the internet.
	2. The Application Load Balancer (ALB) distributes incoming traffic across the two availability zones (AZ 1 and AZ 2).
	3. In each availability zone, the Elastic Load Balancer (ELB) distributes traffic across the EC2 instances running the web application.
	4. The web application instances retrieve and store data from/to the RDS instances in the private subnets.
	5. Data is replicated between the RDS instances in the two availability zones for high availability and fault tolerance.

Key Design Principals:
    1. High Availability: Using multiple AZs ensures the application remains available even if one AZ fails
    2. Security: Private subnets are used for sensitive components (ECS and RDS)
    3. Scalability: The ALB can distribute load across multiple instances
    4. Data Redundancy: Database replication ensures data is backed up and available across zones

</format_example>

Your response will be used downstream to identify improvements to the design, specifically for resiliency and security, so ensure that everything that all details and components are captured and the relationships and workflows between components are captured in your details
Pay extra attention to accuracy and including everything that will be needed to recreate a diagram, and a fully functioning Cloud Formation Infrastructure as Code template

Think through each step of your thought process, and pay extra attention to providing accurate details.
    
Provide your response in <details> xml tags
"""

    prompt = {
        "anthropic_version":"bedrock-2023-05-31",
        "max_tokens":10000,
        "temperature":0,
        "system": system_prompt,
        "messages":[
            {
                "role":"user",
                "content":[
                    {  
                        "type":"text",
                        "text": f"<IaC_template> {template_content} </IaC_template>"
                    }
                ]
            }
        ]
    }

    json_prompt = json.dumps(prompt)

    response = bedrock.invoke_model(body=json_prompt, modelId="anthropic.claude-3-sonnet-20240229-v1:0", accept="application/json", contentType="application/json")


    response_body = json.loads(response.get('body').read())

    llmOutput=response_body['content'][0]['text']

    print(llmOutput)

    details = parse_xml(llmOutput, "details")

    return details



def template_to_component_list(template_content):


    #setup prompt
    system_prompt=f"""
You are an AWS Solutions Architect analyzing an Infrastructure as Code Template. Your task is to identify AWS services that are EXPLICITLY deployed in the template, but ONLY if they exactly match the following approved services list:

<Valid_AWS_Services>
EC2
RDS
VPC
S3
CloudFront
API Gateway
Lambda
Dynamo DB
SNS
SQS
EKS
ECS
</Valid_AWS_Services>

Rules:
1. Only include services that match the services provided in the Valid_AWS_Services list
2. Ignore any AWS services visible in the diagram that aren't in the Valid_AWS_Services list
3. Convert identified services to use the naming convention, spelling and capitalization from the Valid_AWS_Services list. 

Return only the identified services in a comma-separated list within <components> tags. Do not include any explanations or additional text.

Example correct output:
<components>Dynamo DB,ECS</components>
"""

    prompt = {
        "anthropic_version":"bedrock-2023-05-31",
        "max_tokens":10000,
        "temperature":0,
        "system": system_prompt,
        "messages":[
            {
                "role":"user",
                "content":[
                    {  
                        "type":"text",
                        "text": f"<IaC_template> {template_content} </IaC_template>"
                    }
                ]
            }
        ]
    }

    json_prompt = json.dumps(prompt)

    response = bedrock.invoke_model(body=json_prompt, modelId="anthropic.claude-3-sonnet-20240229-v1:0", accept="application/json", contentType="application/json")


    response_body = json.loads(response.get('body').read())

    llmOutput=response_body['content'][0]['text']

    print(llmOutput)

    results = parse_xml(llmOutput, "components")



    # Convert and return list of components
    component_list = [item.strip() for item in results.split(',')]

    return component_list