import asyncio
import os
import aiohttp
import tempfile
import logging
from pathlib import Path
from anthropic import AsyncAnthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    TextContent,
    SamplingMessage,
)

from mcp.types import LoggingMessageNotificationParams



# Configure logging for client
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CLIENT] - %(levelname)s - %(message)s'
)
logger = logging.getLogger('client')

# Load API key and model from config file
config_path = Path.home() / "anandharidas" / "anthropic-config"
api_key = None
model = "claude-sonnet-4-0"  # default fallback

logger.info(f"Loading config from: {config_path}")
if config_path.exists():
    logger.info("Config file found, reading configuration...")
    config_content = config_path.read_text().strip()
    lines = config_content.split('\n')
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            if key == 'api_key':
                api_key = value
                logger.info("API key loaded from config")
            elif key == 'model':
                model = value
                logger.info(f"Model loaded from config: {model}")
else:
    logger.warning("Config file not found, using defaults")

logger.info(f"Initializing Anthropic client with model: {model}")
anthropic_client = AsyncAnthropic(api_key=api_key)


server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)


async def logging_callback(params: LoggingMessageNotificationParams):
    print(params.data)


async def print_progress_callback(
    progress: float, total: float | None, message: str | None
):
    if total is not None:
        percentage = (progress / total) * 100
        print(f"Progress: {progress}/{total} ({percentage:.1f}%)")
    else:
        print(f"Progress: {progress}")
        
async def download_and_extract_content(url: str) -> str:
    """Download and extract text content from PDF or TXT files."""
    logger.info(f"Starting download from URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            logger.info("Making HTTP request...")
            async with session.get(url) as response:
                logger.info(f"HTTP response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Error: Could not download file. HTTP {response.status}"
                    logger.error(error_msg)
                    return error_msg
                
                content_type = response.headers.get('content-type', '').lower()
                logger.info(f"Content-Type detected: {content_type}")
                content = await response.read()
                logger.info(f"Downloaded {len(content)} bytes")
                
                # Handle TXT files
                if 'text/plain' in content_type or url.lower().endswith('.txt'):
                    logger.info("Processing as TXT file")
                    text_content = content.decode('utf-8', errors='ignore')
                    logger.info(f"Extracted {len(text_content)} characters from TXT")
                    return text_content
                
                # Handle PDF files
                elif 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                    logger.info("Processing as PDF file")
                    try:
                        import PyPDF2
                        import io
                        
                        pdf_file = io.BytesIO(content)
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        text = ""
                        
                        logger.info(f"PDF has {len(pdf_reader.pages)} pages")
                        for i, page in enumerate(pdf_reader.pages):
                            page_text = page.extract_text()
                            text += page_text + "\n"
                            logger.info(f"Extracted text from page {i+1}: {len(page_text)} characters")
                        
                        result = text.strip()
                        logger.info(f"Total extracted text: {len(result)} characters")
                        return result
                    except ImportError:
                        error_msg = "Error: PyPDF2 is required to process PDF files. Please install it with: pip install PyPDF2"
                        logger.error(error_msg)
                        return error_msg
                    except Exception as e:
                        error_msg = f"Error processing PDF: {str(e)}"
                        logger.error(error_msg)
                        return error_msg
                
                else:
                    error_msg = f"Error: Unsupported file type. Content-Type: {content_type}"
                    logger.error(error_msg)
                    return error_msg
                    
    except Exception as e:
        error_msg = f"Error downloading file: {str(e)}"
        logger.error(error_msg)
        return error_msg

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)


async def chat(input_messages: list[SamplingMessage], max_tokens=4000):
    logger.info(f"Starting chat with {len(input_messages)} input messages")
    messages = []
    for i, msg in enumerate(input_messages):
        logger.info(f"Processing message {i+1}: role={msg.role}, content_type={msg.content.type}")
        if msg.role == "user" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "user", "content": content})
            logger.info(f"Added user message: {len(content)} characters")
        elif msg.role == "assistant" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "assistant", "content": content})
            logger.info(f"Added assistant message: {len(content)} characters")

    logger.info(f"Calling Anthropic API with model={model}, max_tokens={max_tokens}")
    response = await anthropic_client.messages.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    logger.info("Received response from Anthropic API")

    text = "".join([p.text for p in response.content if p.type == "text"])
    logger.info(f"Extracted response text: {len(text)} characters")
    return text


async def sampling_callback(
    context: RequestContext, params: CreateMessageRequestParams
):
    logger.info("Sampling callback triggered")
    logger.info(f"Received {len(params.messages)} messages for processing")
    
    # Call Claude using the Anthropic SDK
    logger.info("Calling chat function...")
    text = await chat(params.messages)
    logger.info("Chat function completed")

    result = CreateMessageResult(
        role="assistant",
        model=model,
        content=TextContent(type="text", text=text),
    )
    logger.info(f"Returning result with {len(text)} characters")
    return result


