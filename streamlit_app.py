import streamlit as st
from zeep import Client, Settings
from zeep.transports import Transport
import xml.etree.ElementTree as ET

st.title('Solicitudes Internas')

# st.write('Hello Andrew!')

fromuser = st.text_input("Matrícula Solicitante:")
fromusername = st.text_input("Nombre Solicitante:")
subject = st.text_input("Asunto:")
details = st.text_area("Detalles:")
touser = st.text_input("Matrícula Destinatario:")
tousername = st.text_input("Nombre Destinatario:")
client = st.text_input("Cliente asociado")

# --- Configuration ---
WSDL_URL = "https://sgs.softexpert.cl/se/ws/wf_ws.php?wsdl" 
ENDPOINT_URL = "https://sgs.softexpert.cl/apigateway/se/ws/wf_ws.php" 
# IMPORTANT: Replace with your actual SOAP service method name
SOAP_SERVICE_METHOD = "newWorkflowEditData"
# Your API Key header name
API_KEY_HEADER_NAME = "Authorization" 
process_id = '02-SIGSE-CVP000003'

# --- API Call Button ---
if st.button("Registrar"):
        st.info("Llamando API... Por favor esperar.")
        st.session_state.wsdl_url_input = WSDL_URL
        st.session_state.soap_method_input = SOAP_SERVICE_METHOD
        st.session_state.soap_endpoint_url_input = ENDPOINT_URL
        # 1. Prepare HTTP Headers for the API Key
        http_headers = {
            API_KEY_HEADER_NAME: st.secrets["workflow_api_key"]
        }
        #transport = Transport(timeout=30, headers=http_headers)

        client = Client('https://sgs.softexpert.cl/se/ws/wf_ws.php?wsdl')
        test = client.service.newWorkflowEditData()
        st.title(test)


        # 2. Initialize Zeep Client
        #settings = Settings(strict=False, xml_huge_tree=True)
        client = Client(
                wsdl=st.session_state.wsdl_url_input,
                transport=None, 
                settings=None,
                wsse=None, 
                service_name=None, 
                port_name=None, 
                service_url=st.session_state.soap_endpoint_url_input,
                plugins=None
            )

        # 3. Construct SOAP Body Parameters
        soap_params = {
            'ProcessId': process_id,
            'WorkflowTitle': subject,
            'UserID': fromuser,
            'EntityID':'sigsecvp01',
            'texto7': fromuser,
            'texto6': fromusername,
            'texto8': touser,
            'texto9': tousername,
            'texto5': subject,
            'paragrafo13': details,
            'texto4': client
        }

        # 4. Call the SOAP Service
        with st.spinner(f"Ejecutando método: {st.session_state.soap_method_input}..."):
            service_method = getattr(client.service, st.session_state.soap_method_input)
            response = service_method(**soap_params)

        st.success("Registro exitoso!")
        st.json(response)


