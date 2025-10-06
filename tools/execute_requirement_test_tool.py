"""Execute requirement test tool module"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def execute_requirement_test_tool(organization_id: str, message: str) -> Any:
    """
    Execute requirement tests and record test execution results with comprehensive tracking.
    Supports test execution status updates, results documentation, and evidence collection.
    
    Parameters
    ----------
    organization_id : str
        User's individual organization ID
    message : str
        User's request message containing test execution details
        
    Returns
    -------
    Any
        Result containing test execution results and updated status information
    """
    print(f"[execute_requirement_test] Starting with organization_id: {organization_id}")
    print(f"[execute_requirement_test] Message: {message}")
    
    try:
        # Create Supabase client
        print("[execute_requirement_test] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Parse message to extract execution parameters
        execution_data = _parse_execution_message(message)
        
        if not execution_data:
            return {
                "json": {
                    "error": "Invalid message format. Please provide test ID/name and execution status.",
                    "message": message
                }
            }
        
        # Find and validate test
        test_info = _find_and_validate_test(supabase, organization_id, execution_data)
        if not test_info["valid"]:
            return {
                "json": {
                    "error": test_info["error"],
                    "message": message
                }
            }
        
        # Execute test and record results
        execution_result = _execute_and_record_test(supabase, test_info["test"], execution_data)
        
        if execution_result["success"]:
            print("[execute_requirement_test] Test execution recorded successfully")
            
            # Get comprehensive test execution summary
            execution_summary = _get_execution_summary(supabase, test_info["test"], execution_result)
            
            result = {
                "json": {
                    "test_execution": {
                        "test_id": test_info["test"]["id"],
                        "test_title": test_info["test"]["title"],
                        "execution_status": execution_data["status"],
                        "executed_at": execution_result["executed_at"],
                        "executed_by": execution_data.get("executed_by", "mcp-server"),
                        "execution_environment": execution_data.get("environment", "test"),
                        "result_notes": execution_data.get("notes", ""),
                        "defects_found": len(execution_data.get("defects", [])),
                        "evidence_artifacts": len(execution_data.get("evidence", []))
                    },
                    "test_details": {
                        "test_type": test_info["test"]["test_type"],
                        "priority": test_info["test"]["priority"],
                        "method": test_info["test"]["method"],
                        "project_name": test_info.get("project_name", "Unknown")
                    },
                    "execution_summary": execution_summary,
                    "requirements_affected": execution_result.get("requirements_updated", []),
                    "message": f"Test execution recorded: {execution_data['status']}"
                }
            }
            
            # Save result to JSON file
            print("[execute_requirement_test] Saving result to JSON file...")
            with open("execute_requirement_test_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("[execute_requirement_test] SUCCESS: Completed successfully")
            return result
        else:
            return {
                "json": {
                    "error": execution_result["error"],
                    "message": message
                }
            }
            
    except Exception as e:
        print(f"[execute_requirement_test] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def _parse_execution_message(message: str) -> Optional[Dict[str, Any]]:
    """Parse message to extract test execution parameters"""
    try:
        message_lower = message.lower()
        
        execution_data = {}
        
        # Extract test identifier (ID or name pattern)
        words = message.split()
        for word in words:
            if len(word) == 36 and "-" in word:  # UUID pattern
                execution_data["test_id"] = word
                break
        
        # If no UUID, look for test name or external ID
        if "test_id" not in execution_data:
            import re
            # Look for test- pattern
            test_pattern = re.search(r'test-[a-zA-Z0-9]+', message_lower)
            if test_pattern:
                execution_data["external_test_id"] = test_pattern.group()
            else:
                # Look for quoted test name
                quoted_match = re.search(r'"([^"]*)"', message)
                if quoted_match:
                    execution_data["test_name"] = quoted_match.group(1)
        
        # Determine execution status
        if "passed" in message_lower or "success" in message_lower:
            execution_data["status"] = "passed"
        elif "failed" in message_lower or "fail" in message_lower:
            execution_data["status"] = "failed"
        elif "blocked" in message_lower:
            execution_data["status"] = "blocked"
        elif "skipped" in message_lower:
            execution_data["status"] = "skipped"
        else:
            # Default to passed if executing
            execution_data["status"] = "passed"
        
        # Extract environment
        if "production" in message_lower or "prod" in message_lower:
            execution_data["environment"] = "production"
        elif "staging" in message_lower:
            execution_data["environment"] = "staging"
        elif "development" in message_lower or "dev" in message_lower:
            execution_data["environment"] = "development"
        else:
            execution_data["environment"] = "test"
        
        # Extract notes/results
        execution_data["notes"] = message
        
        # Extract defects (simple pattern matching)
        defects = []
        if "bug" in message_lower or "defect" in message_lower or "issue" in message_lower:
            defects.append({
                "type": "defect",
                "description": "Issue identified during test execution",
                "severity": "medium"
            })
        execution_data["defects"] = defects
        
        # Extract evidence (simple pattern)
        evidence = []
        if "screenshot" in message_lower or "log" in message_lower or "evidence" in message_lower:
            evidence.append({
                "type": "log",
                "description": "Test execution evidence",
                "artifact": "test_execution_log.txt"
            })
        execution_data["evidence"] = evidence
        
        return execution_data
        
    except Exception as e:
        print(f"Error parsing execution message: {str(e)}")
        return None

def _find_and_validate_test(supabase, organization_id: str, execution_data: Dict[str, Any]) -> Dict[str, Any]:
    """Find and validate test belongs to organization"""
    try:
        test_response = None
        
        # Try to find test by different identifiers
        if "test_id" in execution_data:
            # Direct test ID lookup
            test_response = supabase.table("test_req").select(
                "*, projects!inner(id, name, organization_id)"
            ).eq("id", execution_data["test_id"]).execute()
        
        elif "external_test_id" in execution_data:
            # External test ID lookup
            test_response = supabase.table("test_req").select(
                "*, projects!inner(id, name, organization_id)"
            ).eq("test_id", execution_data["external_test_id"]).execute()
        
        elif "test_name" in execution_data:
            # Test name lookup
            test_response = supabase.table("test_req").select(
                "*, projects!inner(id, name, organization_id)"
            ).ilike("title", f"%{execution_data['test_name']}%").execute()
        
        if not test_response or not test_response.data:
            return {"valid": False, "error": "Test not found"}
        
        test = test_response.data[0]
        
        # Validate organization access
        if test["projects"]["organization_id"] != organization_id:
            return {"valid": False, "error": "Test does not belong to your organization"}
        
        return {
            "valid": True, 
            "test": test,
            "project_name": test["projects"]["name"]
        }
        
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}

def _execute_and_record_test(supabase, test: Dict[str, Any], execution_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute test and record results in requirement_tests table"""
    try:
        current_time = datetime.now().isoformat()
        
        # Get requirement-test relationships for this test
        req_tests_response = supabase.table("requirement_tests").select(
            "id, requirement_id"
        ).eq("test_id", test["id"]).execute()
        
        if not req_tests_response.data:
            # If no existing relationships, create a general test execution record
            # This might need adjustment based on your specific use case
            print("[execute_requirement_test] No requirement relationships found for test")
        
        # Update each requirement-test relationship with execution results
        requirements_updated = []
        
        for req_test in req_tests_response.data:
            update_data = {
                "execution_status": execution_data["status"],
                "result_notes": execution_data.get("notes", ""),
                "executed_at": current_time,
                "executed_by": execution_data.get("executed_by", "mcp-server"),
                "execution_environment": execution_data.get("environment", "test"),
                "execution_version": execution_data.get("version", "1.0"),
                "updated_at": current_time
            }
            
            # Add defects if any
            if execution_data.get("defects"):
                update_data["defects"] = execution_data["defects"]
            
            # Add evidence if any
            if execution_data.get("evidence"):
                update_data["evidence_artifacts"] = execution_data["evidence"]
            
            # Update the requirement test record
            update_response = supabase.table("requirement_tests").update(
                update_data
            ).eq("id", req_test["id"]).execute()
            
            if update_response.data:
                requirements_updated.append(req_test["requirement_id"])
        
        # Also update the test_req table status if needed
        test_update = {
            "status": _determine_test_status(execution_data["status"]),
            "result": execution_data.get("notes", ""),
            "updated_at": current_time
        }
        
        supabase.table("test_req").update(test_update).eq("id", test["id"]).execute()
        
        return {
            "success": True,
            "executed_at": current_time,
            "requirements_updated": requirements_updated
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to record test execution: {str(e)}"
        }

