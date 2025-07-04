# llm_response_agent_openai.py
import openai
from mcp import MCPMessage
class LLMResponseAgent:
    def __init__(self):
        self.model_name = "gpt-3.5-turbo"
        openai.api_key = ""
        print("OpenAI LLMResponseAgent initialized successfully")
    def generate_response(self, mcp_msg):
        try:
            retrieved_context = mcp_msg["payload"]["retrieved_context"]
            context = "\n\n".join(retrieved_context)
            query = mcp_msg["payload"]["query"]
            prompt = f"""You are a helpful assistant. Answer the user's question based on the context below.
            Context:
            {context}
            Question:
            {query}
            Answer:"""
            print("Sending prompt to OpenAI API")
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            answer = response.choices[0].message.content.strip()
            print("Response received from OpenAI API")
            return MCPMessage(
                sender="LLMResponseAgent",
                receiver="UI",
                msg_type="FINAL_RESPONSE",
                payload={
                    "answer": answer,
                    "source_context": context
                },
                trace_id=mcp_msg.get("trace_id")
            )
        except Exception as e:
            print(f"Response generation error: {str(e)}")
            return MCPMessage(
                sender="LLMResponseAgent",
                receiver="UI",
                msg_type="ERROR",
                payload={
                    "answer": f"Error generating response: {str(e)}",
                    "source_context": ""
                },
                trace_id=mcp_msg.get("trace_id")
            )
