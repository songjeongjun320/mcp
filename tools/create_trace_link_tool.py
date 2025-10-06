"""Create trace link tool for establishing relationships between entities."""

from typing import Any, Dict, List, Optional
from supabase_client.client import get_supabase_client
import json
import uuid
from datetime import datetime


def create_trace_link_tool(organization_id: str, message: str) -> Dict[str, Any]:
    """
    Create traceability links between entities (requirements, documents, tests, etc.)
    
    Parameters
    ----------
    organization_id : str
        User's individual organization_id
    message : str
        User's request message containing trace link details
        Expected format: Create trace link from [source_type]:[source_id] to [target_type]:[target_id] with relationship [link_type]
        
    Returns
    -------
    Dict[str, Any]
        Result containing the created trace link information
    """
    
    try:
        supabase = get_supabase_client()
        
        # Parse the message to extract trace link parameters
        link_data = _parse_trace_link_message(message)
        
        if not link_data:
            return {
                "error": "Could not parse trace link request. Please provide source entity, target entity, and link type.",
                "example": "Create trace link from requirement:req-123 to test:test-456 with relationship validates"
            }
        
        # Validate entities exist and belong to the organization
        source_valid = _validate_entity_access(supabase, link_data['source_id'], link_data['source_type'], organization_id)
        target_valid = _validate_entity_access(supabase, link_data['target_id'], link_data['target_type'], organization_id)
        
        if not source_valid:
            return {"error": f"Source entity {link_data['source_type']}:{link_data['source_id']} not found or not accessible"}
        
        if not target_valid:
            return {"error": f"Target entity {link_data['target_type']}:{link_data['target_id']} not found or not accessible"}
        
        # Check if link already exists
        existing_link = supabase.table("trace_links").select("*").eq(
            "source_id", link_data['source_id']
        ).eq(
            "target_id", link_data['target_id']
        ).eq(
            "source_type", link_data['source_type']
        ).eq(
            "target_type", link_data['target_type']
        ).eq(
            "link_type", link_data['link_type']
        ).execute()
        
        if existing_link.data:
            return {
                "warning": "Trace link already exists",
                "existing_link": existing_link.data[0]
            }
        
        # Create the trace link
        new_link_data = {
            "id": str(uuid.uuid4()),
            "source_id": link_data['source_id'],
            "target_id": link_data['target_id'],
            "source_type": link_data['source_type'],
            "target_type": link_data['target_type'],
            "link_type": link_data['link_type'],
            "description": link_data.get('description', ''),
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "relationship_strength": link_data.get('strength', 5),
            "bidirectional": link_data.get('bidirectional', False),
            "custom_properties": link_data.get('properties', {})
        }
        
        result = supabase.table("trace_links").insert(new_link_data).execute()
        
        if result.data:
            # Get enhanced information about the created link
            enhanced_result = _get_enhanced_link_info(supabase, result.data[0])
            
            return {
                "success": True,
                "message": f"Trace link created successfully",
                "json": {
                    "trace_link": enhanced_result,
                    "relationship": f"{link_data['source_type']} {link_data['link_type']} {link_data['target_type']}"
                }
            }
        else:
            return {"error": "Failed to create trace link"}
            
    except Exception as e:
        return {"error": f"Error creating trace link: {str(e)}"}


def _parse_trace_link_message(message: str) -> Optional[Dict[str, Any]]:
    """Parse user message to extract trace link parameters."""
    
    # Common patterns in user messages
    import re
    
    # Pattern 1: "Create trace link from [source_type]:[source_id] to [target_type]:[target_id] with relationship [link_type]"
    pattern1 = r"from\s+(\w+):([^\\s]+)\s+to\s+(\w+):([^\\s]+)\s+with\s+relationship\s+(\w+)"
    match1 = re.search(pattern1, message, re.IGNORECASE)
    
    if match1:
        return {
            "source_type": match1.group(1),
            "source_id": match1.group(2),
            "target_type": match1.group(3),
            "target_id": match1.group(4),
            "link_type": match1.group(5),
            "description": f"Link created from user request: {message}"
        }
    
    # Pattern 2: Simple format "requirement req-123 satisfies test test-456"
    pattern2 = r"(\w+)\s+([^\\s]+)\s+(\w+)\s+(\w+)\s+([^\\s]+)"
    match2 = re.search(pattern2, message, re.IGNORECASE)
    
    if match2:
        return {
            "source_type": match2.group(1),
            "source_id": match2.group(2),
            "link_type": match2.group(3),
            "target_type": match2.group(4),
            "target_id": match2.group(5),
            "description": f"Link created from user request: {message}"
        }
    
    # Try to extract JSON if present
    try:
        # Look for JSON in the message
        import json
        json_start = message.find('{')
        json_end = message.rfind('}')
        if json_start >= 0 and json_end > json_start:
            json_str = message[json_start:json_end+1]
            parsed = json.loads(json_str)
            
            if all(key in parsed for key in ['source_type', 'source_id', 'target_type', 'target_id', 'link_type']):
                return parsed
    except:
        pass
    
    return None


