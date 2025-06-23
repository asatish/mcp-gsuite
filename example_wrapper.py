import os
import logging
from gmail_mcp_wrapper import GmailMCPWrapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize the Gmail MCP wrapper
    service_account_file = "/var/secrets/google/calServiceAccount.json"
    delegated_user = "murali.velamati@tilda.bio"
    
    gmail_wrapper = GmailMCPWrapper(service_account_file, delegated_user)
    
    # Example 1: Send an email
    try:
        email_data = {
            "to": "recipient@example.com",
            "subject": "Test Email",
            "body": "This is a test email sent using the Gmail MCP wrapper."
        }
        result = gmail_wrapper.execute("send_email", email_data=email_data)
        logger.info(f"Send email result: {result}")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
    
    # Example 2: Read unread messages
    try:
        result = gmail_wrapper.execute("read_unread_messages")
        logger.info(f"Read unread messages result: {result}")
        
        # Example 3: Mark a message as read
        if result["status"] == "success" and result["messages"]:
            message_id = result["messages"][0]["id"]
            mark_result = gmail_wrapper.execute("mark_as_read", message_id=message_id)
            logger.info(f"Mark as read result: {mark_result}")
    except Exception as e:
        logger.error(f"Error reading messages: {str(e)}")
    
    # Example 4: Get tool definition
    try:
        tool_definition = GmailMCPWrapper.get_tool_definition()
        logger.info(f"Tool definition: {tool_definition}")
    except Exception as e:
        logger.error(f"Error getting tool definition: {str(e)}")

if __name__ == "__main__":
    main() 