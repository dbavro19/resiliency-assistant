import streamlit as st
import boto3
import botocore
from diagram_discovery import image_to_workflow_details, image_to_component_list
from template_discovery import template_to_workflow_details, template_to_component_list
from rules_engine import return_component_rules
from raf_report import raf_report_output



st.set_page_config(page_title="Resiliency AI", page_icon=":mag", layout="wide")

#Headers
with st.container():
    st.header("Architecture Resiliency Assistant")
    st.title("Upload your an image of your architecture")



#Streamlit workflow
allowed_types = ["png", "jpg", "jpeg", "yaml", "tf"]
uploaded_file = st.file_uploader(
    "Choose Image or Template",
    type=allowed_types,
    help="Supported formats: XML, JSON, PNG, JPEG"
)




go = st.button("Analyze Architecture")
if go:
    st.write(uploaded_file.name)
    file_type= uploaded_file.type

    if uploaded_file is not None:
        # Get the file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension in ["png", "jpg", "jpeg"]:
            with st.expander("Image uploaded successfully"):
                st.image(uploaded_file)

            #Image Logic
            details = image_to_workflow_details(uploaded_file, file_type)
            with st.expander("Workflow Details"):
                st.write(details)
            components = image_to_component_list(uploaded_file, file_type)
            with st.expander("Components / AWS Services"):
                st.write(components)





        elif file_extension in ["yaml", "tf"]:
            content = uploaded_file.getvalue().decode("utf-8")
            with st.expander("Template uploaded successfully"):
                st.code(content, line_numbers=True, language="yaml")

            #Template Logic
            details = template_to_workflow_details(content)
            with st.expander("Workflow Details"):
                st.write(details)
            components = template_to_component_list(content)
            with st.expander("Components / AWS Services"):
                st.write(components)
        
        else:
            st.error("Unsupported file type. Please upload an image or template.")


        #Continue app logic here
        st.write("Getting Component Rules")

        rules_string = ""
        for component in components:
            rules_string += return_component_rules(component)


        #Send info to final prompts

        report,improvements = raf_report_output(details, rules_string)

        with st.expander("Resiliency Report"):
            st.markdown(report)

        with st.expander("Improvements"):
            st.markdown(improvements)

    else:
        st.error("Please upload a file")