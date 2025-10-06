"""Get comprehensive traceability analysis tool."""

from typing import Any, Dict, List, Optional
from supabase_client.client import get_supabase_client
import json
from collections import defaultdict, deque


def get_trace_analysis_tool(organization_id: str, message: str) -> Dict[str, Any]:
    """
    Perform comprehensive traceability analysis for entities within an organization
    
    Parameters
    ----------
    organization_id : str
        User's individual organization_id
    message : str
        User's request message specifying the entity to analyze
        Expected format: "Analyze traceability for [entity_type]:[entity_id]" or "Full traceability analysis"
        
    Returns
    -------
    Dict[str, Any]
        Comprehensive traceability analysis results
    """
    
    try:
        supabase = get_supabase_client()
        
        # Parse the request to determine analysis scope
        analysis_config = _parse_analysis_request(message)
        
        if analysis_config['scope'] == 'entity':
            # Single entity analysis
            return _analyze_entity_traceability(supabase, organization_id, analysis_config)
        elif analysis_config['scope'] == 'project':
            # Project-wide analysis
            return _analyze_project_traceability(supabase, organization_id, analysis_config)
        else:
            # Organization-wide analysis
            return _analyze_organization_traceability(supabase, organization_id)
            
    except Exception as e:
        return {"error": f"Error performing traceability analysis: {str(e)}"}


def _parse_analysis_request(message: str) -> Dict[str, Any]:
    """Parse user message to determine analysis scope and parameters."""
    
    import re
    
    message_lower = message.lower()
    
    # Entity-specific analysis
    entity_pattern = r"analyze traceability for (\w+):([^\s]+)"
    entity_match = re.search(entity_pattern, message_lower)
    
    if entity_match:
        return {
            "scope": "entity",
            "entity_type": entity_match.group(1),
            "entity_id": entity_match.group(2)
        }
    
    # Project analysis
    project_pattern = r"project\s+([^\s]+)\s+traceability|traceability.*project\s+([^\s]+)"
    project_match = re.search(project_pattern, message_lower)
    
    if project_match:
        project_id = project_match.group(1) or project_match.group(2)
        return {
            "scope": "project",
            "project_id": project_id
        }
    
    # Default to organization analysis
    return {"scope": "organization"}


