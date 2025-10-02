# MCP Document Summarization Project

A comprehensive demonstration of the Model Context Protocol (MCP) featuring document processing, AI-powered summarization, and markdown formatting capabilities.

## Table of Contents

- [Overview](#overview)
- [MCP Concepts Explained](#mcp-concepts-explained)
- [Project Architecture](#project-architecture)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Key Functions](#key-functions)
- [Dependencies](#dependencies)
- [Contributing](#contributing)

## Overview

This project demonstrates the Model Context Protocol (MCP) by creating a client-server architecture that can download documents from HTTP URLs, extract text content from PDF and TXT files, summarize them using Anthropic's Claude AI, and format the summaries as well-structured markdown documents.

## MCP Concepts Explained

### What is MCP?

The Model Context Protocol (MCP) is a standardized way for AI applications to communicate with external tools and services. It enables AI models to:

- **Call Tools**: Execute specific functions with defined parameters
- **Access Resources**: Read from various data sources
- **Process Prompts**: Handle structured input/output for AI interactions
- **Maintain Context**: Keep conversation state across multiple interactions

### Core MCP Components

#### 1. **Tools**
Tools are functions that the AI can call to perform specific tasks. In this project:
- `summarize`: Extracts key information from text documents
- `format_to_markdown`: Converts plain text summaries into structured markdown

#### 2. **Resources**
Resources represent data sources that can be accessed by the AI. While not directly used in this project, MCP supports:
- File systems
- Databases
- APIs
- Web content

#### 3. **Prompts**
Prompts are structured templates for AI interactions. Our project uses:
- Summarization prompts for extracting key information
- Formatting prompts for markdown conversion
- System prompts for defining AI behavior

#### 4. **Sampling**
Sampling refers to the process of generating AI responses. Our implementation:
- Uses Anthropic's Claude for text generation
- Implements proper error handling and logging
- Manages conversation context

## Project Architecture

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│   Client.py     │◄──────────────────►│   Server.py     │
│                 │                    │                 │
│ • File Download │                    │ • summarize()   │
│ • User Interface│                    │ • format_to_    │
│ • Logging       │                    │   markdown()    │
│ • Error Handling│                    │ • AI Sampling   │
└─────────────────┘                    └─────────────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌─────────────────┐                    ┌─────────────────┐
│ HTTP Downloads  │                    │ Anthropic API   │
│ • PDF Files     │                    │ • Claude Sonnet │
│ • TXT Files     │                    │ • Text Gen      │
└─────────────────┘                    └─────────────────┘
```

## Features

### 🔍 **Document Processing**
- Downloads PDF and TXT files from HTTP URLs
- Extracts text content using PyPDF2 for PDFs
- Handles various content types and error conditions

### 🤖 **AI-Powered Summarization**
- Uses Anthropic's Claude Sonnet 4.0 for intelligent summarization
- Configurable model and API key management
- Comprehensive error handling and logging

### 📝 **Markdown Formatting**
- Converts plain text summaries into structured markdown
- Includes headers, bullet points, code blocks, and tables
- Professional document formatting

### 🔧 **Interactive Interface**
- Two main actions: `summarize` and `printable_summary`
- Real-time progress feedback
- Comprehensive logging for debugging

### 📊 **Comprehensive Logging**
- Separate logging for client and server components
- Detailed process tracking and error reporting
- Easy debugging and monitoring

## Setup

### Prerequisites
- Python 3.10 or higher
- Anthropic API key
- Internet connection for downloading documents

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anandharidas/anthropic-eg-sampling.git
   cd anthropic-eg-sampling
   ```

2. **Create configuration file:**
   Create `~/anandharidas/anthropic-config` with your API key and model:
   ```
   api_key=your_anthropic_api_key_here
   model=claude-sonnet-4-0
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

## Usage

### Running the Application

```bash
uv run client.py
```

### Available Actions

1. **`summarize`** - Download and summarize a document
2. **`printable_summary`** - Download, summarize, and format as markdown
3. **`quit`** - Exit the application

### Example Workflow

```
MCP Client is running. Type 'quit' to exit.
Available actions:
1. summarize - Summarize a document
2. printable_summary - Summarize a document and format as markdown
3. quit - Exit the client

Enter action (summarize/printable_summary/quit): printable_summary
Enter the HTTP link to the PDF or TXT file you want to summarize and format: https://example.com/document.pdf
Downloading and extracting content...
Content extracted (5000 characters). Summarizing...
Summary generated (500 characters). Formatting as markdown...

Markdown Formatted Summary:
# Document Summary

## Key Points
- Point 1
- Point 2
- Point 3

## Technical Details
- Detail 1
- Detail 2
```

## Project Structure

```
sampling/
├── client.py              # MCP client with UI and document processing
├── server.py              # MCP server with AI tools
├── pyproject.toml         # Project dependencies and metadata
├── README.md              # This documentation
├── .gitignore             # Git ignore rules
└── uv.lock               # Dependency lock file
```

## Key Functions

### Client Functions (`client.py`)

#### `download_and_extract_content(url: str) -> str`
- Downloads files from HTTP URLs
- Extracts text from PDF and TXT files
- Handles various content types and errors
- Returns extracted text content

#### `chat(input_messages: list[SamplingMessage], max_tokens=4000)`
- Processes messages for AI interaction
- Calls Anthropic's Claude API
- Manages conversation context
- Returns AI-generated text

#### `sampling_callback(context, params)`
- MCP callback for handling AI sampling requests
- Processes incoming messages
- Coordinates with chat function
- Returns structured responses

### Server Functions (`server.py`)

#### `summarize(text_to_summarize: str, ctx: Context)`
- MCP tool for document summarization
- Creates structured prompts for AI
- Calls Claude via sampling
- Returns summarized text

#### `format_to_markdown(summary_text: str, ctx: Context)`
- MCP tool for markdown formatting
- Converts plain text to structured markdown
- Uses specialized formatting prompts
- Returns formatted markdown

## Dependencies

### Core Dependencies
- `anthropic>=0.53.0` - Anthropic Claude API client
- `mcp[cli]>=1.9.3` - Model Context Protocol implementation
- `aiohttp>=3.8.0` - Async HTTP client for downloads
- `PyPDF2>=3.0.0` - PDF text extraction

### Development Dependencies
- `uv` - Fast Python package manager
- `aioconsole>=0.8.1` - Async console utilities

## MCP Implementation Details

### Tool Definition
```python
@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):
    # Tool implementation
```

### Sampling Integration
```python
result = await ctx.session.create_message(
    messages=[SamplingMessage(role="user", content=TextContent(type="text", text=prompt))],
    max_tokens=4000,
    system_prompt="You are a helpful research assistant."
)
```

### Error Handling
- Comprehensive try-catch blocks
- Detailed logging for debugging
- Graceful degradation on failures
- User-friendly error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Anthropic for the Claude AI model
- MCP community for the protocol specification
- Python community for excellent libraries

---

For more information about MCP, visit the [official documentation](https://modelcontextprotocol.io/).
