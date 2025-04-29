# MCP: Model Context Protocol

An entry level example of a MCP server with two tools (functions) and how it is used with Ollama running a current LLM Model.

## Installation

```
deactivate
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 

```

## Start mcp server

In order to test the MCP Server, you may start it with (once you have finished the installation)

```
python string_tools_server.py

```

## Test with llm

```
python ollama_mcp.py

```
