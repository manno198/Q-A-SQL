import streamlit as st
import mysql.connector
import urllib.parse
import os



# Remove proxy-related environment variables to avoid conflicts
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities.sql_database import SQLDatabase

from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq


print(f"GROQ_API_KEY: {os.getenv('GROQ_API_KEY')}")
print(f"Environment variables: {os.environ}")
# Load environment variables
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"Found .env file at: {dotenv_path}")
else:
    load_dotenv()
    print("Using default .env loading")

# Debugging: Show current working directory and API key status
print(f"Current working directory: {os.getcwd()}")
print(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")
if os.getenv('GROQ_API_KEY'):
    print(f"GROQ_API_KEY starts with: {os.getenv('GROQ_API_KEY')[:10]}...")


def connect_database(hostname: str, port: str, username: str, password: str, database: str) -> SQLDatabase:
    """
    Establishes connection with MySQL database and returns SQLDatabase object
    """
    try:
        hostname = str(hostname).strip()
        port = str(port).strip()
        username = str(username).strip()
        password = str(password).strip()
        database = str(database).strip()

        port_int = int(port)

        # Test raw MySQL connection first
        test_conn = mysql.connector.connect(
            host=hostname,
            port=port_int,
            user=username,
            password=password,
            database=database,
            auth_plugin='mysql_native_password',  # Force compatibility
            connection_timeout=10
        )
        test_conn.close()

        encoded_password = urllib.parse.quote_plus(password)
        db_uri = f"mysql+mysqlconnector://{username}:{encoded_password}@{hostname}:{port}/{database}"
        return SQLDatabase.from_uri(db_uri)

    except ValueError as e:
        raise ValueError(f"Invalid input: {e}")
    except mysql.connector.Error as e:
        raise mysql.connector.Error(f"MySQL error: {e}")
    except Exception as e:
        raise Exception(f"Connection failed: {e}")


def get_sql_chain(db):
    prompt_template = """
        You are a senior data analyst. 
        Based on the table schema provided below, write a SQL query that answers the question. 
        Consider the conversation history.
        <SCHEMA>{schema}</SCHEMA>
        Conversation History: {conversation_history}
        Write only the SQL query without any additional text.
        Question: {question}
        SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template=prompt_template)

    try:
        llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
    except TypeError as e:
        if "unexpected keyword argument 'proxies'" in str(e):
            env = os.environ.copy()
            env.pop('http_proxy', None)
            env.pop('https_proxy', None)

            llm = ChatGroq(
                model="llama3-8b-8192",
                temperature=0,
                api_key=os.getenv("GROQ_API_KEY"),
                _env=env
            )
        else:
            raise

    def get_schema(_):
        return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )


def get_response(user_query: str, db: SQLDatabase, conversation_history: list):
    sql_chain = get_sql_chain(db)

    prompt_template = """
        You are a senior data analyst. 
        Given the database schema, question, SQL query, and SQL response, 
        write a natural language response.
        <SCHEMA>{schema}</SCHEMA>
        Conversation History: {conversation_history}
        Question: {question}
        SQL Query: {sql_query}
        SQL Response: {response}
        Provide a clear, natural language answer based on the SQL results.
    """
    prompt = ChatPromptTemplate.from_template(template=prompt_template)

    try:
        llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    except TypeError as e:
        if "unexpected keyword argument 'proxies'" in str(e):
            env = os.environ.copy()
            env.pop('http_proxy', None)
            env.pop('https_proxy', None)

            llm = ChatGroq(
                model="llama3-8b-8192",
                temperature=0,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                _env=env
            )
        else:
            raise

    chain = (
        RunnablePassthrough.assign(sql_query=sql_chain).assign(
            schema=lambda _: db.get_table_info(),
            response=lambda vars: db.run(vars["sql_query"])
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke({
        "question": user_query,
        "conversation_history": conversation_history
    })


# Session state initialization
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        AIMessage(content="Hello! I am a SQL assistant. Ask me questions about your MySQL database.")
    ]
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False
if "db" not in st.session_state:
    st.session_state.db = None


# Streamlit UI Setup
st.set_page_config(page_title="SQL Chat", page_icon="💬")
st.title("Q/A SQL 🗨️")


# Sidebar - Configuration & Connection Form
with st.sidebar:
    st.subheader("🔑 API Configuration")
    
    current_key = os.getenv("GROQ_API_KEY")
    if current_key:
        st.success(f"✅ GROQ API Key loaded from .env: {current_key[:10]}...")
    else:
        st.warning("⚠️ GROQ API Key not found in .env file")

    manual_key = st.text_input(
        "GROQ API Key (Manual Entry)", 
        type="password", 
        help="Enter your GROQ API key if .env file is not working",
        placeholder="gsk_..."
    )
    if manual_key:
        os.environ["GROQ_API_KEY"] = manual_key
        st.success("✅ Manual API Key set!")

    final_key = os.getenv("GROQ_API_KEY")
    if not final_key:
        st.error("❌ No GROQ API Key available!")
        st.info("""
        **Solutions:**
        1. Check your .env file contains: `GROQ_API_KEY=your_api_key_here`
        2. Or enter the key manually above
        3. Restart the app after fixing .env file
        """)

    st.divider()

    with st.form("connection_form"):
        hostname = st.text_input("Hostname", value="localhost")
        port = st.text_input("Port", value="3306")
        username = st.text_input("Username", value="root")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database Name")
        connect_button = st.form_submit_button("🔌 Connect")

    if connect_button:
        if not all([hostname, port, username, password, database]):
            st.error("❌ Please fill in all fields!")
        else:
            with st.spinner("Connecting..."):
                try:
                    st.info(f"Connecting to: {username}@{hostname}:{port}/{database}")
                    db = connect_database(hostname, port, username, password, database)
                    st.session_state.db = db
                    st.session_state.db_connected = True
                    st.success("✅ Connected successfully!")

                    tables = db.get_usable_table_names()
                    if tables:
                        st.success(f"📋 Tables found: {', '.join(tables)}")
                    else:
                        st.warning("⚠️ No tables found")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
                    st.session_state.db_connected = False

    if st.session_state.db_connected:
        st.success("🟢 Connected")
        if st.button("🔌 Disconnect"):
            st.session_state.db_connected = False
            st.session_state.db = None
            st.rerun()
    else:
        st.error("🔴 Not Connected")

    if st.button("🔄 Reset App"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# Main Chat Interface
if not st.session_state.db_connected:
    st.info("👈 Please connect to your MySQL database using the sidebar first!")
    st.markdown("""
    ### 📋 Setup Instructions:
    1. **Start MySQL Server**: Make sure your MySQL server is running
    2. **Fill Connection Details**: Enter your database credentials in the sidebar
    3. **Test Connection**: Click 'Connect' to establish connection
    4. **Start Chatting**: Once connected, you can ask questions about your data
    
    ### 🔧 Troubleshooting:
    - Ensure MySQL server is running on the specified port
    - Verify database name exists and is accessible
    - Check username/password are correct
    - Try connecting with MySQL Workbench or command line first
    """)
else:
    for message in st.session_state.conversation_history:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)

    if user_query := st.chat_input("Ask a question about your database..."):
        st.session_state.conversation_history.append(HumanMessage(content=user_query))
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Analyzing your database..."):
                    response = get_response(user_query, st.session_state.db, st.session_state.conversation_history)
                st.markdown(response)
                st.session_state.conversation_history.append(AIMessage(content=response))
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.conversation_history.append(AIMessage(content=error_msg))