async def run():
    logger.info("Starting MCP client...")
    logger.info(f"Server parameters: {server_params}")
    
    async with stdio_client(server_params) as (read, write):
        logger.info("Stdio client connection established")
        async with ClientSession(
            read, write, sampling_callback=sampling_callback,
            logging_callback=logging_callback
        ) as session:
            logger.info("Client session created, initializing...")
            await session.initialize()
            logger.info("Session initialized successfully")
            
            print("MCP Client is running. Type 'quit' to exit.")
            print("Available actions:")
            print("1. summarize - Summarize a document")
            print("2. printable_summary - Summarize a document and format as markdown")
            print("3. quit - Exit the client")
            print()
            
            await session.call_tool(
                name="add",
                arguments={"a": 1, "b": 3},
                progress_callback=print_progress_callback,
            )

            while True:
                try:
                    action = input("Enter action (summarize/printable_summary/quit): ").strip().lower()
                    logger.info(f"User selected action: {action}")
                    
                    if action == "quit":
                        logger.info("User requested quit, exiting...")
                        print("Goodbye!")
                        break
                    elif action == "summarize":
                        document_link = input("Enter the HTTP link to the PDF or TXT file you want to summarize: ")
                        logger.info(f"User provided document link: {document_link}")
                        
                        print("Downloading and extracting content...")
                        file_content = await download_and_extract_content(document_link)
                        
                        if file_content.startswith("Error:"):
                            logger.error(f"Download/extraction failed: {file_content}")
                            print(f"Error: {file_content}")
                            continue
                        
                        print(f"Content extracted ({len(file_content)} characters). Summarizing...")
                        logger.info(f"Calling summarize tool with {len(file_content)} characters")
                        
                        result = await session.call_tool(
                            name="summarize",
                            arguments={"text_to_summarize": file_content},
                        )
                        logger.info("Summarize tool completed successfully")
                        
                        # Extract the actual text content from the result
                        summary_text = result.content
                        if hasattr(summary_text, 'text'):
                            summary_text = summary_text.text
                        elif isinstance(summary_text, list) and len(summary_text) > 0:
                            summary_text = summary_text[0].text if hasattr(summary_text[0], 'text') else str(summary_text[0])
                        else:
                            summary_text = str(summary_text)
                        
                        print(f"\nSummary:\n{summary_text}\n")
                    elif action == "printable_summary":
                        document_link = input("Enter the HTTP link to the PDF or TXT file you want to summarize and format: ")
                        logger.info(f"User provided document link: {document_link}")
                        
                        print("Downloading and extracting content...")
                        file_content = await download_and_extract_content(document_link)
                        
                        if file_content.startswith("Error:"):
                            logger.error(f"Download/extraction failed: {file_content}")
                            print(f"Error: {file_content}")
                            continue
                        
                        print(f"Content extracted ({len(file_content)} characters). Summarizing...")
                        logger.info(f"Calling summarize tool with {len(file_content)} characters")
                        
                        # First, get the summary
                        summary_result = await session.call_tool(
                            name="summarize",
                            arguments={"text_to_summarize": file_content},
                        )
                        logger.info("Summarize tool completed successfully")
                        
                        # Extract the actual text content from the result
                        summary_text = summary_result.content
                        if hasattr(summary_text, 'text'):
                            summary_text = summary_text.text
                        elif isinstance(summary_text, list) and len(summary_text) > 0:
                            summary_text = summary_text[0].text if hasattr(summary_text[0], 'text') else str(summary_text[0])
                        else:
                            summary_text = str(summary_text)
                        
                        print(f"Summary generated ({len(summary_text)} characters). Formatting as markdown...")
                        logger.info(f"Calling format_to_markdown tool with {len(summary_text)} characters")
                        
                        # Then, format it as markdown
                        markdown_result = await session.call_tool(
                            name="format_to_markdown",
                            arguments={"summary_text": summary_text},
                        )
                        logger.info("Format to markdown tool completed successfully")
                        
                        # Extract the actual text content from the markdown result
                        markdown_text = markdown_result.content
                        if hasattr(markdown_text, 'text'):
                            markdown_text = markdown_text.text
                        elif isinstance(markdown_text, list) and len(markdown_text) > 0:
                            markdown_text = markdown_text[0].text if hasattr(markdown_text[0], 'text') else str(markdown_text[0])
                        else:
                            markdown_text = str(markdown_text)
                        
                        print(f"\nMarkdown Formatted Summary:\n{markdown_text}\n")
                    else:
                        logger.warning(f"Unknown action: {action}")
                        print("Unknown action. Please enter 'summarize', 'printable_summary', or 'quit'.")
                        
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received, exiting...")
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    print(f"Error: {e}")
                    print("Please try again.")


if __name__ == "__main__":
    import asyncio
    
    logger.info("Starting client application")
    try:
        asyncio.run(run())
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        raise
    logger.info("Client application finished")
