import boto3



def get_rules(component):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('raf_rules_engine')
    
    # Define which fields you want to retrieve
    projection_expression = "rule_id, component, raf_property, threat_category, threat, impact_observability, preventative_measures, reactive_measures"
    
    # Create the filter expression for the component
    filter_expression = boto3.dynamodb.conditions.Attr('component').eq(component)
    
    try:
        response = table.scan(
            FilterExpression=filter_expression,
            ProjectionExpression=projection_expression
        )
        
        items = response['Items']
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression=filter_expression,
                ProjectionExpression=projection_expression,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response['Items'])
        
        return items
    
    except Exception as e:
        print(f"Error retrieving rules: {e}")
        return []
    

def return_component_rules(component_name):
    # Filter rules for the specified component
    component_rules = get_rules(component_name)
    
    formatted_output = f"\n <Resiliency Rules for {component_name}>:\n"
    
    for rule in component_rules:
        # Store each value in variables with default values for missing keys
        rule_id = rule.get('rule_id', 'N/A')
        raf_property = rule.get('raf_property', 'N/A')
        threat = rule.get('threat', 'N/A')
        threat_category = rule.get('threat_category', 'N/A')
        impact_obs = rule.get('impact_observability', 'N/A')
        preventative = rule.get('preventative_measures', 'N/A')
        reactive = rule.get('reactive_measures', 'N/A')
        
        # Build formatted string using f-strings
        rule_details = f"""
Rule ID: {rule_id}
RAF Property: {raf_property}
Threat: {threat}
Threat Category: {threat_category}
Impact & Observability: {impact_obs}
Preventative Measures: {preventative}
Reactive Measures: {reactive}
"""
        
        formatted_output += rule_details
    
    # Add final newline for separation between components
    formatted_output += f"</Resiliency Rules for {component_name}> \n"
    
    return formatted_output





