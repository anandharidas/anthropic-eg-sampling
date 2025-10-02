import logging
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
import asyncio

# Configure logging for server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SERVER] - %(levelname)s - %(message)s'
)
logger = logging.getLogger('server')

logger.info("Initializing MCP server...")
mcp = FastMCP(name="Demo Server")
logger.info("MCP server created successfully")


@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):
    logger.info("Summarize tool called")
    logger.info(f"Input text length: {len(text_to_summarize)} characters")
    logger.info(f"Input text preview: {text_to_summarize[:200]}...")
    
    prompt = f"""
        Please summarize the following text:
        {text_to_summarize}
    """
    logger.info(f"Created prompt with {len(prompt)} characters")

    logger.info("Calling create_message...")
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user", content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=4000,
        system_prompt="You are a helpful research assistant.",
    )
    logger.info("create_message completed")

    if result.content.type == "text":
        summary_text = result.content.text
        logger.info(f"Summary generated: {len(summary_text)} characters")
        logger.info(f"Summary preview: {summary_text[:200]}...")
        return summary_text
    else:
        logger.error(f"Sampling failed - unexpected content type: {result.content.type}")
        raise ValueError("Sampling failed")


@mcp.tool()
async def format_to_markdown(summary_text: str, ctx: Context):
    logger.info("Format to markdown tool called")
    logger.info(f"Input summary length: {len(summary_text)} characters")
    logger.info(f"Input summary preview: {summary_text[:200]}...")
    
    prompt = f"""
        Please convert the following summary into a well-formatted markdown document with proper headings, bullet points, and structure:
        
        {summary_text}
        
        Use appropriate markdown formatting including:
        - Headers (# ## ###)
        - Bullet points and numbered lists
        - Bold and italic text where appropriate
        - Code blocks if there are any technical terms
        - Tables if the content warrants it
        - Proper line breaks and spacing
    """
    logger.info(f"Created markdown formatting prompt with {len(prompt)} characters")

    logger.info("Calling create_message for markdown formatting...")
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user", content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=4000,
        system_prompt="You are a helpful assistant that specializes in formatting text into clean, readable markdown documents.",
    )
    logger.info("Markdown formatting create_message completed")

    if result.content.type == "text":
        markdown_text = result.content.text
        logger.info(f"Markdown formatted: {len(markdown_text)} characters")
        logger.info(f"Markdown preview: {markdown_text[:200]}...")
        return markdown_text
    else:
        logger.error(f"Markdown formatting failed - unexpected content type: {result.content.type}")
        raise ValueError("Markdown formatting failed")

@mcp.tool()
async def add(a: int, b: int, ctx: Context) -> int:
    await ctx.info("Preparing to add...")
    await ctx.report_progress(20, 100)

    await asyncio.sleep(2)

    await ctx.info("OK, adding...")
    await ctx.report_progress(80, 100)

    return a + b


if __name__ == "__main__":
    logger.info("Starting MCP server with stdio transport")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    logger.info("MCP server finished")
