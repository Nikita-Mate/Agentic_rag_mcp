# mcp.py
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
class MCPMessage:
    def __init__(self, sender: str, receiver: str, msg_type: str, payload: Dict[str, Any], trace_id: Optional[str] = None):
        try:
            if not isinstance(sender, str) or not sender.strip():
                raise ValueError("sender must be a non-empty string")            
            if not isinstance(receiver, str) or not receiver.strip():
                raise ValueError("receiver must be a non-empty string")            
            if not isinstance(msg_type, str) or not msg_type.strip():
                raise ValueError("msg_type must be a non-empty string")            
            if not isinstance(payload, dict):
                raise ValueError("payload must be a dictionary")            
            self.message = {
                "sender": sender.strip(),
                "receiver": receiver.strip(),
                "type": msg_type.strip(),
                "trace_id": trace_id or str(uuid.uuid4()),
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }            
            self.sender = self.message["sender"]
            self.receiver = self.message["receiver"]
            self.msg_type = self.message["type"]
            self.trace_id = self.message["trace_id"]
            self.payload = self.message["payload"]
            self.timestamp = self.message["timestamp"]            
            print(f"MCPMessage created successfully: {self.sender} -> {self.receiver} [{self.msg_type}]")
        except Exception as e:
            print(f"Error creating MCPMessage: {str(e)}")
            self.message = {
                "sender": "SYSTEM",
                "receiver": "ERROR_HANDLER",
                "type": "CREATION_ERROR",
                "trace_id": str(uuid.uuid4()),
                "payload": {"error": str(e), "original_params": locals()},
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.sender = self.message["sender"]
            self.receiver = self.message["receiver"]
            self.msg_type = self.message["type"]
            self.trace_id = self.message["trace_id"]
            self.payload = self.message["payload"]
            self.timestamp = self.message["timestamp"]    
    def to_dict(self) -> Dict[str, Any]:
        try:
            print(f"Converting MCPMessage to dict: {self.msg_type}")
            return self.message.copy()  
        except Exception as e:
            print(f"Error converting MCPMessage to dict: {str(e)}")
            return {
                "sender": "SYSTEM",
                "receiver": "ERROR_HANDLER",
                "type": "CONVERSION_ERROR",
                "trace_id": str(uuid.uuid4()),
                "payload": {"error": str(e)},
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    def is_valid(self) -> bool:
        try:
            required_fields = ["sender", "receiver", "type", "trace_id", "payload", "timestamp"]
            return all(field in self.message for field in required_fields)
        except:
            return False    
    def is_error_message(self) -> bool:
        return self.msg_type in ["ERROR", "CREATION_ERROR", "CONVERSION_ERROR"]    
    def get_summary(self) -> str:
        try:
            payload_size = len(str(self.payload))
            return f"{self.sender} -> {self.receiver} [{self.msg_type}] (payload: {payload_size} chars, trace: {self.trace_id[:8]}...)"
        except:
            return f"Invalid message: {self.message}"    
    def add_metadata(self, key: str, value: Any) -> None:
        try:
            if "metadata" not in self.payload:
                self.payload["metadata"] = {}
            self.payload["metadata"][key] = value
            print(f"Added metadata {key} to message")
        except Exception as e:
            print(f"Error adding metadata: {str(e)}")    
    def __str__(self) -> str:
        return self.get_summary()    
    def __repr__(self) -> str:
        return f"MCPMessage({self.get_summary()})"    
    @classmethod
    def create_error_message(cls, error: Exception, sender: str = "SYSTEM", receiver: str = "ERROR_HANDLER", trace_id: Optional[str] = None):
        return cls(
            sender=sender,
            receiver=receiver,
            msg_type="ERROR",
            payload={
                "error": str(error),
                "error_type": type(error).__name__,
                "severity": "ERROR"
            },
            trace_id=trace_id
        )    
    @classmethod
    def create_success_message(cls, sender: str, receiver: str, data: Dict[str, Any], trace_id: Optional[str] = None):
        return cls(
            sender=sender,
            receiver=receiver,
            msg_type="SUCCESS",
            payload={
                "status": "success",
                "data": data
            },
            trace_id=trace_id
        )