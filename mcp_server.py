"""Auto-generated FastMCP server."""

from tools.pull_projects_tool import pull_projects
from tools.pull_documents_tool import pull_documents
from tools.pull_members_tool import pull_members
from tools.mail_to_tool import mail_to
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AtomsMCP")

mcp.add_tool(pull_projects)
mcp.add_tool(pull_documents)
mcp.add_tool(pull_members)
mcp.add_tool(mail_to)

if __name__ == "__main__":
    mcp.run(transport="stdio")