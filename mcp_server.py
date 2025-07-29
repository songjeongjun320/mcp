"""Auto-generated FastMCP server for Render deployment."""

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from tools.pull_projects_tool import pull_projects
from tools.pull_documents_tool import pull_documents
from tools.pull_members_tool import pull_members
from tools.mail_to_tool import mail_to
from mcp.server.fastmcp import FastMCP

# Create FastAPI app
app = FastAPI(title="MCP Server", description="Model Context Protocol Server")

# Create MCP instance
mcp = FastMCP("Demo")
mcp.add_tool(pull_projects)
mcp.add_tool(pull_documents)
mcp.add_tool(pull_members)
mcp.add_tool(mail_to)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "MCP Server is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "service": "mcp-server"}

@app.post("/mcp/tools/pull_projects")
async def api_pull_projects(organization_id: str, message: str):
    """API endpoint for pull_projects tool"""
    try:
        result = pull_projects(organization_id, message)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/mcp/tools/pull_documents")
async def api_pull_documents(organization_id: str, message: str):
    """API endpoint for pull_documents tool"""
    try:
        result = pull_documents(organization_id, message)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/mcp/tools/pull_members")
async def api_pull_members(organization_id: str, message: str):
    """API endpoint for pull_members tool"""
    try:
        result = pull_members(organization_id, message)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/mcp/tools/mail_to")
async def api_mail_to(organization_id: str, sender: str, recipient: str, recipient_email: str, subject: str, body: str, message: str):
    """API endpoint for mail_to tool"""
    try:
        result = mail_to(organization_id, sender, recipient, recipient_email, subject, body, message)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
