"""Validate trace links tool module"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def validate_trace_links_tool(organization_id: str, message: str) -> Any:
    """
    Validate traceability links for integrity, consistency, and logical correctness.
    Identifies broken links, inconsistencies, and relationship validation issues.
    
    Parameters
    ----------
    organization_id : str
        User's individual organization ID
    message : str
        User's request message specifying validation scope and criteria
        
    Returns
    -------
    Any
        Result containing validation results, issues found, and recommendations
    """
    print(f"[validate_trace_links] Starting with organization_id: {organization_id}")
    print(f"[validate_trace_links] Message: {message}")
    
    try:
        # Create Supabase client
        print("[validate_trace_links] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Parse validation criteria from message
        validation_criteria = _parse_validation_criteria(message)
        
        print(f"[validate_trace_links] Validation criteria: {validation_criteria}")
        
        # Get organization projects for context
        projects_response = supabase.table("projects").select("id, name").eq("organization_id", organization_id).execute()
        
        if not projects_response.data:
            return {
                "json": {
                    "error": "No projects found for the organization",
                    "message": message
                }
            }
        
        # Perform comprehensive validation
        validation_result = _perform_trace_link_validation(supabase, organization_id, projects_response.data, validation_criteria)
        
        # Generate validation summary and recommendations
        summary = _generate_validation_summary(validation_result)
        recommendations = _generate_validation_recommendations(validation_result)
        
        result = {
            "json": {
                "organization_id": organization_id,
                "validation_timestamp": datetime.now().isoformat(),
                "projects_validated": len(projects_response.data),
                "validation_criteria": validation_criteria,
                "validation_results": validation_result,
                "summary": summary,
                "recommendations": recommendations,
                "overall_status": _determine_overall_status(validation_result),
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[validate_trace_links] Saving result to JSON file...")
        with open("validate_trace_links_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("[validate_trace_links] SUCCESS: Completed successfully")
        return result
        
    except Exception as e:
        print(f"[validate_trace_links] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def _parse_validation_criteria(message: str) -> Dict[str, Any]:
    """Parse message to determine validation criteria"""
    message_lower = message.lower()
    
    criteria = {
        "check_broken_links": True,
        "check_circular_dependencies": True,
        "check_logical_consistency": True,
        "check_entity_existence": True,
        "check_relationship_validity": True,
        "check_duplicate_links": True,
        "severity_threshold": "medium"
    }
    
    if "broken" in message_lower or "integrity" in message_lower:
        criteria["focus"] = "broken_links"
    elif "circular" in message_lower or "cycle" in message_lower:
        criteria["focus"] = "circular_dependencies"
    elif "logical" in message_lower or "consistency" in message_lower:
        criteria["focus"] = "logical_consistency"
    elif "duplicate" in message_lower:
        criteria["focus"] = "duplicates"
    
    if "critical" in message_lower or "high" in message_lower:
        criteria["severity_threshold"] = "high"
    elif "low" in message_lower or "minor" in message_lower:
        criteria["severity_threshold"] = "low"
    
    return criteria

def _perform_trace_link_validation(supabase, organization_id: str, projects: List[Dict], criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Perform comprehensive trace link validation"""
    
    validation_result = {
        "total_links_validated": 0,
        "broken_links": [],
        "circular_dependencies": [],
        "logical_inconsistencies": [],
        "duplicate_links": [],
        "orphaned_entities": [],
        "invalid_relationships": [],
        "statistics": {}
    }
    
    try:
        # Get all trace links for the organization
        trace_links = _get_organization_trace_links(supabase, organization_id)
        validation_result["total_links_validated"] = len(trace_links)
        
        print(f"[validate_trace_links] Validating {len(trace_links)} trace links")
        
        # Get all requirements for reference
        all_requirements = _get_organization_requirements(supabase, projects)
        
        # Validation 1: Check for broken links (entity existence)
        if criteria["check_entity_existence"]:
            validation_result["broken_links"] = _check_broken_links(supabase, trace_links, all_requirements)
        
        # Validation 2: Check for circular dependencies
        if criteria["check_circular_dependencies"]:
            validation_result["circular_dependencies"] = _check_circular_dependencies(trace_links)
        
        # Validation 3: Check logical consistency
        if criteria["check_logical_consistency"]:
            validation_result["logical_inconsistencies"] = _check_logical_consistency(trace_links, all_requirements)
        
        # Validation 4: Check for duplicate links
        if criteria["check_duplicate_links"]:
            validation_result["duplicate_links"] = _check_duplicate_links(trace_links)
        
        # Validation 5: Check relationship validity
        if criteria["check_relationship_validity"]:
            validation_result["invalid_relationships"] = _check_relationship_validity(trace_links, all_requirements)
        
        # Generate statistics
        validation_result["statistics"] = _generate_validation_statistics(validation_result)
        
        return validation_result
        
    except Exception as e:
        print(f"[validate_trace_links] Error in validation: {str(e)}")
        return {"error": f"Validation failed: {str(e)}"}

