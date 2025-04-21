import streamlit as st
from mcp import MCP

# Page configuration
st.set_page_config(
    page_title="Multi-Context Processing (MCP) Demo",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "mcp" not in st.session_state:
    st.session_state.mcp = MCP()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title and description
st.title("🔍 Multi-Context Processing (MCP) Demo")
st.markdown("""
This demo showcases a Multi-Context Processing system that uses multiple search tools:
- **Tavily**: For general web searches
- **FireCrawl**: For real-time and recent information
- **Exa**: For technical and programming-related searches

Ask any question, and the system will use the most appropriate search tool to find the answer!
""")

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching and processing..."):
            response = st.session_state.mcp.process_query(prompt)
            if response["status"] == "success":
                st.markdown(response["response"])
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            else:
                st.error(f"Error: {response['error']}")

# Sidebar
with st.sidebar:
    st.header("Options")
    
    # Save conversation
    if st.button("Save Conversation"):
        st.session_state.mcp.save_conversation()
        st.success("Conversation saved to conversation_history.json!")
    
    # Clear chat
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.mcp = MCP()
        st.rerun() 