import json
import logging
from typing import Dict, Any, Optional, List
from mcp_gsuite.gmail_mcp import GmailMCP

logger = logging.getLogger(__name__)

class GmailMCPWrapper:
    def __init__(self, service_account_file: str, delegated_user: str):
        """Initialize the Gmail MCP wrapper.
        
        Args:
            service_account_file: Path to the service account JSON file
            delegated_user: Email address of the delegated user
        """
        self.gmail_mcp = GmailMCP(service_account_file, delegated_user)
        
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a Gmail MCP action.
        
        Args:
            action: The action to perform
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict containing the result of the action
        """
        try:
            if action == "send_email":
                email_data = kwargs.get("email_data")
                if not email_data:
                    raise ValueError("email_data is required for send_email action")
                
                self.gmail_mcp.send_email(
                    to=email_data["to"],
                    subject=email_data["subject"],
                    body=email_data["body"]
                )
                return {"status": "success", "message": "Email sent successfully"}
                
            elif action == "read_unread_messages":
                messages = self.gmail_mcp.read_unread_messages()
                return {
                    "status": "success",
                    "messages": [
                        {
                            "id": msg["id"],
                            "subject": msg.get("subject", ""),
                            "from": msg.get("from", ""),
                            "snippet": msg.get("snippet", "")
                        }
                        for msg in messages
                    ]
                }
                
            elif action == "mark_as_read":
                message_id = kwargs.get("message_id")
                if not message_id:
                    raise ValueError("message_id is required for mark_as_read action")
                
                self.gmail_mcp.mark_as_read(message_id)
                return {"status": "success", "message": "Message marked as read"}
                
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing Gmail MCP action: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    @classmethod
    def get_tool_definition(cls) -> Dict[str, Any]:
        """Get the tool definition for OpenAI LLM integration."""
        with open("gmail_mcp_tool.json", "r") as f:
            return json.load(f) 