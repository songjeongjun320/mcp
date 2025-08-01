"""Get documents by projects tool module"""

import json
import sys
import os
from typing import Any

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def get_documents_by_projects_tool(organization_id: str, message: str) -> Any:
    """
    Get documents from specific projects within an organization
    
    Parameters
    ----------
    organization_id : str
        Unique identifier of the organization
    message : str
        User's request message containing project specifications
        
    Returns
    -------
    Any
        Structured result containing documents from specified projects
    """
    print(f"[get_documents_by_projects] Starting with organization_id: {organization_id}")
    print(f"[get_documents_by_projects] Message: {message}")
    
    try:
        # Create Supabase client
        print("[get_documents_by_projects] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # First, get all projects from the organization
        print(f"[get_documents_by_projects] Querying projects for organization: {organization_id}")
        projects_response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        if not projects_response.data:
            print("[get_documents_by_projects] No projects found for organization")
            result = {
                "json": {
                    "projects": [],
                    "documents": [],
                    "message": "No projects found for the given organization_id"
                }
            }
            
            # Save result to JSON file
            with open("get_documents_by_projects_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Extract project IDs
        project_ids = [project.get("id", "") for project in projects_response.data]
        print(f"[get_documents_by_projects] Found {len(project_ids)} projects")
        
        # Get documents for all projects
        all_documents = []
        projects_with_docs = []
        
        for project in projects_response.data:
            project_id = project.get("id", "")
            project_name = project.get("name", "")
            project_description = project.get("description", "")
            
            print(f"[get_documents_by_projects] Querying documents for project: {project_name}")
            
            # Query documents for this project
            docs_response = supabase.table("documents").select("*").eq("project_id", project_id).execute()
            
            project_documents = []
            for doc in docs_response.data:
                doc_info = {
                    "document_name": doc.get("name", ""),
                    "document_description": doc.get("description", ""),
                    "document_type": doc.get("type", ""),
                    "created_at": doc.get("created_at", ""),
                    "updated_at": doc.get("updated_at", "")
                }
                project_documents.append(doc_info)
                all_documents.append({
                    **doc_info,
                    "project_name": project_name,
                    "project_id": project_id
                })
            
            projects_with_docs.append({
                "project_name": project_name,
                "project_description": project_description,
                "document_count": len(project_documents),
                "documents": project_documents
            })
            
            print(f"[get_documents_by_projects] Found {len(project_documents)} documents for project: {project_name}")
        
        result = {
            "json": {
                "organization_id": organization_id,
                "total_projects": len(projects_with_docs),
                "total_documents": len(all_documents),
                "projects": projects_with_docs,
                "all_documents": all_documents,
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[get_documents_by_projects] Saving result to JSON file...")
        with open("get_documents_by_projects_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[get_documents_by_projects] SUCCESS: Found {len(all_documents)} documents across {len(projects_with_docs)} projects")
        return result
        
    except Exception as e:
        print(f"[get_documents_by_projects] ERROR: {str(e)}")
        error_result = {"error": f"An error occurred: {str(e)}"}
        
        # Save error to JSON file
        with open("get_documents_by_projects_tool.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
            
        return error_result

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Get all documents from all projects in this organization"
    result = get_documents_by_projects_tool(test_org_id, test_message)
    print(f"Result: {result}")