from mcp.server.fastmcp import FastMCP

mcp = FastMCP("string_tools_server")

@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverses the given string."""
    return f"{text[::-1]}"

@mcp.tool()
def reverse_string2(text: str) -> str:
    """Reverses the given string and adds somthing"""
    return f"xxx -> {text[::-1]}"

@mcp.tool()
def count_words(text: str) -> int:
    """Counts the number of words in a sentence."""
    return len(text.split())

if __name__ == "__main__":
    mcp.run(transport="stdio")
