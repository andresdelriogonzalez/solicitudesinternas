import streamlit as st
from zeep import Client, Settings
from zeep.transports import Transport
import xml.etree.ElementTree as ET
from requests.exceptions import HTTPError
from requests import Session

st.title('Nueva Solicitud Interna - SIGSE')

# st.write('Hello Andrew!')

fromuser = st.text_input("Matrícula Solicitante:")
fromusername = st.text_input("Nombre Solicitante:")
subject = st.text_input("Asunto:")
details = st.text_area("Detalles:")
touser = st.text_input("Matrícula Destinatario:")
tousername = st.text_input("Nombre Destinatario:")
client_asociado = st.text_input("Cliente asociado")

# --- Configuration ---
WSDL_URL = "https://sgs.softexpert.cl/se/ws/wf_ws.php?wsdl" 
ENDPOINT_URL = "https://sgs.softexpert.cl/apigateway/se/ws/wf_ws.php" 
# IMPORTANT: Replace with your actual SOAP service method name
SOAP_SERVICE_METHOD_1 = "newWorkflowEditData"
SOAP_SERVICE_METHOD_2 = "executeActivity"
# Your API Key header name
API_KEY_HEADER_NAME = "Authorization" 
process_id = '02-SIGSE-CVP000003'
DEFAULT_BINDING_NAME = '{urn:workflow}WorkflowBinding' 

# --- API Call Button ---
if st.button("Registrar"):
        st.info("Llamando API... Por favor esperar.")
        st.session_state.wsdl_url_input = WSDL_URL
        st.session_state.soap_method_1 = SOAP_SERVICE_METHOD_1
        st.session_state.soap_method_2 = SOAP_SERVICE_METHOD_2
        st.session_state.soap_endpoint_url_input = ENDPOINT_URL
        st.session_state.binding_name_input = DEFAULT_BINDING_NAME

        # 1. Prepare HTTP Headers for the API Key
        http_headers = {
            API_KEY_HEADER_NAME: st.secrets["workflow_api_key"]
        }

        try:
            # --- DEBUGGING OUTPUTS (before Transport) ---
            # st.info(f"DEBUG: WSDL URL: {st.session_state.wsdl_url_input}")
            # st.info(f"DEBUG: SOAP Endpoint URL: {st.session_state.soap_endpoint_url_input}")
            # st.info(f"DEBUG: Binding Name: {st.session_state.binding_name_input}")
            # st.info(f"DEBUG: API_KEY_HEADER_NAME type: {type(API_KEY_HEADER_NAME)}, value: {API_KEY_HEADER_NAME}")
            # st.info(f"DEBUG: API_KEY type: {type(st.secrets["workflow_api_key"])}, value: {'*' * len(st.secrets["workflow_api_key"])}") # Mask API key for security
            # st.info(f"DEBUG: http_headers type: {type(http_headers)}, value: {http_headers}")
            # st.info(f"DEBUG: timeout value: 30, type: {type(30)}")
            # --- END DEBUGGING OUTPUTS ---


            # 2. Initialize Zeep Client
            session = Session()
            session.headers.update(http_headers)
            transport = Transport(session=session)
            settings = Settings(strict=False, xml_huge_tree=True)
            client = Client(
                    st.session_state.wsdl_url_input,
                    transport = transport,
                    settings=settings
                )

            service = client.create_service(
                st.session_state.binding_name_input, 
                st.session_state.soap_endpoint_url_input
)

            # 3. Construct SOAP Body Parameters
            soap_params = {
                'ProcessID': process_id, 
                'WorkflowTitle': subject,
                'UserID': fromuser,
                'EntityList': {
                    'Entity': [
                        {
                            'EntityID':'sigsecvp01',
                            'EntityAttributeList': {
                                'EntityAttribute': [
                                    {'EntityAttributeID': 'texto7', 'EntityAttributeValue': fromuser},
                                    {'EntityAttributeID': 'texto6', 'EntityAttributeValue': fromusername},
                                    {'EntityAttributeID': 'texto8', 'EntityAttributeValue': touser},
                                    {'EntityAttributeID': 'texto9', 'EntityAttributeValue': tousername},
                                    {'EntityAttributeID': 'texto5', 'EntityAttributeValue': subject},
                                    {'EntityAttributeID': 'paragrafo13', 'EntityAttributeValue': details},
                                    {'EntityAttributeID': 'texto4', 'EntityAttributeValue': client_asociado}
                                ]
                            }
                        }
                    ]
                }
            }

            # 4. Call the SOAP Service
            with st.spinner(f"Ejecutando método: {st.session_state.soap_method_1}..."):
                service_method_1 = getattr(service, st.session_state.soap_method_1)
                response_1 = service_method_1(**soap_params)

            recordID = response_1['RecordID']

            # Parameters for execution of activity
            soap_params_exec = {
                'WorkflowID': recordID, 
                'ActivityID': 'Atividade25525151225202',
                'ActionSequence': 1,
                'UserID': fromuser,
                'ActivityOrder' : None
            }

            with st.spinner(f"Ejecutando método: {st.session_state.soap_method_2}..."):
                service_method_2 = getattr(service, st.session_state.soap_method_2)
                response_2 = service_method_2(**soap_params_exec)

            # st.success("Ejecución de actividad exitosa!")
            # st.write(response_2)

            # st.write("Fue creada la solicitud Nº: ", recordID, " :sunglasses:")
            st.info("Fue creada la solicitud Nº: ", recordID, " :sunglasses:")

        except HTTPError as e:
            st.error(f"HTTP Error occurred: {e}")
            st.error(f"Status Code: {e.response.status_code}")
            st.error(f"Response Body: {e.response.text}")
            st.warning("This means the server responded with an error (e.g., 404 Not Found, 401 Unauthorized, 500 Internal Server Error).")
            st.warning("Double-check your WSDL URL, SOAP Endpoint URL, API Key, and network connectivity.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.warning("Please check the WSDL URL, service method, and input parameters. Also ensure your network allows access to the WSDL.")

