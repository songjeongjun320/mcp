"""Auto-generated FastMCP server with detailed logging."""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

from tools.pull_organization_tool import pull_organization
from tools.pull_projects_tool import pull_projects
from tools.pull_documents_tool import pull_documents
from tools.mail_to_tool import mail_to
from tools.calculate_sum_tool import calculate_sum
from tools.calculate_bmi_tool import calculate_bmi
from mcp.server.fastmcp import FastMCP

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_server.log', mode='a', encoding='utf-8')
    ]
)

# Get loggers
logger = logging.getLogger("MCP_SERVER")
tool_logger = logging.getLogger("TOOL_CALLS")

# Set FastMCP and related libraries to DEBUG level
logging.getLogger("mcp").setLevel(logging.DEBUG)
logging.getLogger("fastmcp").setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.INFO)

logger.info("="*60)
logger.info("MCP SERVER STARTING")
logger.info("="*60)

# Create MCP instance
mcp = FastMCP("Demo")

# Wrapper functions for detailed logging
def log_tool_call(tool_name: str, original_func):
    """Wrapper to log tool calls with detailed information."""
    def wrapper(*args, **kwargs):
        tool_logger.info(f"🔧 TOOL CALLED: {tool_name}")
        tool_logger.info(f"📥 INPUT ARGS: {args}")
        tool_logger.info(f"📥 INPUT KWARGS: {kwargs}")
        
        try:
            start_time = datetime.now()
            result = original_func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            tool_logger.info(f"✅ TOOL SUCCESS: {tool_name} (took {duration:.3f}s)")
            tool_logger.info(f"📤 OUTPUT: {result}")
            
            return result
            
        except Exception as e:
            tool_logger.error(f"❌ TOOL ERROR: {tool_name}")
            tool_logger.error(f"🚨 ERROR DETAILS: {str(e)}")
            tool_logger.error(f"🚨 ERROR TYPE: {type(e).__name__}")
            raise
    
    wrapper.__name__ = original_func.__name__
    wrapper.__doc__ = original_func.__doc__
    return wrapper

# Wrap all tools with logging
pull_organization_logged = log_tool_call("pull_organization", pull_organization)
pull_projects_logged = log_tool_call("pull_projects", pull_projects)
pull_documents_logged = log_tool_call("pull_documents", pull_documents)
mail_to_logged = log_tool_call("mail_to", mail_to)
calculate_sum_logged = log_tool_call("calculate_sum", calculate_sum)
calculate_bmi_logged = log_tool_call("calculate_bmi", calculate_bmi)

# Add tools to MCP server
logger.info("🔨 REGISTERING TOOLS...")

try:
    mcp.add_tool(pull_organization_logged)
    logger.info("✅ Registered: pull_organization")
except Exception as e:
    logger.error(f"❌ Failed to register pull_organization: {e}")

try:
    mcp.add_tool(pull_projects_logged)
    logger.info("✅ Registered: pull_projects")
except Exception as e:
    logger.error(f"❌ Failed to register pull_projects: {e}")

try:
    mcp.add_tool(pull_documents_logged)
    logger.info("✅ Registered: pull_documents")
except Exception as e:
    logger.error(f"❌ Failed to register pull_documents: {e}")

try:
    mcp.add_tool(mail_to_logged)
    logger.info("✅ Registered: mail_to")
except Exception as e:
    logger.error(f"❌ Failed to register mail_to: {e}")

try:
    mcp.add_tool(calculate_sum_logged)
    logger.info("✅ Registered: calculate_sum")
except Exception as e:
    logger.error(f"❌ Failed to register calculate_sum: {e}")

try:
    mcp.add_tool(calculate_bmi_logged)
    logger.info("✅ Registered: calculate_bmi")
except Exception as e:
    logger.error(f"❌ Failed to register calculate_bmi: {e}")

logger.info("🚀 ALL TOOLS REGISTERED SUCCESSFULLY")

if __name__ == "__main__":
    logger.info("🌐 STARTING MCP SERVER on SSE transport...")
    logger.info("📊 Log file: mcp_server.log")
    logger.info("🔍 Debug level: DEBUG")
    logger.info("="*60)
    
    try:
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        logger.info("🛑 SERVER STOPPED BY USER")
    except Exception as e:
        logger.error(f"💥 SERVER CRASHED: {e}")
        raise
