from mcp.server.fastmcp import FastMCP
import math

# Initialize the MCP server
mcp = FastMCP("Hello World")


# Define tools
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    return a / b


@mcp.tool()
def power(a: int, b: int) -> int:
    """Raise a to the power of b"""
    return a ** b


@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    return math.sqrt(a)


@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    return a ** (1/3)


@mcp.tool()
def factorial(a: int) -> int:
    """Factorial of a number"""
    return math.factorial(a)


@mcp.tool()
def log(a: int) -> float:
    """Natural logarithm of a number"""
    return math.log(a)


@mcp.tool()
def remainder(a: int, b: int) -> int:
    """Remainder of division"""
    return a % b


@mcp.tool()
def sin(a: int) -> float:
    """Sine of a number"""
    return math.sin(a)


@mcp.tool()
def cos(a: int) -> float:
    """Cosine of a number"""
    return math.cos(a)


@mcp.tool()
def tan(a: int) -> float:
    """Tangent of a number"""
    return math.tan(a)


# Define a resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
