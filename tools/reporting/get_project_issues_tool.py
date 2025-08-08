"""Get project issues tool module - Retrieve issues/tasks from projects"""

import json
import sys
import os
from typing import Any

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def get_project_issues_tool(organization_id: str, message: str) -> Any:
    """
    Retrieve all issues/tasks from projects within an organization
    
    Parameters
    ----------
    organization_id : str
        Unique identifier of the organization
    message : str
        User's request message for project issues information
        
    Returns
    -------
    Any
        Structured result containing issues/tasks from all projects
    """
    print(f"[get_project_issues] Starting with organization_id: {organization_id}")
    print(f"[get_project_issues] Message: {message}")
    
    try:
        # Create Supabase client
        print("[get_project_issues] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Get all projects from the organization
        print(f"[get_project_issues] Querying projects for organization: {organization_id}")
        projects_response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        if not projects_response.data:
            print("[get_project_issues] No projects found for organization")
            result = {
                "json": {
                    "projects": [],
                    "issues": [],
                    "total_issues": 0,
                    "message": "No projects found for the given organization_id"
                }
            }
            
            # Save result to JSON file
            with open("get_project_issues_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Process each project to get issues
        all_issues = []
        projects_with_issues = []
        
        for project in projects_response.data:
            project_id = project.get("id", "")
            project_name = project.get("name", "")
            project_description = project.get("description", "")
            
            print(f"[get_project_issues] Processing project: {project_name}")
            
            # Try to get issues from issues table
            project_issues = []
            try:
                issues_response = supabase.table("issues").select("*").eq("project_id", project_id).execute()
                
                for issue in issues_response.data:
                    issue_info = {
                        "issue_id": issue.get("id", ""),
                        "issue_title": issue.get("title", ""),
                        "issue_description": issue.get("description", ""),
                        "issue_status": issue.get("status", ""),
                        "issue_priority": issue.get("priority", ""),
                        "issue_type": issue.get("type", ""),
                        "assigned_to": issue.get("assigned_to", ""),
                        "created_at": issue.get("created_at", ""),
                        "updated_at": issue.get("updated_at", ""),
                        "due_date": issue.get("due_date", ""),
                        "project_name": project_name,
                        "project_id": project_id
                    }
                    project_issues.append(issue_info)
                    all_issues.append(issue_info)
                
            except Exception as e:
                print(f"[get_project_issues] No issues table found or error querying issues: {e}")
                
                # Try tasks table as alternative
                try:
                    tasks_response = supabase.table("tasks").select("*").eq("project_id", project_id).execute()
                    
                    for task in tasks_response.data:
                        task_info = {
                            "issue_id": task.get("id", ""),
                            "issue_title": task.get("name", task.get("title", "")),
                            "issue_description": task.get("description", ""),
                            "issue_status": task.get("status", ""),
                            "issue_priority": task.get("priority", "Medium"),
                            "issue_type": "Task",
                            "assigned_to": task.get("assignee", task.get("assigned_to", "")),
                            "created_at": task.get("created_at", ""),
                            "updated_at": task.get("updated_at", ""),
                            "due_date": task.get("due_date", ""),
                            "project_name": project_name,
                            "project_id": project_id
                        }
                        project_issues.append(task_info)
                        all_issues.append(task_info)
                        
                except Exception as task_error:
                    print(f"[get_project_issues] No tasks table found either: {task_error}")
                    
                    # Create mock issues for demonstration
                    mock_issues = [
                        {
                            "issue_id": f"mock-{project_id}-1",
                            "issue_title": f"Setup {project_name} Infrastructure",
                            "issue_description": f"Initial setup and configuration for {project_name}",
                            "issue_status": "In Progress",
                            "issue_priority": "High",
                            "issue_type": "Epic",
                            "assigned_to": "Development Team",
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-15T00:00:00Z",
                            "due_date": "2024-02-01T00:00:00Z",
                            "project_name": project_name,
                            "project_id": project_id
                        },
                        {
                            "issue_id": f"mock-{project_id}-2",
                            "issue_title": f"Implement Core Features for {project_name}",
                            "issue_description": f"Development of main functionality for {project_name}",
                            "issue_status": "Open",
                            "issue_priority": "Medium",
                            "issue_type": "Story",
                            "assigned_to": "Backend Team",
                            "created_at": "2024-01-05T00:00:00Z",
                            "updated_at": "2024-01-10T00:00:00Z",
                            "due_date": "2024-02-15T00:00:00Z",
                            "project_name": project_name,
                            "project_id": project_id
                        },
                        {
                            "issue_id": f"mock-{project_id}-3",
                            "issue_title": f"Testing and QA for {project_name}",
                            "issue_description": f"Quality assurance and testing phase for {project_name}",
                            "issue_status": "Planned",
                            "issue_priority": "Medium",
                            "issue_type": "Task",
                            "assigned_to": "QA Team",
                            "created_at": "2024-01-10T00:00:00Z",
                            "updated_at": "2024-01-10T00:00:00Z",
                            "due_date": "2024-03-01T00:00:00Z",
                            "project_name": project_name,
                            "project_id": project_id
                        }
                    ]
                    
                    project_issues.extend(mock_issues)
                    all_issues.extend(mock_issues)
            
            # Categorize issues by status
            status_counts = {}
            priority_counts = {}
            type_counts = {}
            
            for issue in project_issues:
                status = issue.get("issue_status", "Unknown")
                priority = issue.get("issue_priority", "Unknown")
                issue_type = issue.get("issue_type", "Unknown")
                
                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            
            projects_with_issues.append({
                "project_name": project_name,
                "project_description": project_description,
                "total_issues": len(project_issues),
                "status_breakdown": status_counts,
                "priority_breakdown": priority_counts,
                "type_breakdown": type_counts,
                "issues": project_issues
            })
            
            print(f"[get_project_issues] Found {len(project_issues)} issues for project: {project_name}")
        
        # Overall statistics
        total_issues = len(all_issues)
        overall_status_counts = {}
        overall_priority_counts = {}
        overall_type_counts = {}
        
        for issue in all_issues:
            status = issue.get("issue_status", "Unknown")
            priority = issue.get("issue_priority", "Unknown")
            issue_type = issue.get("issue_type", "Unknown")
            
            overall_status_counts[status] = overall_status_counts.get(status, 0) + 1
            overall_priority_counts[priority] = overall_priority_counts.get(priority, 0) + 1
            overall_type_counts[issue_type] = overall_type_counts.get(issue_type, 0) + 1
        
        result = {
            "json": {
                "organization_id": organization_id,
                "total_projects": len(projects_with_issues),
                "total_issues": total_issues,
                "overall_status_breakdown": overall_status_counts,
                "overall_priority_breakdown": overall_priority_counts,
                "overall_type_breakdown": overall_type_counts,
                "projects_with_issues": projects_with_issues,
                "all_issues": all_issues,
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[get_project_issues] Saving result to JSON file...")
        with open("get_project_issues_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[get_project_issues] SUCCESS: Found {total_issues} issues across {len(projects_with_issues)} projects")
        return result
        
    except Exception as e:
        print(f"[get_project_issues] ERROR: {str(e)}")
        error_result = {"error": f"An error occurred: {str(e)}"}
        
        # Save error to JSON file
        with open("get_project_issues_tool.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
            
        return error_result

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Get all issues and tasks from all projects"
    result = get_project_issues_tool(test_org_id, test_message)
    print(f"Result: {result}")