"""Create test requirement tool module"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def create_test_requirement_tool(organization_id: str, message: str) -> Any:
    """
    Create comprehensive test requirements/test cases for system validation.
    Supports various test types including unit, integration, system, and acceptance tests.
    
    Parameters
    ----------
    organization_id : str
        User's individual organization ID
    message : str
        User's request message containing test requirement specifications
        
    Returns
    -------
    Any
        Result containing created test requirement information
    """
    print(f"[create_test_requirement] Starting with organization_id: {organization_id}")
    print(f"[create_test_requirement] Message: {message}")
    
    try:
        # Create Supabase client
        print("[create_test_requirement] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Parse message to extract test requirement parameters
        test_data = _parse_test_requirement_message(message)
        
        if not test_data:
            return {
                "json": {
                    "error": "Invalid message format. Please provide test title, description, type, and project context.",
                    "message": message
                }
            }
        
        # Validate project exists and belongs to organization
        validation_result = _validate_project_access(supabase, organization_id, test_data.get("project_id"))
        if not validation_result["valid"]:
            return {
                "json": {
                    "error": validation_result["error"],
                    "message": message
                }
            }
        
        # Create test requirement
        test_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Generate test steps if not provided
        if not test_data.get("test_steps"):
            test_data["test_steps"] = _generate_default_test_steps(test_data)
        
        test_requirement = {
            "id": test_id,
            "test_id": test_data.get("external_test_id", f"TEST-{test_id[:8]}"),
            "project_id": test_data["project_id"],
            "title": test_data["title"],
            "description": test_data["description"],
            "test_type": test_data.get("test_type", "functional"),
            "priority": test_data.get("priority", "medium"),
            "status": test_data.get("status", "planned"),
            "method": test_data.get("method", "manual"),
            "expected_results": test_data.get("expected_results", "Test should pass successfully"),
            "preconditions": test_data.get("preconditions", "System is available and accessible"),
            "test_steps": test_data["test_steps"],
            "estimated_duration": test_data.get("estimated_duration", "00:30:00"),  # 30 minutes default
            "category": test_data.get("category", ["functional"]),
            "test_environment": test_data.get("test_environment", "test"),
            "version": test_data.get("version", "1.0"),
            "is_active": True,
            "created_at": current_time,
            "updated_at": current_time,
            "created_by": "mcp-server",  # Could be enhanced to track actual user
            "updated_by": "mcp-server"
        }
        
        print(f"[create_test_requirement] Creating test requirement: {test_data['title']}")
        
        # Insert test requirement
        response = supabase.table("test_req").insert(test_requirement).execute()
        
        if response.data:
            print("[create_test_requirement] Test requirement created successfully")
            
            # Link to requirements if specified
            if test_data.get("requirement_ids"):
                _create_requirement_test_links(supabase, test_id, test_data["requirement_ids"])
            
            # Get project details for response
            project_details = _get_project_details(supabase, test_data["project_id"])
            
            result = {
                "json": {
                    "test_id": test_id,
                    "external_test_id": test_requirement["test_id"],
                    "title": test_data["title"],
                    "test_type": test_data.get("test_type", "functional"),
                    "priority": test_data.get("priority", "medium"),
                    "status": test_data.get("status", "planned"),
                    "method": test_data.get("method", "manual"),
                    "project": project_details,
                    "test_steps_count": len(test_data["test_steps"]),
                    "estimated_duration": test_data.get("estimated_duration", "00:30:00"),
                    "created_at": current_time,
                    "linked_requirements": len(test_data.get("requirement_ids", [])),
                    "message": f"Test requirement '{test_data['title']}' created successfully"
                }
            }
            
            # Save result to JSON file
            print("[create_test_requirement] Saving result to JSON file...")
            with open("create_test_requirement_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("[create_test_requirement] SUCCESS: Completed successfully")
            return result
        else:
            print("[create_test_requirement] Failed to create test requirement")
            return {
                "json": {
                    "error": "Failed to create test requirement in database",
                    "message": message
                }
            }
            
    except Exception as e:
        print(f"[create_test_requirement] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def _parse_test_requirement_message(message: str) -> Optional[Dict[str, Any]]:
    """Parse message to extract test requirement parameters"""
    try:
        message_lower = message.lower()
        
        # Extract basic information
        test_data = {}
        
        # Look for project ID (UUID pattern)
        words = message.split()
        for word in words:
            if len(word) == 36 and "-" in word:  # UUID pattern
                test_data["project_id"] = word
                break
        
        # Extract test title (simple heuristic)
        if "test" in message_lower:
            # Look for quoted strings or capitalize words after "test"
            import re
            
            # Try to find quoted title
            quoted_match = re.search(r'"([^"]*)"', message)
            if quoted_match:
                test_data["title"] = quoted_match.group(1)
            else:
                # Simple extraction based on common patterns
                if "create test" in message_lower:
                    after_create = message_lower.split("create test")[-1].strip()
                    test_data["title"] = after_create.split(".")[0].split("for")[0].strip()
                else:
                    test_data["title"] = "New Test Case"
        
        # Set description
        test_data["description"] = message
        
        # Determine test type
        if "unit" in message_lower:
            test_data["test_type"] = "unit"
        elif "integration" in message_lower:
            test_data["test_type"] = "integration"
        elif "system" in message_lower:
            test_data["test_type"] = "system"
        elif "acceptance" in message_lower:
            test_data["test_type"] = "acceptance"
        elif "performance" in message_lower:
            test_data["test_type"] = "performance"
        elif "security" in message_lower:
            test_data["test_type"] = "security"
        elif "usability" in message_lower:
            test_data["test_type"] = "usability"
        else:
            test_data["test_type"] = "functional"
        
        # Determine priority
        if "critical" in message_lower or "high" in message_lower:
            test_data["priority"] = "high"
        elif "low" in message_lower:
            test_data["priority"] = "low"
        else:
            test_data["priority"] = "medium"
        
        # Determine method
        if "automated" in message_lower or "automation" in message_lower:
            test_data["method"] = "automated"
        else:
            test_data["method"] = "manual"
        
        # Set default values if missing
        if not test_data.get("title"):
            test_data["title"] = f"Test Case for {test_data.get('test_type', 'Functional')} Testing"
        
        return test_data
        
    except Exception as e:
        print(f"Error parsing test requirement message: {str(e)}")
        return None

def _validate_project_access(supabase, organization_id: str, project_id: str) -> Dict[str, Any]:
    """Validate that project exists and belongs to organization"""
    try:
        if not project_id:
            return {"valid": False, "error": "Project ID is required"}
        
        project_response = supabase.table("projects").select("id, name, organization_id").eq("id", project_id).execute()
        
        if not project_response.data:
            return {"valid": False, "error": "Project not found"}
        
        project = project_response.data[0]
        if project["organization_id"] != organization_id:
            return {"valid": False, "error": "Project does not belong to your organization"}
        
        return {"valid": True, "project": project}
        
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}

def _generate_default_test_steps(test_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate default test steps based on test type and description"""
    
    test_type = test_data.get("test_type", "functional")
    
    if test_type == "unit":
        return [
            {"step": 1, "action": "Set up test environment and test data", "expected": "Environment ready"},
            {"step": 2, "action": "Execute unit test function", "expected": "Function executes without errors"},
            {"step": 3, "action": "Verify test results against expected values", "expected": "All assertions pass"},
            {"step": 4, "action": "Clean up test environment", "expected": "Environment restored"}
        ]
    elif test_type == "integration":
        return [
            {"step": 1, "action": "Initialize system components", "expected": "All components start successfully"},
            {"step": 2, "action": "Execute integration scenario", "expected": "Components interact correctly"},
            {"step": 3, "action": "Verify data flow between components", "expected": "Data passed correctly"},
            {"step": 4, "action": "Validate end-to-end functionality", "expected": "Complete workflow functions"}
        ]
    elif test_type == "system":
        return [
            {"step": 1, "action": "Start complete system", "expected": "System loads successfully"},
            {"step": 2, "action": "Perform system-level operation", "expected": "Operation completes successfully"},
            {"step": 3, "action": "Verify system state", "expected": "System remains stable"},
            {"step": 4, "action": "Check system logs for errors", "expected": "No critical errors found"}
        ]
    elif test_type == "acceptance":
        return [
            {"step": 1, "action": "Access system as end user", "expected": "User can login successfully"},
            {"step": 2, "action": "Perform business workflow", "expected": "Workflow completes as expected"},
            {"step": 3, "action": "Verify business requirements met", "expected": "All acceptance criteria satisfied"},
            {"step": 4, "action": "Validate user experience", "expected": "Experience meets usability standards"}
        ]
    elif test_type == "performance":
        return [
            {"step": 1, "action": "Set up performance monitoring", "expected": "Monitoring tools ready"},
            {"step": 2, "action": "Execute performance test scenario", "expected": "Test completes within time limits"},
            {"step": 3, "action": "Measure response times", "expected": "Response times within acceptable range"},
            {"step": 4, "action": "Analyze performance metrics", "expected": "All metrics meet performance criteria"}
        ]
    else:  # functional or default
        return [
            {"step": 1, "action": "Prepare test environment", "expected": "Environment is ready"},
            {"step": 2, "action": "Execute test scenario", "expected": "Test executes successfully"},
            {"step": 3, "action": "Verify expected results", "expected": "Results match expectations"},
            {"step": 4, "action": "Document test outcome", "expected": "Test results recorded"}
        ]

