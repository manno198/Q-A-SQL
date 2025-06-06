# SQL Chat 💬

A powerful and intuitive chat interface for querying MySQL databases using natural language. Built with Streamlit, LangChain, and ChatGroq, this application allows you to interact with your MySQL database through conversational queries.

## 🌟 Features

- 🤖 **AI-Powered SQL Generation**: Automatically converts natural language questions into SQL queries
- 💬 **Conversational Interface**: Chat-based interaction with context-aware responses
- 🔌 **Easy Database Connection**: Simple MySQL connection setup through a user-friendly interface
- 🔐 **Secure Credentials**: Password-protected database connection with environment variable support
- 📊 **Real-time Results**: Instant query execution and natural language responses
- 🔄 **Conversation History**: Maintains context of your chat history for better query understanding
- 🛠️ **Error Handling**: Robust error handling and user-friendly error messages
- 🔑 **API Key Management**: Support for both .env file and manual GROQ API key entry

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server
- GROQ API Key (Get one from [Groq Console](https://console.groq.com/))

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sql-chat.git
cd sql-chat
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your GROQ API key:
```
GROQ_API_KEY=your_api_key_here
```

## ⚙️ Configuration

1. Start your MySQL server
2. Launch the application:
```bash
streamlit run app.py
```
3. In the sidebar:
   - Enter your GROQ API key (if not in .env file)
   - Fill in your MySQL connection details:
     - Hostname (default: localhost)
     - Port (default: 3306)
     - Username
     - Password
     - Database Name
4. Click "Connect" to establish the database connection

## 💡 Usage

1. Once connected, you can start asking questions about your database in natural language
2. The AI will:
   - Convert your question to SQL
   - Execute the query
   - Provide a natural language response with the results
3. The conversation history is maintained for context
4. Use the sidebar to:
   - Monitor connection status
   - Disconnect from the database
   - Reset the application
   - View available tables

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) - Web application framework
- [LangChain](https://www.langchain.com/) - Framework for LLM applications
- [ChatGroq](https://console.groq.com/) - LLM API for natural language processing
- [MySQL Connector](https://dev.mysql.com/doc/connector-python/en/) - MySQL database connection
- [Python-dotenv](https://pypi.org/project/python-dotenv/) - Environment variable management

## ⚠️ Troubleshooting

- **Connection Issues**:
  - Verify MySQL server is running
  - Check database credentials
  - Ensure database exists and is accessible
  - Try connecting with MySQL Workbench first

- **API Key Issues**:
  - Verify GROQ API key is valid
  - Check .env file location and format
  - Try manual key entry in the sidebar

- **Query Issues**:
  - Ensure your question is clear and specific
  - Check if the required tables exist
  - Verify you have necessary permissions

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.