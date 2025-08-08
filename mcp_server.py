"""ATOMS.TECH MCP Server - Enhanced with Phase 1 Foundation Tools."""
import os
import sys
import logging
from typing import Any, Dict, Optional
from datetime import datetime

# Core business logic tools
from tools.core.pull_projects_tool import pull_projects_tool
from tools.core.pull_documents_tool import pull_documents_tool
from tools.core.pull_members_tool import pull_members_tool
from tools.core.get_documents_by_projects_tool import get_documents_by_projects_tool
from tools.core.task_assign_tool import task_assign_tool

# Document processing tools (enhanced)
from tools.analyze_doc_tool import analyze_doc_tool
from tools.mail_to_tool import mail_to_tool

# Reporting tools
from tools.reporting.get_project_issues_tool import get_project_issues_tool
from tools.reporting.progress_reporting_tool import progress_reporting_tool
from tools.reporting.milestone_tracking_tool import milestone_tracking_tool

# Phase 1 Foundation Tools imports (loaded dynamically in functions to avoid import errors)
# from tools.database.natural_query_tool import natural_query_tool
# from tools.database.analytics_tool import analytics_tool  
# from tools.document_processing.ocr_processing_tool import ocr_processing_tool
# from tools.document_processing.advanced_pdf_tool import advanced_pdf_tool
# from tools.file_management.file_system_tool import file_system_tool

# Phase 2 Strategic Tools imports (loaded dynamically in functions to avoid import errors)
# from tools.workflow.n8n_integration_tool import n8n_workflow_automation_tool
# from tools.standards.context7_integration_tool import context7_standards_integration_tool
# from tools.reasoning.sequential_integration_tool import sequential_reasoning_tool
# from tools.ui_generation.magic_integration_tool import magic_ui_generation_tool

# Framework imports
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('atoms_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MCP Server Configuration
MCP_SERVERS_CONFIG = {
    'postgresql': {
        'enabled': os.environ.get('POSTGRESQL_MCP_ENABLED', 'true').lower() == 'true',
        'connection_string': os.environ.get('SUPABASE_CONNECTION_STRING', ''),
        'max_connections': int(os.environ.get('POSTGRESQL_MAX_CONNECTIONS', '10'))
    },
    'google_ocr': {
        'enabled': os.environ.get('GOOGLE_OCR_ENABLED', 'false').lower() == 'true',
        'api_key': os.environ.get('GOOGLE_OCR_API_KEY', ''),
        'project_id': os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '')
    },
    'pdf_processing': {
        'enabled': os.environ.get('PDF_PROCESSING_ENABLED', 'true').lower() == 'true',
        'max_file_size': int(os.environ.get('PDF_MAX_FILE_SIZE', '50000000'))  # 50MB
    },
    'file_system': {
        'enabled': os.environ.get('FILE_SYSTEM_ENABLED', 'true').lower() == 'true',
        'storage_path': os.environ.get('FILE_STORAGE_PATH', '/tmp/atoms_storage')
    },
    # Phase 2 Strategic Tools Configuration
    'n8n': {
        'enabled': os.environ.get('N8N_MCP_ENABLED', 'false').lower() == 'true',
        'server_url': os.environ.get('N8N_SERVER_URL', 'http://localhost:5678'),
        'api_key': os.environ.get('N8N_API_KEY', ''),
        'webhook_base_url': os.environ.get('N8N_WEBHOOK_BASE_URL', 'http://localhost:5678')
    },
    'context7': {
        'enabled': os.environ.get('CONTEXT7_ENABLED', 'false').lower() == 'true',
        'server_url': os.environ.get('CONTEXT7_SERVER_URL', 'https://api.context7.com'),
        'api_key': os.environ.get('CONTEXT7_API_KEY', '')
    },
    'sequential': {
        'enabled': os.environ.get('SEQUENTIAL_ENABLED', 'false').lower() == 'true',
        'server_url': os.environ.get('SEQUENTIAL_SERVER_URL', 'https://api.sequential.ai'),
        'api_key': os.environ.get('SEQUENTIAL_API_KEY', '')
    },
    'magic': {
        'enabled': os.environ.get('MAGIC_ENABLED', 'false').lower() == 'true',
        'server_url': os.environ.get('MAGIC_SERVER_URL', 'https://api.magic.dev'),
        'api_key': os.environ.get('MAGIC_API_KEY', '')
    },
    # Phase 3 Custom Requirements Intelligence Configuration
    'intelligence': {
        'enabled': os.environ.get('INTELLIGENCE_ENABLED', 'true').lower() == 'true',
        'ai_model_cache_size': int(os.environ.get('AI_MODEL_CACHE_SIZE', '1000')),
        'embedding_model': os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
        'realtime_monitoring_interval': int(os.environ.get('REALTIME_MONITORING_INTERVAL', '30')),
        'max_concurrent_analysis': int(os.environ.get('MAX_CONCURRENT_ANALYSIS', '5')),
        'max_embedding_batch_size': int(os.environ.get('MAX_EMBEDDING_BATCH_SIZE', '100')),
        'cache_ttl': int(os.environ.get('INTELLIGENCE_CACHE_TTL', '3600')),
        'compliance_standards': os.environ.get('COMPLIANCE_STANDARDS', 'GDPR,ISO27001,IEEE830,NIST').split(','),
        'prediction_accuracy_threshold': float(os.environ.get('PREDICTION_ACCURACY_THRESHOLD', '0.85')),
        'recommendation_confidence_threshold': float(os.environ.get('RECOMMENDATION_CONFIDENCE_THRESHOLD', '0.90'))
    }
}

