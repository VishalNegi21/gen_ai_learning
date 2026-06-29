from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit 
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st


db = SQLDatabase.from_uri("sqlite:///apps/my_tasks.db")

db.run("""
    CREATE TABLE IF NOT EXISTS tasks(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       description TEXT,
       status TEXT CHECK( status IN ('pending','in_progress','completed')) DEFAULT 'pending',
       created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
       );
""")

llm = ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db,llm=llm)
tools = toolkit.get_tools()


system_prompt = """
You are a task manager assistant that interacts with a SQL Database containing a 'tasks' table.

Task Rules:
1. Limit SELECT queries to 10 result max with ORDER BY created_at DESC
2. After every CREATE/UPDATE/DELETE , confirm that operation with SELECT query
3. If user requests a list of tasks or any output , present the output in a structured table format to ensure a clean and organized diplay in the browser

CRUD Operations:
    CREATE: INSERT INTO tasks(title , description , status)
    READ : SELECT * FROM tasks WHERE ...... LIMIT 10
    UPDATE: UPDATE tasks SET status = ? WHERE id=? OR title=?
    DELETE : DELETE FROM tasks WHERE id=? OR title=?

Table Schema : id,title,description,status(pending/in_progress/completed),created_at.
"""

@st.cache_resource   # this func will not run again and again so memory will also not refresh
def get_agent():
    agent = create_agent(
        model=llm,
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )
    return agent

agent = get_agent()

st.subheader("TaskManager - Manage your Tasks")

if "messages" not in st.session_state:
    st.session_state.messages=[]

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])


prompt = st.chat_input("Ask me to manage your tasks")

if prompt:    
    st.session_state.messages.append({"role":"user","content":prompt})

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user","content":prompt})

    with st.chat_message("ai"):
        with st.spinner("Processing...."):
            response = agent.invoke(
                {"messages":[{"role":"user","content":prompt}]},
                {"configurable":{"thread_id":"abc"}}
            )
            result = response["messages"][-1].content
            st.markdown(result)
            st.session_state.messages.append({"role":"ai","content":result})

    