import asyncio
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from agents.mcp.server import MCPServerStdio, MCPServerStdioParams
from agents import Agent, Runner, gen_trace_id, trace
import argparse

# Load environment variables
load_dotenv()

# Configure logging to write to a file
log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, 'gmail_cli.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.NullHandler()  # This prevents logs from being printed to console
    ]
)
logger = logging.getLogger("gmail-cli")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default service account file location
DEFAULT_SERVICE_ACCOUNT_FILE = "/var/secrets/google/calServiceAccount.json"

def get_service_account_email():
    return "murali.velamati@tilda.bio"

class GmailCLI:
    def __init__(self, service_account_file):
        self.service_account_email = get_service_account_email()
        self.service_account_file = service_account_file
        self.server = None
        self.agent = None

    async def initialize(self):
        """Initialize the Gmail MCP server and create agent."""
        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(
                f"Service account file not found at {self.service_account_file}. "
                "Please provide a valid service account file using --service-account-file"
            )

        params = MCPServerStdioParams(
            command="uv",
            args=[
                "run",
                "mcp-gsuite",
                "--service-account-file", self.service_account_file,
                "--impersonate", self.service_account_email
            ]
        )
        
        self.server = MCPServerStdio(
            params=params,
            cache_tools_list=True,
            name="Gmail MCP Server"
        )
        
        await self.server.connect()
        
        # Create agent with MCP server
        self.agent = Agent(
            name="Gmail Assistant",
            instructions=f"""You are an AI assistant with access to Gmail tools. 
            Use these tools to help with email-related tasks.
            Note: All operations will be performed on behalf of {self.service_account_email}.""",
            mcp_servers=[self.server]
        )

    async def process_user_input(self, user_input):
        """Process user input and get response from agent."""
        try:
            trace_id = gen_trace_id()
            with trace(workflow_name="Gmail CLI", trace_id=trace_id):
                print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
                result = await Runner.run(starting_agent=self.agent, input=user_input)
                return result.final_output
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return f"Error: {str(e)}"

    async def cleanup(self):
        """Clean up resources."""
        if self.server:
            await self.server.cleanup()

async def main():
    parser = argparse.ArgumentParser(description='Gmail CLI with OpenAI Integration')
    parser.add_argument(
        '--service-account-file',
        default=DEFAULT_SERVICE_ACCOUNT_FILE,
        help=f'Path to the service account JSON file (default: {DEFAULT_SERVICE_ACCOUNT_FILE})'
    )
    args = parser.parse_args()

    cli = GmailCLI(args.service_account_file)
    
    try:
        await cli.initialize()
        print("\nWelcome to Gmail CLI! Type 'exit' to quit.")
        print(f"All operations will be performed on behalf of {cli.service_account_email}")
        print("You can ask me to help with your Gmail tasks.\n")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            response = await cli.process_user_input(user_input)
            print("\nAssistant:", response, "\n")
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
    finally:
        await cli.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 