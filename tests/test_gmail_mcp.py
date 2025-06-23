import asyncio
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from agents.mcp.server import MCPServerStdio, MCPServerStdioParams
from mcp.types import Tool, TextContent
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-gmail-mcp")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load service account email from .accounts.json
def get_service_account_email():
   return "test@gmail.com"

def serialize_tools(tools):
    """Convert Tool objects to a serializable format."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        }
        for tool in tools
    ]

async def test_gmail_mcp():
    # Get service account email
    service_account_email = get_service_account_email()
    if not service_account_email:
        raise RuntimeError("No service account email found in .accounts.json")
    
    # Start the Gmail MCP server
    params = MCPServerStdioParams(
        command="uv",
        args=[
            "run",
            "mcp-gsuite",
            "--service-account-file", "/var/secrets/google/calServiceAccount.json"
        ]
    )
    
    server = MCPServerStdio(
        params=params,
        cache_tools_list=True,  # Cache tools list for better performance
        name="Gmail MCP Server"  # Give it a friendly name
    )
    
    try:
        await server.connect()
        
        # List available tools
        tools = await server.list_tools()
        serialized_tools = serialize_tools(tools)
        logger.info(f"Available tools: {serialized_tools}")

        # Create a system message that includes the available tools
        system_message = f"""You are an AI assistant with access to Gmail tools. 
        Available tools: {json.dumps(serialized_tools, indent=2)}
        Use these tools to help with email-related tasks."""

        # Example conversation with OpenAI
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Check my latest unread emails and summarize them"}
        ]

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
        )

        # Process the response and use the Gmail tools
        assistant_message = response.choices[0].message.content
        logger.info(f"Assistant response: {assistant_message}")

        # # Test 1: Query unread emails
        # logger.info("Testing query_gmail_emails tool...")
        # result = await server.call_tool(
        #     "query_gmail_emails",
        #     {
        #         "__user_id__": service_account_email,
        #         "query": "is:unread"
        #     }
        # )
        
        # # Parse the result and display the first unread email
        # if result.content and not result.isError:
        #     emails = json.loads(result.content[0].text)
        #     if emails:
        #         first_email = emails[0]
        #         logger.info(f"Found unread email:")
        #         logger.info(f"Subject: {first_email.get('subject', 'No subject')}")
        #         logger.info(f"From: {first_email.get('from', 'Unknown sender')}")
                
        #         # Get the full email content
        #         email_content = await server.call_tool(
        #             "get_gmail_email",
        #             {
        #                 "__user_id__": service_account_email,
        #                 "email_id": first_email["id"]
        #             }
        #         )
        #         if email_content.content and not email_content.isError:
        #             email_data = json.loads(email_content.content[0].text)
        #             logger.info(f"Body:\n{email_data.get('body', 'No body content')}")
        #         else:
        #             logger.error("Failed to get email content")
        #     else:
        #         logger.info("No unread emails found")
        # else:
        #     logger.error("Failed to query unread emails")

        # # Test 2: Send an email
        # logger.info("Testing send_gmail_email tool...")
        # result = await server.call_tool(
        #     "send_gmail_email",
        #     {
        #         "__user_id__": service_account_email,
        #         "to": service_account_email,
        #         "subject": "Test Email from Gmail MCP",
        #         "body": "This is a test email sent using the Gmail MCP service."
        #     }
        # )
        # logger.info(f"Send email result: {result}")
        
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(test_gmail_mcp()) 