def _get_organization_trace_links(supabase, organization_id: str) -> List[Dict]:
    """Get all trace links for the organization"""
    try:
        trace_links_response = supabase.table("trace_links").select(
            "id, source_id, target_id, source_type, target_type, link_type, description, created_at, version"
        ).eq("is_deleted", False).execute()
        
        return trace_links_response.data if trace_links_response.data else []
        
    except Exception:
        return []

def _get_organization_requirements(supabase, projects: List[Dict]) -> Dict[str, Dict]:
    """Get all requirements for the organization indexed by ID"""
    requirements = {}
    
    try:
        for project in projects:
            # Get documents in project
            docs_response = supabase.table("documents").select("id, name").eq("project_id", project["id"]).execute()
            
            for doc in docs_response.data:
                # Get requirements in document
                reqs_response = supabase.table("requirements").select(
                    "id, name, description, status, priority, level, type, document_id"
                ).eq("document_id", doc["id"]).execute()
                
                for req in reqs_response.data:
                    req["project_name"] = project["name"]
                    req["document_name"] = doc["name"]
                    requirements[req["id"]] = req
        
        return requirements
        
    except Exception as e:
        print(f"Error getting requirements: {str(e)}")
        return {}

def _check_broken_links(supabase, trace_links: List[Dict], requirements: Dict[str, Dict]) -> List[Dict]:
    """Check for trace links pointing to non-existent entities"""
    broken_links = []
    
    for link in trace_links:
        issues = []
        
        # Check if source entity exists
        if link["source_type"] == "requirement" and link["source_id"] not in requirements:
            issues.append(f"Source requirement {link['source_id']} does not exist")
        
        # Check if target entity exists
        if link["target_type"] == "requirement" and link["target_id"] not in requirements:
            issues.append(f"Target requirement {link['target_id']} does not exist")
        
        if issues:
            broken_links.append({
                "link_id": link["id"],
                "source_id": link["source_id"],
                "target_id": link["target_id"],
                "link_type": link["link_type"],
                "issues": issues,
                "severity": "high"
            })
    
    return broken_links

def _check_circular_dependencies(trace_links: List[Dict]) -> List[Dict]:
    """Check for circular dependencies in trace links"""
    # Build directed graph
    graph = {}
    for link in trace_links:
        source = link["source_id"]
        target = link["target_id"]
        
        if source not in graph:
            graph[source] = []
        graph[source].append({"target": target, "link": link})
    
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs_check_cycle(node, path, link_path):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor_info in graph.get(node, []):
            neighbor = neighbor_info["target"]
            link = neighbor_info["link"]
            
            if neighbor not in visited:
                result = dfs_check_cycle(neighbor, path + [node], link_path + [link])
                if result:
                    return result
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycle_path = path[cycle_start:] + [node, neighbor]
                cycle_links = link_path[cycle_start:] + [link]
                
                return {
                    "cycle_path": cycle_path,
                    "cycle_links": [{"id": l["id"], "type": l["link_type"]} for l in cycle_links],
                    "severity": "medium"
                }
        
        rec_stack.remove(node)
        return None
    
    # Check for cycles starting from each unvisited node
    for node in graph:
        if node not in visited:
            cycle = dfs_check_cycle(node, [], [])
            if cycle:
                cycles.append(cycle)
    
    return cycles

