"""pull documents tool module"""

import json
import sys
import os
from typing import Any
from pull_projects_tool import pull_projects_tool

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def pull_documents_tool(organization_id: str, message: str) -> Any:
    print(f"[pull_documents] Starting with organization_id: {organization_id}")
    print(f"[pull_documents] Message: {message}")
    projects = pull_projects_tool(organization_id, message)
    print(f"[pull_documents] Pull_Projects: {projects}")
    

    try:
        # Create Supabase client
        print("[pull_documents] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Extract project_ids from projects response
        if "error" in projects:
            print(f"[pull_documents] Error from pull_projects_tool: {projects['error']}")
            return {"error": f"Failed to get projects: {projects['error']}"}
        
        project_ids = projects.get("json", {}).get("project_ids", [])
        print(f"[pull_documents] Found {len(project_ids)} project_ids: {project_ids}")
        
        if not project_ids:
            print("[pull_documents] No project_ids found")
            result = {
                "json": {
                    "documents": [],
                    "project_ids": [],
                    "message": "No project_ids found from projects"
                }
            }
            
            # Save empty result to JSON file
            print("[pull_documents] Saving empty result to JSON file...")
            with open("pull_documents_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Query documents table using the extracted project_ids
        print(f"[pull_documents] Querying documents table for project_ids: {project_ids}")
        documents_response = supabase.table("documents").select("id, project_id, name, description").in_("project_id", project_ids).execute()
        
        print(f"[pull_documents] Found {len(documents_response.data)} matching documents")
        
        # Extract document_ids for blocks query
        document_ids = [doc.get("id") for doc in documents_response.data if doc.get("id")]
        print(f"[pull_documents] Extracted {len(document_ids)} document_ids for blocks query")
        
        # Query blocks table using the extracted document_ids
        blocks_response = None
        if document_ids:
            print(f"[pull_documents] Querying blocks table for document_ids: {document_ids}")
            blocks_response = supabase.table("blocks").select("*").in_("document_id", document_ids).execute()
            print(f"[pull_documents] Found {len(blocks_response.data)} matching blocks")
        
        # Get project information from the projects response
        project_names = projects.get("json", {}).get("project_names", [])
        project_descriptions = projects.get("json", {}).get("project_descriptions", [])
        
        # Create a dictionary to map project_id to project info
        project_info = {}
        for i, project_id in enumerate(project_ids):
            project_info[project_id] = {
                "project_name": project_names[i] if i < len(project_names) else "",
                "project_description": project_descriptions[i] if i < len(project_descriptions) else ""
            }
        
        # Group blocks by document_id
        blocks_by_document = {}
        if blocks_response and blocks_response.data:
            for block in blocks_response.data:
                document_id = block.get("document_id")
                if document_id not in blocks_by_document:
                    blocks_by_document[document_id] = []
                blocks_by_document[document_id].append(block)
        
        # Group documents by project_id
        projects_with_documents = {}
        for doc in documents_response.data:
            project_id = doc.get("project_id")
            if project_id not in projects_with_documents:
                projects_with_documents[project_id] = {
                    "project_id": project_id,
                    "project_name": project_info.get(project_id, {}).get("project_name", ""),
                    "project_description": project_info.get(project_id, {}).get("project_description", ""),
                    "documents": []
                }
            
            # Add document to the project with blocks
            document_id = doc.get("id")
            document = {
                "document_id": document_id,
                "document_name": doc.get("name"),
                "document_description": doc.get("description"),
                "blocks": blocks_by_document.get(document_id, [])
            }
            projects_with_documents[project_id]["documents"].append(document)
        
        # Convert dictionary to list for better JSON structure
        structured_projects = list(projects_with_documents.values())
        
        # Calculate totals
        total_blocks = len(blocks_response.data) if blocks_response else 0
        
        # Return the structured data
        result = {
            "json": {
                "projects": structured_projects,
                "total_projects": len(structured_projects),
                "total_documents": len(documents_response.data),
                "total_blocks": total_blocks,
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[pull_documents] Saving result to JSON file...")
        with open("pull_documents_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("[pull_documents] SUCCESS: Completed successfully")
        return result

    except ValueError as e:
        print(f"[pull_documents] ERROR: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[pull_documents] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "List up all projects"
    result = pull_documents_tool(test_org_id, test_message)
    print(f"Result: {result}")
