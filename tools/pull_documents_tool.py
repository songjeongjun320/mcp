"""pull documents tool module"""

import json
import sys
import os
from typing import Any
# Add parent directory to sys.path to import local supabase module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from supabase_client.client import get_supabase_client
from pull_projects_tool import pull_projects_tool

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
            blocks_response = supabase.table("blocks").select("id, document_id, position, content, type").in_("document_id", document_ids).execute()
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
        
        # Find table blocks first
        table_blocks = []
        if blocks_response and blocks_response.data:
            for block in blocks_response.data:
                if block.get("type") == "table":
                    table_blocks.append(block.get("id"))
        
        # Query requirements and group by block_id
        requirements_by_block_id = {}
        if table_blocks:
            print(f"[pull_documents] Found {len(table_blocks)} table blocks, querying requirements table...")
            requirements_response = supabase.table("requirements").select("*").in_("document_id", document_ids).execute()
            print(f"[pull_documents] Found {len(requirements_response.data)} requirements")
            
            # Filter out unwanted keys and group by block_id
            excluded_keys = {
                "format", "level", "tags", "position", "type", "original_requirement",
                "enchanced_requirement", "ai_analysis", "created_at", "updated_at",
                "created_by", "updated_by", "version", "is_deleted", "deleted_at",
                "deleted_by", "properties"
            }
            
            for req in requirements_response.data:
                block_id = req.get("block_id")
                if block_id:
                    if block_id not in requirements_by_block_id:
                        requirements_by_block_id[block_id] = []
                    
                    # Filter out excluded keys
                    filtered_req = {k: v for k, v in req.items() if k not in excluded_keys}
                    requirements_by_block_id[block_id].append(filtered_req)
        
        # Group blocks by document_id and filter required fields
        blocks_by_document = {}
        if blocks_response and blocks_response.data:
            for block in blocks_response.data:
                document_id = block.get("document_id")
                block_id = block.get("id")
                
                if document_id not in blocks_by_document:
                    blocks_by_document[document_id] = []
                
                # Only include required fields
                filtered_block = {
                    "id": block_id,
                    "type": block.get("type"),
                    "position": block.get("position"),
                    "content": block.get("content")
                }
                
                # Add requirements to block if they exist for this block_id
                if block_id in requirements_by_block_id:
                    filtered_block["requirements"] = requirements_by_block_id[block_id]
                
                blocks_by_document[document_id].append(filtered_block)
        
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
            
            # Add document to the project with filtered blocks
            document_id = doc.get("id")
            raw_blocks = blocks_by_document.get(document_id, [])
            
            # Filter out empty blocks
            filtered_blocks = []
            for block in raw_blocks:
                block_type = block.get("type")
                content = block.get("content")
                
                # Skip table blocks with empty requirements
                if block_type == "table":
                    requirements = block.get("requirements", [])
                    if not requirements:  # Empty list
                        continue
                
                # Skip text blocks with empty text content
                if block_type == "text":
                    if isinstance(content, dict) and content.get("text") == "":
                        continue
                    elif isinstance(content, str) and content.strip() == "":
                        continue
                
                # Keep this block
                filtered_blocks.append(block)
            
            # Create human-readable blocks without IDs and positions
            clean_blocks = []
            for block in filtered_blocks:
                clean_block = {}
                
                # Extract content and flatten it
                content = block.get("content")
                if content:
                    # If content is a dict, extract its values and flatten
                    if isinstance(content, dict):
                        for key, value in content.items():
                            if value is not None and value != "":
                                # Remove format only if both text and format exist
                                if key == "format" and "text" in content:
                                    continue  # Skip format field
                                clean_block[key] = value
                    else:
                        # If content is a string or other type, use it directly
                        clean_block["text"] = content
                
                # Add requirements if they exist, but clean them too
                if "requirements" in block:
                    clean_requirements = []
                    for req in block["requirements"]:
                        clean_req = {}
                        # Remove technical keys
                        excluded_keys = {"id", "document_id", "block_id", "project_id", "type", "position", "format"}
                        for key, value in req.items():
                            if key not in excluded_keys and value is not None and value != "":
                                clean_req[key] = value
                        if clean_req:
                            clean_requirements.append(clean_req)
                    
                    if clean_requirements:
                        clean_block["requirements"] = clean_requirements
                
                if clean_block:
                    clean_blocks.append(clean_block)
            
            # Only include document if it has meaningful content
            if clean_blocks or doc.get("description"):
                clean_document = {}
                if doc.get("name"):
                    clean_document["name"] = doc.get("name")
                if doc.get("description"):
                    clean_document["description"] = doc.get("description")
                if clean_blocks:
                    clean_document["content"] = clean_blocks
                
                if clean_document:
                    projects_with_documents[project_id]["documents"].append(clean_document)
        
        # Create clean project structure
        clean_projects = []
        for project_data in projects_with_documents.values():
            if project_data["documents"]:
                clean_project = {}
                if project_data.get("project_name"):
                    clean_project["name"] = project_data["project_name"]
                if project_data.get("project_description"):
                    clean_project["description"] = project_data["project_description"]
                if project_data["documents"]:
                    clean_project["documents"] = project_data["documents"]
                
                if clean_project:
                    clean_projects.append(clean_project)
        
        # Return clean structured data
        result = {
            "json": {
                "projects": clean_projects
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
