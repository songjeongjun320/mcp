"""Auto-generated tool module."""

import os
import json
from typing import Any
from supabase import create_client, Client

def pull_projects(organization_id: str, message: str) -> Any:
    """
    Call this tool if user want to check, list up or retrieve detailed information about our projects. It provides all projects's information, names, and descriptions.
    
    Parameters
    ----------
        organization_id (str): Unique identifier of the organization to pull project ids from database
        message (str): user's request message

    Returns
    -------
    Any
        Result of the tool.
    """
    try:
        # Create Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            return {"error": "Supabase credentials not found in environment variables"}
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Filter data from projects table by organization_id
        response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        if response.data:
            # Extract required information from response.data
            project_ids = [project.get("id", "") for project in response.data]
            project_names = [project.get("name", "") for project in response.data]
            project_descriptions = [project.get("description", "") for project in response.data]
            
            result = {
                "json": {
                    "project_ids": project_ids,
                    "project_names": project_names,
                    "project_descriptions": project_descriptions,
                    "message": message
                }
            }
            
            # Save result to JSON file
            with open("pull_projects_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        else:
            result = {
                "json": {
                    "project_ids": [],
                    "project_names": [],
                    "project_descriptions": [],
                    "message": "No projects found for the given organization_id"
                }
            }
            
            # Save result to JSON file
            with open("pull_projects_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            
            return result
            
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "List up all projects"
    result = pull_projects(test_org_id, test_message)
    print(f"Result: {result}")
