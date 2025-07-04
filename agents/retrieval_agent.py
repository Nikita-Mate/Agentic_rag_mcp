# retrieval_agent.py
from mcp import MCPMessage
class RetrievalAgent:
    def __init__(self, vector_store):
        self.vector_store = vector_store    
    def handle_query(self, mcp_msg):
        query = ""  
        try:
            if not isinstance(mcp_msg, dict):
                raise ValueError("mcp_msg must be a dictionary")            
            if "payload" not in mcp_msg:
                raise ValueError("mcp_msg must contain 'payload' key")            
            if "query" not in mcp_msg["payload"]:
                raise ValueError("payload must contain 'query' key")            
            query = mcp_msg["payload"]["query"]
            if not query or not isinstance(query, str) or not query.strip():
                raise ValueError("Query must be a non-empty string")            
            chunks = self.vector_store.retrieve(query.strip())            
            if chunks and isinstance(chunks[0], dict):
                retrieved_context = [chunk['text'] for chunk in chunks]
                distances = [chunk['distance'] for chunk in chunks]
            else:
                retrieved_context = chunks
                distances = None
            payload = {
                "retrieved_context": retrieved_context,
                "query": query,
                "num_results": len(retrieved_context)
            }
            if distances:
                payload["distances"] = distances            
            return MCPMessage(
                sender="RetrievalAgent",
                receiver="LLMResponseAgent",
                msg_type="RETRIEVAL_RESULT",
                payload=payload,
                trace_id=mcp_msg.get("trace_id")
            )            
        except Exception as e:
            print(f"Retrieval error: {str(e)}")
            error_payload = {
                "retrieved_context": [],
                "query": query,
                "error": str(e),
                "error_type": type(e).__name__
            }            
            return MCPMessage(
                sender="RetrievalAgent",
                receiver="LLMResponseAgent",
                msg_type="ERROR",
                payload=error_payload,
                trace_id=mcp_msg.get("trace_id")
            )    
    def validate_vector_store(self):
        try:
            if not hasattr(self.vector_store, 'retrieve'):
                raise AttributeError("Vector store must have a 'retrieve' method")
            if not hasattr(self.vector_store, 'get_stats'):
                return True
            stats = self.vector_store.get_stats()
            if stats['total_documents'] == 0:
                print("Warning: Vector store is empty")
            else:
                print(f"Vector store contains {stats['total_documents']} documents")            
            return True            
        except Exception as e:
            print(f"Vector store validation error: {str(e)}")
            return False    
    def process_query_with_validation(self, mcp_msg):
        if not self.validate_vector_store():
            return MCPMessage(
                sender="RetrievalAgent",
                receiver="LLMResponseAgent",
                msg_type="ERROR",
                payload={
                    "retrieved_context": [],
                    "query": "",
                    "error": "Vector store validation failed",
                    "error_type": "ValidationError"
                },
                trace_id=mcp_msg.get("trace_id") if isinstance(mcp_msg, dict) else None
            )
        return self.handle_query(mcp_msg)