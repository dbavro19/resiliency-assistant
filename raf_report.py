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




def raf_report_output(overview, rules):


    #setup prompt
    system_prompt=f"""
You are an AWS Solutions architect tasked with analyzing the resiliency posture of an application or workflow according to the AWS Resiliency Architecture Framework to generate a "Resiliency Report" based on the details of the workflow/application provided
You wil also make specific recommendations on how to enhance the resiliency and availability posture for the workflow overall, as well as specifics for the services leveraged based on the results from the "component_rule_engine_result" if they apply

Your report will follow this format
<report_format>

1. Single Points of Failure Assessment (Critical/High/Medium/Low)
   - Redundancy Architecture
   - Failure Impact Analysis
   - Availability Zone Dependencies
   - Component Interdependencies

2. Latency Analysis:
   - Component Latency Patterns
   - Timeout Configurations
   - Retry Strategies
   - Performance Bottlenecks
   - Network Dependencies
   - Failure Propagation Paths

3. Load Management Assessment:
   - Overload Scenarios
   - Circuit Breaker Configurations
   - Scaling Mechanisms
   - Resource Quotas and Limits
   - Backlog Management
   - Bimodal Behavior Patterns

4. Configuration and Bug Prevention:
   - Deployment Safety Mechanisms
   - Rollback Capabilities
   - Operational Guardrails
   - Critical Expirations
   - Change Management Controls

5. Shared Fate Analysis:
   - Fault Isolation Boundaries
   - Component Dependencies
   - Partial Failure Scenarios
   - Gray Failure Impacts
   - Resource Sharing Assessment



Please provide specific:
1. Risk ratings for each category
2. Concrete examples of potential failure modes
3. Practical mitigation strategies
4. Critical implementation gaps
5. Immediate action items
6. Long-term recommendations

</report_format>

Lastly you will make recommendations for the service specific considerations using your intimate knowledge of AWS resiliency best practices and the provided list of service computes rules

<component_rule_engine_result>
{rules}
</component_rule_engine_result>


think carefully through each step and write it down in <thinking> xml tags

return your resiliency report in <report_output> xml tags in valid markdown with no extra text

return your service improvement recommendations in <service_improvements> xml tags in valid markdown with no extra text


"""

    prompt = {
        "anthropic_version":"bedrock-2023-05-31",
        "max_tokens":4096,
        "temperature":0,
        "system": system_prompt,
        "messages":[
            {
                "role":"user",
                "content":[
                    {  
                        "type":"text",
                        "text": f"<workload_overview> {overview} </workload_overview>"
                    }
                ]
            }
        ]
    }

    json_prompt = json.dumps(prompt)

    response = bedrock.invoke_model(body=json_prompt, modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0", accept="application/json", contentType="application/json")


    response_body = json.loads(response.get('body').read())

    llmOutput=response_body['content'][0]['text']

    print(llmOutput)

    report_output = parse_xml(llmOutput, "report_output")
    service_improvements = parse_xml(llmOutput, "service_improvements")


    return report_output, service_improvements