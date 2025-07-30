"""Auto-generated tool module."""

import json
import sys
import os
from typing import Any

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def pull_projects_tool(organization_id: str, message: str) -> Any:
    print(f"[pull_projects] Starting with organization_id: {organization_id}")
    print(f"[pull_projects] Message: {message}")
    
    try:
        # Create Supabase client
        print("[pull_projects] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Filter data from projects table by organization_id
        print(f"[pull_projects] Querying projects table for organization_id: {organization_id}")
        response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        print(f"[pull_projects] Query executed. Found {len(response.data)} projects")
        
        if response.data:
            print("[pull_projects] Processing project data...")
            # Extract required information from response.data
            project_ids = [project.get("id", "") for project in response.data]
            project_names = [project.get("name", "") for project in response.data]
            project_descriptions = [project.get("description", "") for project in response.data]
            
            print(f"[pull_projects] Extracted {len(project_ids)} project IDs")
            
            result = {
                "json": {
                    "project_ids": project_ids,
                    "project_names": project_names,
                    "project_descriptions": project_descriptions,
                    "message": message
                }
            }
            
            # Save result to JSON file
            print("[pull_projects] Saving result to JSON file...")
            with open("pull_projects_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("[pull_projects] SUCCESS: Completed successfully")
            return result
        else:
            print("[pull_projects] No projects found for the given organization_id")
            result = {
                "json": {
                    "project_ids": [],
                    "project_names": [],
                    "project_descriptions": [],
                    "message": "No projects found for the given organization_id"
                }
            }
            
            # Save result to JSON file
            print("[pull_projects] Saving empty result to JSON file...")
            with open("pull_projects_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            
            print("[pull_projects] COMPLETED: No projects found")
            return result
            
    except ValueError as e:
        print(f"[pull_projects] ERROR: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[pull_projects] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "List up all projects"
    result = pull_projects_tool(test_org_id, test_message)
    print(f"Result: {result}")
