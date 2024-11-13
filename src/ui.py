import os
import uuid
import base64
from io import StringIO
import streamlit as st

from api_connect import get_response

st.title(":blue[_Barclays New Product Review Assistant_]")

# Initialize session state for unique session identification and file caching
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4()
    st.session_state.document_cache = {}

session_id = st.session_state.session_id

if "file_data" not in st.session_state:
    st.session_state.file_data = None

if "file_key" not in st.session_state:
    st.session_state.file_key = None

# Reset the chat state and clear garbage
def reset_chat_state():
    st.session_state.messages = []
    st.session_state.document_cache = {}


def render_pdf(file):
    decoded_pdf = base64.b64encode(file.read()).decode("utf-8")
    return decoded_pdf

def render_doc(file):
    decoded_doc = StringIO(file.getvalue().decode("utf-8"))
    return decoded_doc.read()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

## Doc uploader section 
with st.sidebar:
    st.button("Clear Chat", on_click=reset_chat_state)
    
    st.header(f"Add your documents!")  
    # doc_purpose = st.selectbox(
    #     "Mode?",
    #     ("Product Review", "Country Review"),
    # )
    
    uploaded_file = st.file_uploader("Upload file", ['pdf', 'txt', "doc"])
    # Create a unique key for the file to manage state

  
    if uploaded_file:
        file_key = f"{session_id}-{uploaded_file.name}"
        if file_key not in st.session_state.document_cache:
            st.session_state.document_cache[file_key] = True
            if str(uploaded_file.name).endswith(".pdf"):
                st.session_state.file_data = render_pdf(uploaded_file)
            if str(uploaded_file.name).endswith(".doc") or str(uploaded_file.name).endswith(".txt"):
                st.session_state.file_data = render_doc(uploaded_file)



# Main chat interface layout

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt}) 
    if st.session_state.file_data:
        st.session_state.messages.append({"role": "user", "content": f"You are also given the following data to answer: {st.session_state.file_data}"})
        st.session_state.file_data = None
               
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)


    # with st.sidebar:
    #     st.write(st.session_state.messages)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        messages.append(
            {"role": "system", "content": "You are a Barclays risk manager. Given a project proposal, provide a detailed risk assessment based on various principal risks including 1)Regulatory Risk, 2)Market Risk, 3)ESG Risk, 4)Operational Risk, \
            5)Cybersecurity Risk, 6)Political Risk, 7)Credit Risk, 8)Conduct Risk 9) Geopolitical Risk. For country risk, provide commentary on state of corruption, government effectiveness, rule of law, political stability and regulatory quality."})   

        api_response = get_response(messages, stream=True)
        response = st.write_stream(api_response)

    st.session_state.messages.append({"role": "assistant", "content": response})
