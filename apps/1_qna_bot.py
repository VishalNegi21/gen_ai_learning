
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

import streamlit as st
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")

st.title("ASK-ME : GEMINI POWERED QNA BOT")
st.markdown("QNA bot with langchain and Gemini")

if "messages" not in st.session_state:  #messages is a key if it is not there it will make it , all roles and contents are stored inside mesaages key which is a list of dictionries (each role and content are a dictionary)
    st.session_state.messages = []

# we do not want previous question to be erased from screen and continue with new questions below that
for message in st.session_state.messages:
    role= message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

question = st.chat_input("Ask me")
if question:
    #store query in llm
    st.session_state.messages.append({"role":"user" , "content":question})   # session state messages is a list of dictionary so appned dict
    # show question on browser
    st.chat_message("user").markdown(question)
    # ask to llm
    res = llm.invoke(question)
    # show response on browser
    st.chat_message("ai").markdown(res.content)
    # store query
    st.session_state.messages.append({"role":"ai" , "content":res.content})