def _create_requirement_test_links(supabase, test_id: str, requirement_ids: List[str]) -> None:
    """Create links between test and requirements"""
    try:
        current_time = datetime.now().isoformat()
        
        for req_id in requirement_ids:
            link_data = {
                "id": str(uuid.uuid4()),
                "requirement_id": req_id,
                "test_id": test_id,
                "execution_status": "not_executed",
                "created_at": current_time,
                "updated_at": current_time
            }
            
            supabase.table("requirement_tests").insert(link_data).execute()
            
    except Exception as e:
        print(f"Error creating requirement test links: {str(e)}")

def _get_project_details(supabase, project_id: str) -> Dict[str, Any]:
    """Get project details for response"""
    try:
        project_response = supabase.table("projects").select("id, name, description").eq("id", project_id).execute()
        
        if project_response.data:
            return {
                "id": project_response.data[0]["id"],
                "name": project_response.data[0]["name"],
                "description": project_response.data[0].get("description", "")
            }
        
        return {"id": project_id, "name": "Unknown Project", "description": ""}
        
    except Exception:
        return {"id": project_id, "name": "Unknown Project", "description": ""}

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Create unit test for login functionality in project c41a1968-dafe-466b-98c2-bcf8a5e71584"
    result = create_test_requirement_tool(test_org_id, test_message)
    print(f"Result: {result}")