def _check_logical_consistency(trace_links: List[Dict], requirements: Dict[str, Dict]) -> List[Dict]:
    """Check for logical inconsistencies in trace relationships"""
    inconsistencies = []
    
    # Group links by source-target pairs
    link_groups = {}
    for link in trace_links:
        key = f"{link['source_id']}-{link['target_id']}"
        if key not in link_groups:
            link_groups[key] = []
        link_groups[key].append(link)
    
    # Check for conflicting relationships
    for key, links in link_groups.items():
        if len(links) > 1:
            link_types = [link["link_type"] for link in links]
            
            # Check for conflicting link types
            conflicting_pairs = [
                ("satisfies", "conflicts_with"),
                ("derived_from", "conflicts_with"),
                ("refines", "conflicts_with")
            ]
            
            for type1, type2 in conflicting_pairs:
                if type1 in link_types and type2 in link_types:
                    inconsistencies.append({
                        "source_id": links[0]["source_id"],
                        "target_id": links[0]["target_id"],
                        "conflicting_types": [type1, type2],
                        "link_ids": [link["id"] for link in links if link["link_type"] in [type1, type2]],
                        "severity": "high",
                        "issue": f"Conflicting relationship types: {type1} and {type2}"
                    })
    
    # Check for invalid hierarchical relationships
    for link in trace_links:
        if link["source_type"] == "requirement" and link["target_type"] == "requirement":
            source_req = requirements.get(link["source_id"])
            target_req = requirements.get(link["target_id"])
            
            if source_req and target_req:
                source_level = source_req.get("level", "")
                target_level = target_req.get("level", "")
                
                # Check if "derived_from" goes from lower to higher level appropriately
                if link["link_type"] == "derived_from":
                    level_hierarchy = ["system", "component", "feature", "detail"]
                    if (source_level in level_hierarchy and target_level in level_hierarchy):
                        source_idx = level_hierarchy.index(source_level)
                        target_idx = level_hierarchy.index(target_level)
                        
                        if source_idx <= target_idx:  # Should derive from higher level
                            inconsistencies.append({
                                "link_id": link["id"],
                                "source_id": link["source_id"],
                                "target_id": link["target_id"],
                                "issue": f"Invalid derivation: {source_level} level deriving from {target_level} level",
                                "severity": "medium"
                            })
    
    return inconsistencies

def _check_duplicate_links(trace_links: List[Dict]) -> List[Dict]:
    """Check for duplicate trace links"""
    seen_links = {}
    duplicates = []
    
    for link in trace_links:
        # Create a key based on source, target, and link type
        key = f"{link['source_id']}-{link['target_id']}-{link['link_type']}"
        
        if key in seen_links:
            duplicates.append({
                "original_link_id": seen_links[key]["id"],
                "duplicate_link_id": link["id"],
                "source_id": link["source_id"],
                "target_id": link["target_id"],
                "link_type": link["link_type"],
                "severity": "low"
            })
        else:
            seen_links[key] = link
    
    return duplicates

def _check_relationship_validity(trace_links: List[Dict], requirements: Dict[str, Dict]) -> List[Dict]:
    """Check for invalid relationship types based on entity characteristics"""
    invalid_relationships = []
    
    # Define valid relationship matrix
    valid_relationships = {
        "requirement": {
            "requirement": ["satisfies", "derived_from", "refines", "conflicts_with", "depends_on"],
            "test": ["validates", "tests"],
            "document": ["documented_in"]
        }
    }
    
    for link in trace_links:
        source_type = link["source_type"]
        target_type = link["target_type"]
        link_type = link["link_type"]
        
        # Check if relationship type is valid for entity types
        if source_type in valid_relationships:
            if target_type in valid_relationships[source_type]:
                if link_type not in valid_relationships[source_type][target_type]:
                    invalid_relationships.append({
                        "link_id": link["id"],
                        "source_id": link["source_id"],
                        "target_id": link["target_id"],
                        "source_type": source_type,
                        "target_type": target_type,
                        "link_type": link_type,
                        "issue": f"Invalid relationship type '{link_type}' between {source_type} and {target_type}",
                        "severity": "medium",
                        "valid_types": valid_relationships[source_type][target_type]
                    })
    
    return invalid_relationships