def _validate_entity_access(supabase, entity_id: str, entity_type: str, organization_id: str) -> bool:
    """Validate that the entity exists and is accessible to the organization."""
    
    try:
        if entity_type == 'requirement':
            # Check through documents -> projects -> organizations
            result = supabase.table("requirements").select(
                "id, document_id, documents(project_id, projects(organization_id))"
            ).eq("id", entity_id).execute()
            
            if result.data:
                req_org_id = result.data[0]['documents']['projects']['organization_id']
                return req_org_id == organization_id
                
        elif entity_type == 'document':
            result = supabase.table("documents").select(
                "id, project_id, projects(organization_id)"
            ).eq("id", entity_id).execute()
            
            if result.data:
                doc_org_id = result.data[0]['projects']['organization_id']
                return doc_org_id == organization_id
                
        elif entity_type == 'project':
            result = supabase.table("projects").select(
                "id, organization_id"
            ).eq("id", entity_id).eq("organization_id", organization_id).execute()
            
            return len(result.data) > 0
            
        elif entity_type == 'test':
            result = supabase.table("test_req").select(
                "id, project_id, projects(organization_id)"
            ).eq("id", entity_id).execute()
            
            if result.data:
                test_org_id = result.data[0]['projects']['organization_id']
                return test_org_id == organization_id
                
        return False
        
    except Exception:
        return False


def _get_enhanced_link_info(supabase, link_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get enhanced information about the trace link including entity details."""
    
    try:
        # Get source entity info
        source_info = _get_entity_info(supabase, link_data['source_id'], link_data['source_type'])
        target_info = _get_entity_info(supabase, link_data['target_id'], link_data['target_type'])
        
        return {
            **link_data,
            "source_entity": source_info,
            "target_entity": target_info,
            "relationship_summary": f"{source_info.get('name', link_data['source_id'])} {link_data['link_type']} {target_info.get('name', link_data['target_id'])}"
        }
        
    except Exception:
        return link_data


def _get_entity_info(supabase, entity_id: str, entity_type: str) -> Dict[str, Any]:
    """Get basic information about an entity."""
    
    try:
        if entity_type == 'requirement':
            result = supabase.table("requirements").select("id, name, description, status").eq("id", entity_id).execute()
        elif entity_type == 'document':
            result = supabase.table("documents").select("id, name, description").eq("id", entity_id).execute()
        elif entity_type == 'project':
            result = supabase.table("projects").select("id, name, description, status").eq("id", entity_id).execute()
        elif entity_type == 'test':
            result = supabase.table("test_req").select("id, title, description, status").eq("id", entity_id).execute()
            if result.data:
                # Normalize test data to match other entities
                test_data = result.data[0]
                return {
                    "id": test_data["id"],
                    "name": test_data["title"],
                    "description": test_data["description"],
                    "status": test_data["status"],
                    "type": entity_type
                }
        else:
            return {"id": entity_id, "type": entity_type, "name": entity_id}
        
        if result.data:
            return {**result.data[0], "type": entity_type}
        else:
            return {"id": entity_id, "type": entity_type, "name": entity_id}
            
    except Exception:
        return {"id": entity_id, "type": entity_type, "name": entity_id}


# Valid entity types for trace links
VALID_ENTITY_TYPES = [
    'requirement', 'test', 'document', 'project', 'assignment', 'diagram',
    'document_block', 'requirement_field', 'specification_section', 
    'implementation_component', 'validation_criteria'
]

# Valid link types
VALID_LINK_TYPES = [
    'derived_from', 'satisfies', 'conflicts_with', 'depends_on',
    'parent_document', 'child_document', 'sibling_document', 
    'references_block', 'implements_spec', 'inherits_from',
    'complements', 'alternative_to', 'synchronizes_with',
    'validates_against', 'derives_requirement', 'realizes_design'
]