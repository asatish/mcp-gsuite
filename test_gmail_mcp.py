import logging
from mcp_gsuite.gmail_mcp import GmailMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gmail_mcp():
    # Initialize Gmail MCP with service account
    service_account_file = "/var/secrets/google/calServiceAccount.json"
    delegated_user = "murali.velamati@tilda.bio"
    
    try:
        # Initialize Gmail MCP
        gmail_mcp = GmailMCP(service_account_file, delegated_user)
        logger.info("Successfully initialized Gmail MCP")
        
        # Test sending an email
        test_email = {
            "to": "murali.velamati@tilda.bio",
            "subject": "Test Email from Gmail MCP",
            "body": "This is a test email sent using the Gmail MCP tool."
        }
        
        logger.info("Sending test email...")
        result = gmail_mcp.send_email(test_email)
        logger.info(f"Email sent successfully: {result}")
        
        # Test reading unread messages
        logger.info("Reading unread messages...")
        unread_messages = gmail_mcp.read_unread_messages()
        logger.info(f"Found {len(unread_messages)} unread messages")
        
        # Test marking messages as read
        if unread_messages:
            logger.info("Marking messages as read...")
            for message in unread_messages:
                gmail_mcp.mark_as_read(message["id"])
            logger.info("Successfully marked messages as read")
        
    except Exception as e:
        logger.error(f"Error testing Gmail MCP: {str(e)}")
        raise

if __name__ == "__main__":
    test_gmail_mcp() 