# Store organization_id per session
SESSION_ORGS = {}

def extract_org_id_from_session(session_id: str) -> str:
    """Extract organization_id from session_id"""
    if not session_id:
        raise ValueError("No session_id provided")
    
    print(f"Full session_id: {session_id}")
    
    # session_id는 UUID 형식 (32자리 hex)
    # 하이픈 제거 후 32자리인지 확인
    cleaned_session = session_id.replace('-', '')
    
    if len(cleaned_session) == 32:
        # 전체가 organization_id
        org_id = session_id
        print(f"Using full session_id as organization_id: {org_id}")
        return org_id
    elif len(cleaned_session) >= 32:
        # 마지막 32자리가 organization_id (하이픈 포함하여 재구성)
        hex_part = cleaned_session[-32:]
        # UUID 형식으로 변환: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        org_id = f"{hex_part[:8]}-{hex_part[8:12]}-{hex_part[12:16]}-{hex_part[16:20]}-{hex_part[20:32]}"
        print(f"Extracted organization_id from session: {org_id}")
        return org_id
    else:
        raise ValueError(f"Session ID too short to extract organization_id: {session_id}")

def get_organization_id_for_session(session_id: str = None) -> str:
    """Get organization_id for current session"""
    if not session_id:
        raise ValueError("No session_id provided")
        
    if session_id in SESSION_ORGS:
        return SESSION_ORGS[session_id]
    
    org_id = extract_org_id_from_session(session_id)
    SESSION_ORGS[session_id] = org_id
    return org_id

# Helper function to clean up technical fields
def clean_result(result):
    """Remove technical fields like IDs from the result"""
    if isinstance(result, dict) and "json" in result:
        # Remove top-level technical fields
        technical_fields = ["project_ids", "user_ids", "document_ids", "id"]
        for field in technical_fields:
            if field in result["json"]:
                del result["json"][field]
        
        # Recursively clean nested structures
        _clean_nested_ids(result["json"])
    
    return result

def _clean_nested_ids(data):
    """Recursively remove id fields from nested data structures"""
    if isinstance(data, list):
        for item in data:
            _clean_nested_ids(item)
    elif isinstance(data, dict):
        # Remove id fields
        if "id" in data:
            del data["id"]
        # Continue cleaning nested structures
        for value in data.values():
            _clean_nested_ids(value)

# Global variable to store current session info
CURRENT_SESSION_ID = None