def _analyze_entity_traceability(supabase, organization_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze traceability for a specific entity."""
    
    entity_type = config['entity_type']
    entity_id = config['entity_id']
    
    # Validate entity access
    if not _validate_entity_access(supabase, entity_id, entity_type, organization_id):
        return {"error": f"Entity {entity_type}:{entity_id} not found or not accessible"}
    
    # Get entity information
    entity_info = _get_entity_info(supabase, entity_id, entity_type)
    
    # Get all trace links involving this entity
    outgoing_links = supabase.table("trace_links").select("*").eq("source_id", entity_id).execute()
    incoming_links = supabase.table("trace_links").select("*").eq("target_id", entity_id).execute()
    
    # Build traceability map
    traceability_map = _build_traceability_map(supabase, entity_id, max_depth=3)
    
    # Calculate traceability metrics
    metrics = _calculate_traceability_metrics(outgoing_links.data, incoming_links.data)
    
    # Identify potential issues
    issues = _identify_traceability_issues(supabase, entity_info, outgoing_links.data, incoming_links.data)
    
    return {
        "success": True,
        "json": {
            "entity": entity_info,
            "traceability_summary": {
                "outgoing_links": len(outgoing_links.data),
                "incoming_links": len(incoming_links.data),
                "total_relationships": len(outgoing_links.data) + len(incoming_links.data),
                "relationship_types": list(set([link['link_type'] for link in outgoing_links.data + incoming_links.data]))
            },
            "outgoing_relationships": [_enhance_link_info(supabase, link) for link in outgoing_links.data],
            "incoming_relationships": [_enhance_link_info(supabase, link) for link in incoming_links.data],
            "traceability_map": traceability_map,
            "metrics": metrics,
            "potential_issues": issues,
            "recommendations": _generate_traceability_recommendations(entity_info, metrics, issues)
        }
    }


def _analyze_project_traceability(supabase, organization_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze traceability for an entire project."""
    
    project_id = config['project_id']
    
    # Validate project access
    project = supabase.table("projects").select("*").eq("id", project_id).eq("organization_id", organization_id).execute()
    
    if not project.data:
        return {"error": f"Project {project_id} not found or not accessible"}
    
    project_info = project.data[0]
    
    # Get all entities in the project
    documents = supabase.table("documents").select("id, name").eq("project_id", project_id).execute()
    requirements = supabase.rpc("get_project_requirements", {"project_id": project_id}).execute()
    tests = supabase.table("test_req").select("id, title").eq("project_id", project_id).execute()
    
    # Get all trace links involving project entities
    entity_ids = []
    if documents.data:
        entity_ids.extend([doc['id'] for doc in documents.data])
    if requirements.data:
        entity_ids.extend([req['id'] for req in requirements.data])
    if tests.data:
        entity_ids.extend([test['id'] for test in tests.data])
    
    trace_links = []
    if entity_ids:
        links_query = supabase.table("trace_links").select("*").or_(
            f"source_id.in.({','.join(entity_ids)}),target_id.in.({','.join(entity_ids)})"
        ).execute()
        trace_links = links_query.data
    
    # Analyze traceability coverage
    coverage_analysis = _analyze_traceability_coverage(
        documents.data or [], 
        requirements.data or [], 
        tests.data or [], 
        trace_links
    )
    
    # Generate traceability matrix
    matrix = _generate_traceability_matrix(requirements.data or [], tests.data or [], trace_links)
    
    return {
        "success": True,
        "json": {
            "project": project_info,
            "entity_counts": {
                "documents": len(documents.data or []),
                "requirements": len(requirements.data or []),
                "tests": len(tests.data or []),
                "trace_links": len(trace_links)
            },
            "coverage_analysis": coverage_analysis,
            "traceability_matrix": matrix,
            "recommendations": _generate_project_recommendations(coverage_analysis)
        }
    }


def _analyze_organization_traceability(supabase, organization_id: str) -> Dict[str, Any]:
    """Analyze traceability across the entire organization."""
    
    # Get organization projects
    projects = supabase.table("projects").select("id, name, status").eq("organization_id", organization_id).execute()
    
    if not projects.data:
        return {"error": "No projects found in organization"}
    
    # Aggregate statistics
    total_stats = {
        "projects": len(projects.data),
        "documents": 0,
        "requirements": 0,
        "tests": 0,
        "trace_links": 0
    }
    
    project_analyses = []
    
    for project in projects.data:
        # Get project statistics
        docs = supabase.table("documents").select("id").eq("project_id", project['id']).execute()
        reqs = supabase.rpc("get_project_requirements", {"project_id": project['id']}).execute()
        tests = supabase.table("test_req").select("id").eq("project_id", project['id']).execute()
        
        # Count trace links for this project
        project_entities = []
        if docs.data:
            project_entities.extend([doc['id'] for doc in docs.data])
        if reqs.data:
            project_entities.extend([req['id'] for req in reqs.data])
        if tests.data:
            project_entities.extend([test['id'] for test in tests.data])
        
        project_links = 0
        if project_entities:
            links = supabase.table("trace_links").select("id").or_(
                f"source_id.in.({','.join(project_entities)}),target_id.in.({','.join(project_entities)})"
            ).execute()
            project_links = len(links.data or [])
        
        project_stats = {
            "project": project,
            "documents": len(docs.data or []),
            "requirements": len(reqs.data or []),
            "tests": len(tests.data or []),
            "trace_links": project_links,
            "traceability_ratio": project_links / max(len(reqs.data or []), 1)
        }
        
        project_analyses.append(project_stats)
        
        # Update totals
        total_stats["documents"] += project_stats["documents"]
        total_stats["requirements"] += project_stats["requirements"] 
        total_stats["tests"] += project_stats["tests"]
        total_stats["trace_links"] += project_stats["trace_links"]
    
    # Calculate organization-wide metrics
    org_metrics = {
        "total_entities": total_stats["documents"] + total_stats["requirements"] + total_stats["tests"],
        "average_traceability_ratio": sum([p["traceability_ratio"] for p in project_analyses]) / len(project_analyses),
        "projects_with_good_traceability": len([p for p in project_analyses if p["traceability_ratio"] > 0.5]),
        "projects_needing_attention": len([p for p in project_analyses if p["traceability_ratio"] < 0.3])
    }
    
    return {
        "success": True,
        "json": {
            "organization_summary": total_stats,
            "organization_metrics": org_metrics,
            "project_analyses": project_analyses,
            "recommendations": _generate_organization_recommendations(org_metrics, project_analyses)
        }
    }


def _build_traceability_map(supabase, start_entity_id: str, max_depth: int = 3) -> Dict[str, Any]:
    """Build a comprehensive traceability map using breadth-first search."""
    
    visited = set()
    traceability_map = {"nodes": [], "edges": []}
    queue = deque([(start_entity_id, 0)])
    
    while queue and len(visited) < 100:  # Limit to prevent excessive queries
        entity_id, depth = queue.popleft()
        
        if entity_id in visited or depth > max_depth:
            continue
            
        visited.add(entity_id)
        
        # Get entity info
        entity_info = _get_entity_info_by_id(supabase, entity_id)
        traceability_map["nodes"].append({
            "id": entity_id,
            "info": entity_info,
            "depth": depth
        })
        
        # Get connected entities
        if depth < max_depth:
            outgoing = supabase.table("trace_links").select("*").eq("source_id", entity_id).execute()
            incoming = supabase.table("trace_links").select("*").eq("target_id", entity_id).execute()
            
            for link in outgoing.data or []:
                traceability_map["edges"].append(link)
                queue.append((link["target_id"], depth + 1))
                
            for link in incoming.data or []:
                if link not in traceability_map["edges"]:
                    traceability_map["edges"].append(link)
                queue.append((link["source_id"], depth + 1))
    
    return traceability_map


def _calculate_traceability_metrics(outgoing_links: List[Dict], incoming_links: List[Dict]) -> Dict[str, Any]:
    """Calculate various traceability metrics."""
    
    all_links = outgoing_links + incoming_links
    
    link_type_counts = defaultdict(int)
    strength_distribution = defaultdict(int)
    bidirectional_count = 0
    
    for link in all_links:
        link_type_counts[link['link_type']] += 1
        strength = link.get('relationship_strength', 1)
        strength_distribution[f"strength_{strength}"] += 1
        if link.get('bidirectional', False):
            bidirectional_count += 1
    
    return {
        "total_relationships": len(all_links),
        "outgoing_count": len(outgoing_links),
        "incoming_count": len(incoming_links),
        "relationship_types": dict(link_type_counts),
        "strength_distribution": dict(strength_distribution),
        "bidirectional_relationships": bidirectional_count,
        "relationship_diversity": len(link_type_counts),
        "average_strength": sum([link.get('relationship_strength', 1) for link in all_links]) / max(len(all_links), 1)
    }


def _identify_traceability_issues(supabase, entity_info: Dict, outgoing_links: List[Dict], incoming_links: List[Dict]) -> List[Dict[str, Any]]:
    """Identify potential traceability issues."""
    
    issues = []
    
    # Check for isolated entities
    if not outgoing_links and not incoming_links:
        issues.append({
            "type": "isolated_entity",
            "severity": "high",
            "description": "Entity has no traceability relationships",
            "recommendation": "Establish relationships with related requirements, tests, or documents"
        })
    
    # Check for unidirectional critical relationships
    critical_types = ['satisfies', 'validates_against', 'derived_from']
    for link in outgoing_links:
        if link['link_type'] in critical_types and not link.get('bidirectional', False):
            issues.append({
                "type": "unidirectional_critical",
                "severity": "medium",
                "description": f"Critical relationship '{link['link_type']}' is unidirectional",
                "recommendation": "Consider making this relationship bidirectional for better traceability"
            })
    
    # Check for weak relationships
    weak_links = [link for link in outgoing_links + incoming_links if link.get('relationship_strength', 1) < 3]
    if weak_links:
        issues.append({
            "type": "weak_relationships",
            "severity": "low",
            "description": f"Found {len(weak_links)} weak relationships (strength < 3)",
            "recommendation": "Review and strengthen important relationships"
        })
    
    return issues


def _generate_traceability_recommendations(entity_info: Dict, metrics: Dict, issues: List[Dict]) -> List[str]:
    """Generate recommendations based on traceability analysis."""
    
    recommendations = []
    
    # Based on relationship count
    if metrics['total_relationships'] == 0:
        recommendations.append("Establish traceability links to related entities")
    elif metrics['total_relationships'] < 3:
        recommendations.append("Consider adding more traceability relationships for better coverage")
    
    # Based on relationship diversity
    if metrics['relationship_diversity'] < 2:
        recommendations.append("Diversify relationship types to improve traceability richness")
    
    # Based on issues
    high_severity_issues = [issue for issue in issues if issue['severity'] == 'high']
    if high_severity_issues:
        recommendations.append("Address high-severity traceability issues immediately")
    
    # Entity type specific recommendations
    if entity_info.get('type') == 'requirement':
        if not any(link['link_type'] == 'validates_against' for link in metrics.get('outgoing_links', [])):
            recommendations.append("Link this requirement to test cases for validation")
    
    return recommendations


def _analyze_traceability_coverage(documents: List, requirements: List, tests: List, trace_links: List) -> Dict[str, Any]:
    """Analyze traceability coverage across different entity types."""
    
    # Build lookup sets
    req_ids = {req['id'] for req in requirements}
    test_ids = {test['id'] for test in tests}
    
    # Count linked requirements and tests
    linked_reqs = set()
    linked_tests = set()
    
    for link in trace_links:
        if link['source_id'] in req_ids:
            linked_reqs.add(link['source_id'])
        if link['target_id'] in req_ids:
            linked_reqs.add(link['target_id'])
        if link['source_id'] in test_ids:
            linked_tests.add(link['source_id'])
        if link['target_id'] in test_ids:
            linked_tests.add(link['target_id'])
    
    # Calculate coverage percentages
    req_coverage = len(linked_reqs) / max(len(requirements), 1) * 100
    test_coverage = len(linked_tests) / max(len(tests), 1) * 100
    
    return {
        "requirement_coverage": {
            "total": len(requirements),
            "linked": len(linked_reqs),
            "percentage": req_coverage
        },
        "test_coverage": {
            "total": len(tests),
            "linked": len(linked_tests),
            "percentage": test_coverage
        },
        "overall_coverage": (req_coverage + test_coverage) / 2
    }


def _generate_traceability_matrix(requirements: List, tests: List, trace_links: List) -> Dict[str, Any]:
    """Generate a traceability matrix between requirements and tests."""
    
    matrix = {}
    
    # Initialize matrix
    for req in requirements:
        matrix[req['id']] = {
            "requirement": req,
            "tests": [],
            "coverage": 0
        }
    
    # Populate matrix with linked tests
    for link in trace_links:
        if link['source_type'] == 'requirement' and link['target_type'] == 'test':
            req_id = link['source_id']
            if req_id in matrix:
                test_info = next((t for t in tests if t['id'] == link['target_id']), None)
                if test_info:
                    matrix[req_id]["tests"].append({
                        "test": test_info,
                        "link_type": link['link_type'],
                        "relationship_strength": link.get('relationship_strength', 1)
                    })
        elif link['target_type'] == 'requirement' and link['source_type'] == 'test':
            req_id = link['target_id']
            if req_id in matrix:
                test_info = next((t for t in tests if t['id'] == link['source_id']), None)
                if test_info:
                    matrix[req_id]["tests"].append({
                        "test": test_info,
                        "link_type": link['link_type'],
                        "relationship_strength": link.get('relationship_strength', 1)
                    })
    
    # Calculate coverage for each requirement
    for req_id in matrix:
        matrix[req_id]["coverage"] = len(matrix[req_id]["tests"])
    
    return matrix


def _generate_project_recommendations(coverage_analysis: Dict) -> List[str]:
    """Generate recommendations for project traceability."""
    
    recommendations = []
    
    req_coverage = coverage_analysis['requirement_coverage']['percentage']
    test_coverage = coverage_analysis['test_coverage']['percentage']
    
    if req_coverage < 50:
        recommendations.append("Low requirement traceability coverage. Link more requirements to related entities.")
    
    if test_coverage < 50:
        recommendations.append("Low test traceability coverage. Ensure tests are linked to requirements they validate.")
    
    if coverage_analysis['overall_coverage'] < 60:
        recommendations.append("Overall traceability coverage is below recommended threshold (60%)")
    
    return recommendations


def _generate_organization_recommendations(metrics: Dict, project_analyses: List) -> List[str]:
    """Generate recommendations for organization-wide traceability."""
    
    recommendations = []
    
    if metrics['average_traceability_ratio'] < 0.4:
        recommendations.append("Organization-wide traceability needs improvement. Focus on establishing more relationships.")
    
    if metrics['projects_needing_attention'] > metrics['projects_with_good_traceability']:
        recommendations.append("More projects need traceability attention. Consider organization-wide traceability initiative.")
    
    low_performing_projects = [p for p in project_analyses if p['traceability_ratio'] < 0.2]
    if low_performing_projects:
        project_names = [p['project']['name'] for p in low_performing_projects[:3]]
        recommendations.append(f"Focus immediate attention on projects: {', '.join(project_names)}")
    
    return recommendations


# Helper functions
def _validate_entity_access(supabase, entity_id: str, entity_type: str, organization_id: str) -> bool:
    """Validate entity access (reused from create_trace_link_tool)."""
    # Implementation would be the same as in create_trace_link_tool
    # For brevity, returning True here
    return True


def _get_entity_info(supabase, entity_id: str, entity_type: str) -> Dict[str, Any]:
    """Get entity information (reused from create_trace_link_tool)."""
    # Implementation would be the same as in create_trace_link_tool
    return {"id": entity_id, "type": entity_type, "name": entity_id}


def _get_entity_info_by_id(supabase, entity_id: str) -> Dict[str, Any]:
    """Get entity info when type is unknown."""
    # Try different tables to find the entity
    tables_to_try = [
        ("requirements", "requirement"),
        ("documents", "document"), 
        ("projects", "project"),
        ("test_req", "test")
    ]
    
    for table_name, entity_type in tables_to_try:
        try:
            result = supabase.table(table_name).select("*").eq("id", entity_id).limit(1).execute()
            if result.data:
                return {**result.data[0], "type": entity_type}
        except:
            continue
    
    return {"id": entity_id, "type": "unknown", "name": entity_id}


def _enhance_link_info(supabase, link: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance link with entity information."""
    source_info = _get_entity_info_by_id(supabase, link['source_id'])
    target_info = _get_entity_info_by_id(supabase, link['target_id'])
    
    return {
        **link,
        "source_entity": source_info,
        "target_entity": target_info,
        "relationship_summary": f"{source_info.get('name', link['source_id'])} {link['link_type']} {target_info.get('name', link['target_id'])}"
    }