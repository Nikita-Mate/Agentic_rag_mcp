# app.py
import streamlit as st
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent  # Import your separate agent
from mcp import MCPMessage
from vector_store import VectorStore
import atexit
@st.cache_resource
def initialize_agents():
    try:
        vector_store = VectorStore()
        ingestion_agent = IngestionAgent()
        retrieval_agent = RetrievalAgent(vector_store)
        return vector_store, ingestion_agent, retrieval_agent
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        st.stop()
@st.cache_resource
def get_llm_agent():
    return LLMResponseAgent()
def cleanup_vector_store():
    if 'vector_store' in st.session_state:
        st.session_state.vector_store.clear()
try:
    st.title("🕵️ Agent-based RAG Chatbot")    
    with st.spinner("Loading model... This may take a few minutes on first run."):
        llm_agent = get_llm_agent()
    if not llm_agent:
        st.error("Failed to load the model. Please check your internet connection and try again.")
        st.stop()
    else:
        st.success("✅ Model loaded successfully!")
    vector_store, ingestion_agent, retrieval_agent = initialize_agents()
    atexit.register(cleanup_vector_store)    
    st.header("📄 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload your documents",
        type=["pdf", "docx", "pptx", "csv", "txt", "md"],
        accept_multiple_files=True,
        help="Upload documents to create a knowledge base for Q&A"
    )        
    if uploaded_files:
        try:
            with st.spinner("Processing documents..."):
                total_chunks = 0
                for file in uploaded_files:
                    chunks = ingestion_agent.process_document(file)
                    vector_store.add_documents(chunks)
                    total_chunks += len(chunks)
                print("Document ingestion completed")            
            st.success(f"✅ {len(uploaded_files)} document(s) processed successfully! Created {total_chunks} text chunks.")
            if hasattr(vector_store, 'get_stats'):
                stats = vector_store.get_stats()
                st.sidebar.success(f"📊 Vector Store: {stats['total_documents']} documents indexed")
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")    
    st.header("💬 Chat with your documents")
    query = st.text_input("Ask a question about your documents:", placeholder="e.g., What is the main topic of the document?")
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("Submit", type="primary")
    with col2:
        if st.button("Clear Chat"):
            st.rerun()   
    if submit_button and query:
        if vector_store.get_stats()['total_documents'] == 0:
            st.warning("⚠️ Please upload some documents first!")
        else:
            try:
                with st.spinner("🔍 Searching documents and generating response..."):
                    mcp_query = MCPMessage(
                        sender="UI",
                        receiver="RetrievalAgent",
                        msg_type="QUERY",
                        payload={"query": query}
                    ).to_dict()
                    mcp_retrieval = retrieval_agent.handle_query(mcp_query).to_dict()
                    mcp_response = llm_agent.generate_response(mcp_retrieval).to_dict()
                st.subheader("🔍 Answer")
                if mcp_response["type"] == "ERROR":
                    st.error(f"Error: {mcp_response['payload']['answer']}")
                else:
                    st.write(mcp_response["payload"]["answer"])                    
                    if mcp_response["payload"].get("source_context"):
                        with st.expander("📚 Source Context"):
                            st.text(mcp_response["payload"]["source_context"])                    
                    if mcp_retrieval.get("payload", {}).get("retrieved_context"):
                        retrieved_docs = mcp_retrieval["payload"]["retrieved_context"]
                        with st.expander(f"📖 Retrieved Documents ({len(retrieved_docs)} found)"):
                            for i, doc in enumerate(retrieved_docs):
                                st.write(f"**Document {i+1}:**")
                                st.write(doc)
                                st.write("---")   
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.error("Please try again or check your model configuration.")
except Exception as e:
    print(f"App error: {str(e)}")
    st.error(f"App error: {str(e)}")
    st.error("Please refresh the page and try again.")