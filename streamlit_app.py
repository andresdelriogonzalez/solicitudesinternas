import streamlit as st

st.title('🎈 Solicitudes Internas')

st.write('Hello Andrew!')

fromuser = st.text_input("Solicitante:")
subject = st.text_input("Asunto:")
details = st.text_area("Detalles:")
touser = st.text_input("Destinatario:")
client = st.text_input("Cliente asociado")