def get_current_org_id() -> str:
    """Get organization_id for current request"""
    # Try to extract organization_id directly from context
    org_id = extract_org_id_from_context()
    
    if org_id:
        print(f"Using organization_id: {org_id}")
        return org_id
    
    # Fallback: try environment variables
    org_id = (
        os.environ.get("organization_id") or 
        os.environ.get("ORGANIZATION_ID") or
        os.environ.get("ORG_ID")
    )
    
    if org_id:
        print(f"Using organization_id from environment: {org_id}")
        return org_id
        
    raise ValueError("No organization_id found in headers, context, or environment")

# Wrapper functions that use organization_id from session
def pull_projects(message: str) -> Any:
    """
    Call tool if user want to check, list up or retrieve detailed information about our projects. It provides all projects's information, names, and descriptions.
    
    Parameters
    ----------
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    org_id = get_current_org_id()
    print("organization_id: ", org_id)
    print("message: ", message)
    result = pull_projects_tool(org_id, message)
    return clean_result(result)

def pull_documents(message: str) -> Any:
    """
    If user wants to get documents' names, descriptions from database

    Parameters
    ----------
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    org_id = get_current_org_id()
    return pull_documents_tool(org_id, message)

def pull_members(message: str) -> Any:
    """
    If user wants to get member information from projects or organizations

    Parameters
    ----------
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """    
    org_id = get_current_org_id()
    result = pull_members_tool(org_id, message)
    return clean_result(result)