def _generate_validation_statistics(validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate validation statistics"""
    stats = {
        "total_issues": 0,
        "issues_by_severity": {"high": 0, "medium": 0, "low": 0},
        "issues_by_type": {}
    }
    
    # Count issues by type and severity
    issue_types = [
        ("broken_links", "Broken Links"),
        ("circular_dependencies", "Circular Dependencies"), 
        ("logical_inconsistencies", "Logical Inconsistencies"),
        ("duplicate_links", "Duplicate Links"),
        ("invalid_relationships", "Invalid Relationships")
    ]
    
    for key, display_name in issue_types:
        issues = validation_result.get(key, [])
        count = len(issues)
        stats["issues_by_type"][display_name] = count
        stats["total_issues"] += count
        
        # Count by severity
        for issue in issues:
            severity = issue.get("severity", "medium")
            stats["issues_by_severity"][severity] += 1
    
    # Calculate health score (0-100)
    total_links = validation_result.get("total_links_validated", 1)
    health_score = max(0, 100 - (stats["total_issues"] / total_links * 100))
    stats["health_score"] = round(health_score, 1)
    
    return stats

def _generate_validation_summary(validation_result: Dict[str, Any]) -> Dict[str, str]:
    """Generate human-readable validation summary"""
    stats = validation_result.get("statistics", {})
    
    summary = {}
    
    total_links = validation_result.get("total_links_validated", 0)
    total_issues = stats.get("total_issues", 0)
    health_score = stats.get("health_score", 0)
    
    summary["overall"] = f"Validated {total_links} trace links with {total_issues} issues found. Health score: {health_score}%"
    
    # Specific issue summaries
    if validation_result.get("broken_links"):
        summary["broken_links"] = f"Found {len(validation_result['broken_links'])} broken links pointing to non-existent entities"
    
    if validation_result.get("circular_dependencies"):
        summary["circular_dependencies"] = f"Detected {len(validation_result['circular_dependencies'])} circular dependency chains"
    
    if validation_result.get("logical_inconsistencies"):
        summary["logical_inconsistencies"] = f"Identified {len(validation_result['logical_inconsistencies'])} logical inconsistencies"
    
    return summary

def _generate_validation_recommendations(validation_result: Dict[str, Any]) -> List[str]:
    """Generate actionable validation recommendations"""
    recommendations = []
    
    stats = validation_result.get("statistics", {})
    
    # Health score based recommendations
    health_score = stats.get("health_score", 100)
    
    if health_score < 70:
        recommendations.append("Critical: Low trace link health score. Immediate attention required for data integrity.")
    elif health_score < 85:
        recommendations.append("Warning: Moderate trace link issues detected. Consider cleanup activities.")
    
    # Specific issue recommendations
    if validation_result.get("broken_links"):
        recommendations.append("Fix broken links by either removing invalid links or creating missing entities.")
    
    if validation_result.get("circular_dependencies"):
        recommendations.append("Resolve circular dependencies by reviewing and restructuring trace link relationships.")
    
    if validation_result.get("logical_inconsistencies"):
        recommendations.append("Address logical inconsistencies by reviewing conflicting relationship types.")
    
    if validation_result.get("duplicate_links"):
        recommendations.append("Remove duplicate trace links to improve data quality and performance.")
    
    if validation_result.get("invalid_relationships"):
        recommendations.append("Update invalid relationship types to use appropriate trace link types for entity combinations.")
    
    # General recommendations
    if stats.get("total_issues", 0) > 0:
        recommendations.append("Implement regular trace link validation as part of quality assurance processes.")
        recommendations.append("Consider establishing trace link governance policies to prevent future issues.")
    
    return recommendations

def _determine_overall_status(validation_result: Dict[str, Any]) -> str:
    """Determine overall validation status"""
    stats = validation_result.get("statistics", {})
    health_score = stats.get("health_score", 100)
    high_severity_issues = stats.get("issues_by_severity", {}).get("high", 0)
    
    if high_severity_issues > 0:
        return "CRITICAL"
    elif health_score < 70:
        return "WARNING"
    elif health_score < 90:
        return "NEEDS_ATTENTION"
    else:
        return "HEALTHY"

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Validate all trace links for integrity and consistency"
    result = validate_trace_links_tool(test_org_id, test_message)
    print(f"Result: {result}")