def _determine_test_status(execution_status: str) -> str:
    """Map execution status to test status"""
    status_mapping = {
        "passed": "passed",
        "failed": "failed", 
        "blocked": "blocked",
        "skipped": "skipped",
        "not_executed": "planned"
    }
    
    return status_mapping.get(execution_status, "active")

def _get_execution_summary(supabase, test: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """Get comprehensive execution summary"""
    try:
        # Get all executions for this test
        executions_response = supabase.table("requirement_tests").select(
            "execution_status, executed_at"
        ).eq("test_id", test["id"]).execute()
        
        executions = executions_response.data if executions_response.data else []
        
        # Calculate execution statistics
        total_executions = len(executions)
        status_counts = {}
        
        for execution in executions:
            status = execution.get("execution_status", "not_executed")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate success rate
        passed_count = status_counts.get("passed", 0)
        failed_count = status_counts.get("failed", 0)
        total_completed = passed_count + failed_count
        
        success_rate = (passed_count / total_completed * 100) if total_completed > 0 else 0
        
        return {
            "total_executions": total_executions,
            "execution_status_breakdown": status_counts,
            "success_rate_percentage": round(success_rate, 1),
            "last_execution_time": execution_result["executed_at"],
            "requirements_covered": len(execution_result.get("requirements_updated", []))
        }
        
    except Exception as e:
        print(f"Error getting execution summary: {str(e)}")
        return {
            "total_executions": 1,
            "success_rate_percentage": 100.0 if execution_result.get("requirements_updated") else 0,
            "last_execution_time": execution_result["executed_at"]
        }

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Execute test TEST-12345 with passed status in staging environment"
    result = execute_requirement_test_tool(test_org_id, test_message)
    print(f"Result: {result}")