def mail_to(message: str):
    """
    If user wants to send email messages to specified recipients with attachment support

    Parameters
    ----------
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    org_id = get_current_org_id()
    return mail_to_tool(org_id, message)

def get_documents_by_projects(message: str) -> Any:
    """
    Get documents from specific projects within an organization

    Parameters
    ----------
        message (str): User's request message containing project specifications

    Returns
    -------
    Any
        Structured result containing documents from specified projects
    """
    org_id = get_current_org_id()
    result = get_documents_by_projects_tool(org_id, message)
    return clean_result(result)

def task_assign(message: str) -> Any:
    """
    Retrieve task assignments for team members in projects

    Parameters
    ----------
        message (str): User's request message for task assignment information

    Returns
    -------
    Any
        Structured result containing task assignments by team members and projects
    """
    org_id = get_current_org_id()
    result = task_assign_tool(org_id, message)
    return clean_result(result)

def analyze_doc(message: str) -> Any:
    """
    Analyze document content and provide AI-powered summary and insights

    Parameters
    ----------
        message (str): User's request message specifying which document to analyze

    Returns
    -------
    Any
        Structured result containing document analysis and AI-generated summary
    """
    org_id = get_current_org_id()
    result = analyze_doc_tool(org_id, message)
    return clean_result(result)

def get_project_issues(message: str) -> Any:
    """
    Retrieve all issues/tasks from projects within an organization

    Parameters
    ----------
        message (str): User's request message for project issues information

    Returns
    -------
    Any
        Structured result containing issues/tasks from all projects
    """
    org_id = get_current_org_id()
    result = get_project_issues_tool(org_id, message)
    return clean_result(result)

def progress_reporting(message: str) -> Any:
    """
    Generate comprehensive progress reports for projects in an organization

    Parameters
    ----------
        message (str): User's request message for progress reporting

    Returns
    -------
    Any
        Structured result containing detailed progress reports for all projects
    """
    org_id = get_current_org_id()
    result = progress_reporting_tool(org_id, message)
    return clean_result(result)

def milestone_tracking(message: str) -> Any:
    """
    Track and analyze project milestones and key achievements

    Parameters
    ----------
        message (str): User's request message for milestone tracking

    Returns
    -------
    Any
        Structured result containing milestone tracking data and analysis
    """
    org_id = get_current_org_id()
    result = milestone_tracking_tool(org_id, message)
    return clean_result(result)

# Phase 1 Foundation Tools - Enhanced MCP Integration

def natural_query(message: str) -> Any:
    """
    Execute natural language database queries for complex requirements analysis
    
    Phase 1 Foundation Tool - PostgreSQL MCP Server Integration
    
    Purpose: Enable natural language database queries across ATOMS organization data
    Expected Benefits:
    - 60% improvement in complex query efficiency
    - Natural language interface reduces technical barriers  
    - Advanced analytics for requirements traceability

    Parameters
    ----------
        message (str): Natural language query request

    Returns
    -------
    Any
        Structured query results with metadata and analytics
        
    Examples:
        - "Show me all projects with their document counts"
        - "Find requirements that trace to other requirements"
        - "Check compliance status for all requirements"
        - "List documents by project with requirement counts"
    """
    org_id = get_current_org_id()
    from tools.database.natural_query_tool import natural_query_tool_sync
    result = natural_query_tool_sync(org_id, message)
    return clean_result(result)

def analytics_query(message: str) -> Any:
    """
    Generate advanced analytics and insights for requirements engineering
    
    Phase 1 Foundation Tool - Database Intelligence Enhancement
    
    Purpose: Provide comprehensive analytics across ATOMS organization data
    Expected Benefits:
    - Complex multi-table analysis for requirements traceability
    - Usage analytics for billing and feature adoption insights
    - Audit trail analytics for compliance reporting

    Parameters
    ----------
        message (str): Analytics request specifying type and parameters

    Returns
    -------
    Any
        Comprehensive analytics results with metadata
        
    Analytics Types:
        - project_overview: Overall project statistics and trends
        - document_metrics: Document-focused analytics and quality metrics
        - requirements_analysis: Requirements quality and traceability analytics
        - compliance_status: Compliance analytics across standards
        - user_engagement: User activity and feature usage analytics
        - traceability_analysis: Traceability network analysis
        - quality_metrics: Quality scoring and process metrics
        - performance_insights: System performance and usage patterns
    """
    org_id = get_current_org_id()
    from tools.database.analytics_tool import analytics_tool_sync
    result = analytics_tool_sync(org_id, message)
    return clean_result(result)

def ocr_processing(message: str) -> Any:
    """
    Enterprise-grade OCR processing for requirements document ingestion
    
    Phase 1 Foundation Tool - Google OCR MCP Server Integration
    
    Purpose: Process uploaded documents with Google OCR MCP Server integration
    Expected Benefits:
    - Superior accuracy for technical documentation (94%+ confidence)
    - 40-60% improvement in document processing accuracy
    - Support for multiple languages and technical formats
    - Structured requirements extraction and analysis

    Parameters
    ----------
        message (str): OCR processing request with file information

    Returns
    -------
    Any
        OCR results with structured requirements analysis
        
    Supported Formats:
        - Images: JPEG, PNG, TIFF, BMP
        - Documents: PDF
        
    Features:
        - Text extraction with high confidence scoring
        - Requirements pattern recognition
        - Document structure analysis
        - Content quality recommendations
        - Multi-language support
    """
    org_id = get_current_org_id()
    from tools.document_processing.ocr_processing_tool import ocr_processing_tool_sync
    result = ocr_processing_tool_sync(org_id, message)
    return clean_result(result)

def advanced_pdf_processing(message: str) -> Any:
    """
    Advanced PDF analysis and content extraction for requirements documents
    
    Phase 1 Foundation Tool - PDF Processing MCP Server Integration
    
    Purpose: Enhanced PDF processing beyond basic OCR with structure analysis
    Expected Benefits:
    - Enhanced text extraction with structure preservation
    - Table and diagram recognition and extraction
    - Requirements pattern detection and quality analysis
    - Integration with AI analysis workflows

    Parameters
    ----------
        message (str): PDF processing request with file information and options

    Returns
    -------
    Any
        Comprehensive PDF analysis with requirements insights
        
    Features:
        - Document structure analysis (headings, sections, subsections)
        - Table extraction and analysis
        - Image and diagram detection
        - Requirements quality scoring
        - Traceability potential assessment
        - Compliance coverage analysis
        - Improvement recommendations
    """
    org_id = get_current_org_id()
    from tools.document_processing.advanced_pdf_tool import advanced_pdf_tool_sync
    result = advanced_pdf_tool_sync(org_id, message)
    return clean_result(result)

def file_system_management(message: str) -> Any:
    """
    Intelligent file organization and management for requirements documents
    
    Phase 1 Foundation Tool - File System MCP Server Integration
    
    Purpose: Provide comprehensive file system management with AI-powered organization
    Expected Benefits:
    - Automated file categorization and organization
    - Content-based file search and retrieval
    - Integration with document versioning
    - Secure file access with permission controls

    Parameters
    ----------
        message (str): File system operation request

    Returns
    -------
    Any
        File system operation results
        
    Operations:
        - list: List files with filtering options
        - categorize: Auto-categorize files based on content
        - search: Content-based file search
        - organize: Organize files into structured layout
        - analyze: Storage usage analysis and insights
        - cleanup: Clean up old/duplicate files
        - backup: Backup files to archive
        - restore: Restore files from archive
    """
    org_id = get_current_org_id()
    from tools.file_management.file_system_tool import file_system_tool_sync
    result = file_system_tool_sync(org_id, message)
    return clean_result(result)

# Phase 2 Strategic Tools - Advanced MCP Integration

def workflow_automation(message: str) -> Any:
    """
    Advanced workflow automation for requirements engineering processes
    
    Phase 2 Strategic Tool - N8N MCP Server Integration
    
    Purpose: Create and manage automated workflows for requirements validation,
    compliance checking, stakeholder notifications, and approval processes
    
    Expected Benefits:
    - 50-70% reduction in manual process management
    - Automated requirements validation workflows
    - Integration with external systems (Slack, email, project management)
    - Custom automation rules based on document changes
    - Notifications and approval processes

    Parameters
    ----------
        message (str): Workflow automation request with configuration

    Returns
    -------
    Any
        Workflow automation results with execution details
        
    Operations:
        - create_workflow: Create new automated workflow
        - list_workflows: List organization's workflows
        - trigger_workflow: Manually trigger workflow execution
        - workflow_status: Check workflow execution status
        - update_workflow: Modify existing workflow configuration
    """
    org_id = get_current_org_id()
    from tools.workflow.n8n_integration_tool import n8n_workflow_automation_tool_sync
    result = n8n_workflow_automation_tool_sync(org_id, message)
    return clean_result(result)

def standards_compliance(message: str) -> Any:
    """
    Industry standards and best practices integration for requirements engineering
    
    Phase 2 Strategic Tool - Context7 MCP Server Integration
    
    Purpose: Provide access to requirements engineering standards and best practices
    for compliance checking, template generation, and quality improvement
    
    Expected Benefits:
    - IEEE 830, ISO 29148 standards compliance checking
    - Requirements template generation
    - Best practice recommendations
    - Standards-based quality scoring
    - 40% improvement in AI recommendation accuracy

    Parameters
    ----------
        message (str): Standards integration request

    Returns
    -------
    Any
        Standards analysis and recommendations
        
    Operations:
        - compliance_check: Check document compliance against standards
        - generate_template: Create requirements templates
        - best_practices: Get best practices recommendations
        - standards_info: Get information about specific standards
        - quality_assessment: Assess requirements quality against standards
    """
    org_id = get_current_org_id()
    from tools.standards.context7_integration_tool import context7_standards_integration_tool_sync
    result = context7_standards_integration_tool_sync(org_id, message)
    return clean_result(result)

def multi_step_reasoning(message: str) -> Any:
    """
    Complex multi-step analysis and reasoning for requirements engineering
    
    Phase 2 Strategic Tool - Sequential MCP Server Integration
    
    Purpose: Perform sophisticated multi-step analysis for complex requirements
    engineering challenges requiring systematic reasoning approaches
    
    Expected Benefits:
    - Complex requirements impact analysis
    - Multi-step validation chains
    - Advanced traceability analysis  
    - Root cause analysis for requirements conflicts
    - 3x improvement in complex analysis capabilities

    Parameters
    ----------
        message (str): Multi-step reasoning request

    Returns
    -------
    Any
        Complex analysis results with step-by-step reasoning
        
    Analysis Types:
        - impact_analysis: Assess impacts of requirement changes
        - traceability_analysis: Analyze requirements traceability
        - conflict_resolution: Resolve requirements conflicts
        - validation_chain: Multi-step requirements validation
        - root_cause_analysis: Identify root causes of issues
    """
    org_id = get_current_org_id()
    from tools.reasoning.sequential_integration_tool import sequential_reasoning_tool_sync
    result = sequential_reasoning_tool_sync(org_id, message)
    return clean_result(result)

def dynamic_ui_generation(message: str) -> Any:
    """
    Dynamic UI components for requirements management
    
    Phase 2 Strategic Tool - Magic MCP Server Integration
    
    Purpose: Generate modern, responsive UI components for requirements
    management with AI-powered design and accessibility features
    
    Expected Benefits:
    - Dynamic dashboard generation
    - Custom forms for requirements capture  
    - Interactive visualization components
    - Responsive requirements management interfaces
    - Rapid UI development and customization

    Parameters
    ----------
        message (str): UI generation request

    Returns
    -------
    Any
        Generated UI components with code and styling
        
    Component Types:
        - requirements_form: Dynamic forms for capturing requirements
        - dashboard: Interactive dashboards with metrics and charts
        - traceability_matrix: Visual traceability matrix components
        - requirements_editor: Rich text editors with AI assistance
        - compliance_checker: Real-time compliance checking interfaces
        - analytics_widget: Configurable analytics widgets
    """
    org_id = get_current_org_id()
    from tools.ui_generation.magic_integration_tool import magic_ui_generation_tool_sync
    result = magic_ui_generation_tool_sync(org_id, message)
    return clean_result(result)
    
port = int(os.environ.get("PORT", 10000))

mcp = FastMCP("AtomsMCP", host="0.0.0.0", port=port)

# Hook to capture organization_id from MCP headers
def extract_org_id_from_context():
    """Try to extract organization_id from current context"""
    import inspect
    
    # Get current frame and look for headers or organization_id in call stack
    frame = inspect.currentframe()
    try:
        while frame:
            local_vars = frame.f_locals
            
            # Look for organization_id directly
            if 'organization_id' in local_vars:
                org_id = local_vars['organization_id']
                print(f"Found organization_id in context: {org_id}")
                return org_id
                
            # Look for headers containing organization_id
            if 'headers' in local_vars:
                headers = local_vars['headers']
                if hasattr(headers, 'get'):
                    org_id = headers.get('organization_id') or headers.get('x-organization-id')
                    if org_id:
                        print(f"Found organization_id in headers: {org_id}")
                        return org_id
            
            # Look for request object with headers
            if 'request' in local_vars:
                request = local_vars['request']
                if hasattr(request, 'headers'):
                    org_id = request.headers.get('organization_id') or request.headers.get('x-organization-id')
                    if org_id:
                        print(f"Found organization_id in request headers: {org_id}")
                        return org_id
                        
            frame = frame.f_back
    finally:
        del frame
    return None

mcp.add_tool(pull_projects)
mcp.add_tool(pull_documents)
mcp.add_tool(pull_members)
# mcp.add_tool(mail_to)

# Add existing tools
mcp.add_tool(get_documents_by_projects)
mcp.add_tool(task_assign)
mcp.add_tool(analyze_doc)
mcp.add_tool(get_project_issues)
mcp.add_tool(progress_reporting)
mcp.add_tool(milestone_tracking)

# Add Phase 1 Foundation Tools
mcp.add_tool(natural_query)
mcp.add_tool(analytics_query)
mcp.add_tool(ocr_processing)
mcp.add_tool(advanced_pdf_processing)
mcp.add_tool(file_system_management)

# Add Phase 2 Strategic Tools
mcp.add_tool(workflow_automation)
mcp.add_tool(standards_compliance)
mcp.add_tool(multi_step_reasoning)
mcp.add_tool(dynamic_ui_generation)

if __name__ == "__main__":
    print(f"Starting MCP server on 0.0.0.0:{port}")
    mcp.run(transport="sse")