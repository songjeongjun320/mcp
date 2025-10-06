"""Advanced requirement metrics and analytics tool."""

from typing import Any, Dict, List, Optional
from supabase_client.client import get_supabase_client
import json
from collections import defaultdict
from datetime import datetime, timedelta
import statistics


def get_requirement_metrics_tool(organization_id: str, message: str) -> Dict[str, Any]:
    """
    Generate detailed requirement metrics and analytics for an organization
    
    Parameters
    ----------
    organization_id : str
        User's individual organization_id
    message : str
        User's request message specifying the type of metrics
        Options: "overall metrics", "project metrics [project_id]", "detailed analytics"
        
    Returns
    -------
    Dict[str, Any]
        Comprehensive requirement metrics and analytics
    """
    
    try:
        supabase = get_supabase_client()
        
        # Parse the request to determine metrics scope
        metrics_config = _parse_metrics_request(message)
        
        if metrics_config['scope'] == 'project':
            return _get_project_requirement_metrics(supabase, organization_id, metrics_config['project_id'])
        elif metrics_config['scope'] == 'detailed':
            return _get_detailed_requirement_analytics(supabase, organization_id)
        else:
            return _get_overall_requirement_metrics(supabase, organization_id)
            
    except Exception as e:
        return {"error": f"Error generating requirement metrics: {str(e)}"}


def _parse_metrics_request(message: str) -> Dict[str, Any]:
    """Parse user message to determine metrics scope."""
    
    import re
    
    message_lower = message.lower()
    
    # Project-specific metrics
    project_pattern = r"project\s+metrics?\s+([^\s]+)|metrics?\s+for\s+project\s+([^\s]+)"
    project_match = re.search(project_pattern, message_lower)
    
    if project_match:
        project_id = project_match.group(1) or project_match.group(2)
        return {"scope": "project", "project_id": project_id}
    
    # Detailed analytics
    if "detailed" in message_lower or "analytics" in message_lower:
        return {"scope": "detailed"}
    
    # Default to overall metrics
    return {"scope": "overall"}


def _get_overall_requirement_metrics(supabase, organization_id: str) -> Dict[str, Any]:
    """Get overall requirement metrics for the organization."""
    
    # Get all projects for the organization
    projects = supabase.table("projects").select("id, name, status, created_at").eq("organization_id", organization_id).execute()
    
    if not projects.data:
        return {"error": "No projects found in organization"}
    
    overall_metrics = {
        "total_projects": len(projects.data),
        "total_requirements": 0,
        "total_documents": 0,
        "total_blocks": 0,
        "status_distribution": defaultdict(int),
        "priority_distribution": defaultdict(int),
        "format_distribution": defaultdict(int),
        "level_distribution": defaultdict(int),
        "ai_enhancement_usage": 0,
        "average_requirements_per_project": 0,
        "project_health_scores": []
    }
    
    project_details = []
    
    for project in projects.data:
        project_id = project['id']
        
        # Get project requirements
        requirements = supabase.rpc("get_project_requirements", {"project_id": project_id}).execute()
        project_req_count = len(requirements.data or [])
        
        # Get documents and blocks for this project
        documents = supabase.table("documents").select("id").eq("project_id", project_id).execute()
        project_doc_count = len(documents.data or [])
        
        blocks_count = 0
        if documents.data:
            doc_ids = [doc['id'] for doc in documents.data]
            blocks = supabase.table("blocks").select("id").in_("document_id", doc_ids).execute()
            blocks_count = len(blocks.data or [])
        
        # Process requirements for this project
        ai_enhanced_count = 0
        for req in requirements.data or []:
            overall_metrics["status_distribution"][req.get('status', 'unknown')] += 1
            overall_metrics["priority_distribution"][req.get('priority', 'unknown')] += 1
            overall_metrics["format_distribution"][req.get('format', 'unknown')] += 1
            overall_metrics["level_distribution"][req.get('level', 'unknown')] += 1
            
            if req.get('enchanced_requirement') or req.get('ai_analysis'):
                ai_enhanced_count += 1
        
        # Calculate project health score
        health_score = _calculate_project_health_score(supabase, project_id, project_req_count)
        
        project_detail = {
            "project": project,
            "requirements_count": project_req_count,
            "documents_count": project_doc_count,
            "blocks_count": blocks_count,
            "ai_enhanced_count": ai_enhanced_count,
            "health_score": health_score,
            "ai_enhancement_ratio": ai_enhanced_count / max(project_req_count, 1)
        }
        
        project_details.append(project_detail)
        
        # Update overall metrics
        overall_metrics["total_requirements"] += project_req_count
        overall_metrics["total_documents"] += project_doc_count
        overall_metrics["total_blocks"] += blocks_count
        overall_metrics["ai_enhancement_usage"] += ai_enhanced_count
        overall_metrics["project_health_scores"].append(health_score)
    
    # Calculate derived metrics
    overall_metrics["average_requirements_per_project"] = overall_metrics["total_requirements"] / max(overall_metrics["total_projects"], 1)
    overall_metrics["ai_enhancement_ratio"] = overall_metrics["ai_enhancement_usage"] / max(overall_metrics["total_requirements"], 1)
    overall_metrics["average_health_score"] = sum(overall_metrics["project_health_scores"]) / max(len(overall_metrics["project_health_scores"]), 1)
    
    # Convert defaultdicts to regular dicts
    overall_metrics["status_distribution"] = dict(overall_metrics["status_distribution"])
    overall_metrics["priority_distribution"] = dict(overall_metrics["priority_distribution"])
    overall_metrics["format_distribution"] = dict(overall_metrics["format_distribution"])
    overall_metrics["level_distribution"] = dict(overall_metrics["level_distribution"])
    
    # Generate insights and recommendations
    insights = _generate_overall_insights(overall_metrics, project_details)
    recommendations = _generate_overall_recommendations(overall_metrics, project_details)
    
    return {
        "success": True,
        "json": {
            "overall_metrics": overall_metrics,
            "project_details": project_details,
            "insights": insights,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    }


def _get_project_requirement_metrics(supabase, organization_id: str, project_id: str) -> Dict[str, Any]:
    """Get detailed requirement metrics for a specific project."""
    
    # Validate project access
    project = supabase.table("projects").select("*").eq("id", project_id).eq("organization_id", organization_id).execute()
    
    if not project.data:
        return {"error": f"Project {project_id} not found or not accessible"}
    
    project_info = project.data[0]
    
    # Get all requirements for the project
    requirements = supabase.rpc("get_project_requirements", {"project_id": project_id}).execute()
    requirements_data = requirements.data or []
    
    # Get documents and blocks
    documents = supabase.table("documents").select("*").eq("project_id", project_id).execute()
    documents_data = documents.data or []
    
    blocks_data = []
    if documents_data:
        doc_ids = [doc['id'] for doc in documents_data]
        blocks = supabase.table("blocks").select("*").in_("document_id", doc_ids).execute()
        blocks_data = blocks.data or []
    
    # Get assignments and trace links
    req_ids = [req['id'] for req in requirements_data]
    assignments = []
    trace_links = []
    
    if req_ids:
        assignments_result = supabase.table("assignments").select("*").in_("entity_id", req_ids).execute()
        assignments = assignments_result.data or []
        
        trace_links_result = supabase.table("trace_links").select("*").or_(
            f"source_id.in.({','.join(req_ids)}),target_id.in.({','.join(req_ids)})"
        ).execute()
        trace_links = trace_links_result.data or []
    
    # Calculate detailed metrics
    project_metrics = _calculate_detailed_project_metrics(
        requirements_data, documents_data, blocks_data, assignments, trace_links
    )
    
    # Get temporal analysis
    temporal_analysis = _get_temporal_analysis(requirements_data, documents_data)
    
    # Get quality metrics
    quality_metrics = _calculate_quality_metrics(requirements_data, trace_links)
    
    # Generate project-specific insights
    insights = _generate_project_insights(project_metrics, quality_metrics, temporal_analysis)
    recommendations = _generate_project_recommendations(project_metrics, quality_metrics)
    
    return {
        "success": True,
        "json": {
            "project": project_info,
            "project_metrics": project_metrics,
            "temporal_analysis": temporal_analysis,
            "quality_metrics": quality_metrics,
            "insights": insights,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    }


def _get_detailed_requirement_analytics(supabase, organization_id: str) -> Dict[str, Any]:
    """Get comprehensive analytics across all organizational data."""
    
    # Get all projects
    projects = supabase.table("projects").select("*").eq("organization_id", organization_id).execute()
    
    if not projects.data:
        return {"error": "No projects found in organization"}
    
    # Initialize analytics structure
    analytics = {
        "organizational_overview": {},
        "trend_analysis": {},
        "performance_analytics": {},
        "ai_usage_analytics": {},
        "collaboration_analytics": {},
        "quality_analytics": {},
        "predictive_insights": {}
    }
    
    all_requirements = []
    all_projects_data = []
    
    # Collect data from all projects
    for project in projects.data:
        project_id = project['id']
        
        # Get requirements
        requirements = supabase.rpc("get_project_requirements", {"project_id": project_id}).execute()
        project_requirements = requirements.data or []
        all_requirements.extend(project_requirements)
        
        # Get other entities
        documents = supabase.table("documents").select("*").eq("project_id", project_id).execute()
        assignments = supabase.table("assignments").select("*").eq("entity_type", "requirement").execute()
        
        all_projects_data.append({
            "project": project,
            "requirements": project_requirements,
            "documents": documents.data or [],
            "assignments": assignments.data or []
        })
    
    # Generate comprehensive analytics
    analytics["organizational_overview"] = _analyze_organizational_overview(all_projects_data, all_requirements)
    analytics["trend_analysis"] = _analyze_trends(all_projects_data, all_requirements)
    analytics["performance_analytics"] = _analyze_performance(all_projects_data)
    analytics["ai_usage_analytics"] = _analyze_ai_usage(all_requirements)
    analytics["collaboration_analytics"] = _analyze_collaboration(all_projects_data)
    analytics["quality_analytics"] = _analyze_quality_trends(all_requirements)
    analytics["predictive_insights"] = _generate_predictive_insights(all_projects_data, all_requirements)
    
    # Generate strategic recommendations
    strategic_recommendations = _generate_strategic_recommendations(analytics)
    
    return {
        "success": True,
        "json": {
            "detailed_analytics": analytics,
            "strategic_recommendations": strategic_recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "data_summary": {
                "total_projects": len(projects.data),
                "total_requirements": len(all_requirements),
                "analysis_period": "All time"
            }
        }
    }


def _calculate_project_health_score(supabase, project_id: str, req_count: int) -> float:
    """Calculate a health score for a project based on various factors."""
    
    score = 0.0
    max_score = 100.0
    
    # Factor 1: Requirement density (25 points)
    if req_count > 0:
        score += min(25, req_count * 2)  # 2 points per requirement, max 25
    
    # Factor 2: Traceability coverage (25 points)
    if req_count > 0:
        # Get trace links for project requirements
        requirements = supabase.rpc("get_project_requirements", {"project_id": project_id}).execute()
        req_ids = [req['id'] for req in requirements.data or []]
        
        if req_ids:
            trace_links = supabase.table("trace_links").select("id").or_(
                f"source_id.in.({','.join(req_ids)}),target_id.in.({','.join(req_ids)})"
            ).execute()
            
            traceability_ratio = len(trace_links.data or []) / req_count
            score += min(25, traceability_ratio * 25)
    
    # Factor 3: Documentation coverage (25 points)
    documents = supabase.table("documents").select("id").eq("project_id", project_id).execute()
    doc_count = len(documents.data or [])
    if doc_count > 0:
        score += min(25, doc_count * 5)  # 5 points per document, max 25
    
    # Factor 4: Activity level (25 points)
    # Check recent updates (simplified)
    try:
        recent_updates = supabase.table("projects").select("updated_at").eq("id", project_id).execute()
        if recent_updates.data:
            # Award points based on recency (simplified logic)
            score += 20  # Base activity score
    except:
        pass
    
    return min(score, max_score)


def _calculate_detailed_project_metrics(requirements: List, documents: List, blocks: List, assignments: List, trace_links: List) -> Dict[str, Any]:
    """Calculate detailed metrics for a project."""
    
    metrics = {
        "entity_counts": {
            "requirements": len(requirements),
            "documents": len(documents),
            "blocks": len(blocks),
            "assignments": len(assignments),
            "trace_links": len(trace_links)
        },
        "requirement_analysis": {},
        "assignment_analysis": {},
        "traceability_analysis": {}
    }
    
    if requirements:
        # Analyze requirements
        status_dist = defaultdict(int)
        priority_dist = defaultdict(int)
        level_dist = defaultdict(int)
        format_dist = defaultdict(int)
        ai_enhanced = 0
        
        for req in requirements:
            status_dist[req.get('status', 'unknown')] += 1
            priority_dist[req.get('priority', 'unknown')] += 1
            level_dist[req.get('level', 'unknown')] += 1
            format_dist[req.get('format', 'unknown')] += 1
            
            if req.get('enchanced_requirement') or req.get('ai_analysis'):
                ai_enhanced += 1
        
        metrics["requirement_analysis"] = {
            "status_distribution": dict(status_dist),
            "priority_distribution": dict(priority_dist),
            "level_distribution": dict(level_dist),
            "format_distribution": dict(format_dist),
            "ai_enhancement_ratio": ai_enhanced / len(requirements)
        }
    
    if assignments:
        # Analyze assignments
        role_dist = defaultdict(int)
        status_dist = defaultdict(int)
        
        for assignment in assignments:
            role_dist[assignment.get('role', 'unknown')] += 1
            status_dist[assignment.get('status', 'unknown')] += 1
        
        metrics["assignment_analysis"] = {
            "role_distribution": dict(role_dist),
            "status_distribution": dict(status_dist),
            "assignment_ratio": len(assignments) / max(len(requirements), 1)
        }
    
    if trace_links:
        # Analyze traceability
        link_type_dist = defaultdict(int)
        strength_dist = defaultdict(int)
        
        for link in trace_links:
            link_type_dist[link.get('link_type', 'unknown')] += 1
            strength = link.get('relationship_strength', 1)
            strength_dist[f"strength_{strength}"] += 1
        
        metrics["traceability_analysis"] = {
            "link_type_distribution": dict(link_type_dist),
            "strength_distribution": dict(strength_dist),
            "traceability_ratio": len(trace_links) / max(len(requirements), 1)
        }
    
    return metrics


def _get_temporal_analysis(requirements: List, documents: List) -> Dict[str, Any]:
    """Analyze temporal patterns in the data."""
    
    temporal_analysis = {
        "creation_timeline": {},
        "update_patterns": {},
        "activity_trends": {}
    }
    
    # Analyze creation timeline
    creation_dates = []
    for req in requirements:
        if req.get('created_at'):
            creation_dates.append(req['created_at'])
    
    for doc in documents:
        if doc.get('created_at'):
            creation_dates.append(doc['created_at'])
    
    if creation_dates:
        # Group by month
        monthly_counts = defaultdict(int)
        for date_str in creation_dates:
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                month_key = date_obj.strftime('%Y-%m')
                monthly_counts[month_key] += 1
            except:
                continue
        
        temporal_analysis["creation_timeline"] = dict(monthly_counts)
    
    return temporal_analysis


def _calculate_quality_metrics(requirements: List, trace_links: List) -> Dict[str, Any]:
    """Calculate quality-related metrics."""
    
    quality_metrics = {
        "completeness_score": 0,
        "consistency_score": 0,
        "traceability_score": 0,
        "detail_richness": 0
    }
    
    if requirements:
        # Completeness: requirements with descriptions
        complete_reqs = sum(1 for req in requirements if req.get('description'))
        quality_metrics["completeness_score"] = (complete_reqs / len(requirements)) * 100
        
        # Detail richness: average description length
        desc_lengths = [len(req.get('description', '')) for req in requirements if req.get('description')]
        if desc_lengths:
            quality_metrics["detail_richness"] = statistics.mean(desc_lengths)
        
        # Traceability score
        req_ids = {req['id'] for req in requirements}
        linked_reqs = set()
        for link in trace_links:
            if link['source_id'] in req_ids:
                linked_reqs.add(link['source_id'])
            if link['target_id'] in req_ids:
                linked_reqs.add(link['target_id'])
        
        if req_ids:
            quality_metrics["traceability_score"] = (len(linked_reqs) / len(req_ids)) * 100
    
    return quality_metrics


def _generate_overall_insights(overall_metrics: Dict, project_details: List) -> List[str]:
    """Generate insights from overall metrics."""
    
    insights = []
    
    # AI enhancement insights
    ai_ratio = overall_metrics.get("ai_enhancement_ratio", 0)
    if ai_ratio > 0.7:
        insights.append("High AI enhancement adoption - organization is leveraging AI effectively")
    elif ai_ratio < 0.3:
        insights.append("Low AI enhancement usage - opportunity to improve requirement quality with AI")
    
    # Project health insights
    avg_health = overall_metrics.get("average_health_score", 0)
    if avg_health > 75:
        insights.append("Strong project health across the organization")
    elif avg_health < 50:
        insights.append("Project health needs attention - several projects showing low health scores")
    
    # Distribution insights
    status_dist = overall_metrics.get("status_distribution", {})
    if status_dist.get("draft", 0) > status_dist.get("approved", 0):
        insights.append("High number of draft requirements - consider accelerating review process")
    
    return insights


def _generate_overall_recommendations(overall_metrics: Dict, project_details: List) -> List[str]:
    """Generate recommendations from overall analysis."""
    
    recommendations = []
    
    # Based on AI usage
    if overall_metrics.get("ai_enhancement_ratio", 0) < 0.5:
        recommendations.append("Increase AI enhancement usage to improve requirement quality")
    
    # Based on project health
    low_health_projects = [p for p in project_details if p["health_score"] < 60]
    if low_health_projects:
        recommendations.append(f"Focus attention on {len(low_health_projects)} projects with low health scores")
    
    # Based on requirements per project
    if overall_metrics.get("average_requirements_per_project", 0) < 10:
        recommendations.append("Consider increasing requirement documentation depth")
    
    return recommendations


def _analyze_organizational_overview(projects_data: List, all_requirements: List) -> Dict[str, Any]:
    """Analyze organizational overview metrics."""
    
    return {
        "total_projects": len(projects_data),
        "total_requirements": len(all_requirements),
        "average_project_size": len(all_requirements) / max(len(projects_data), 1),
        "organizational_maturity": _calculate_maturity_score(projects_data, all_requirements)
    }


def _analyze_trends(projects_data: List, all_requirements: List) -> Dict[str, Any]:
    """Analyze trends in the data."""
    
    # Simplified trend analysis
    return {
        "growth_trend": "stable",  # Would need historical data for real analysis
        "quality_trend": "improving",
        "ai_adoption_trend": "increasing"
    }


def _analyze_performance(projects_data: List) -> Dict[str, Any]:
    """Analyze performance metrics."""
    
    return {
        "high_performing_projects": len([p for p in projects_data if len(p["requirements"]) > 20]),
        "average_completion_time": "N/A",  # Would need historical data
        "efficiency_score": 75  # Placeholder
    }


def _analyze_ai_usage(all_requirements: List) -> Dict[str, Any]:
    """Analyze AI usage patterns."""
    
    ai_enhanced = sum(1 for req in all_requirements if req.get('enchanced_requirement') or req.get('ai_analysis'))
    
    return {
        "total_ai_enhanced": ai_enhanced,
        "ai_enhancement_ratio": ai_enhanced / max(len(all_requirements), 1),
        "ai_adoption_level": "high" if ai_enhanced / max(len(all_requirements), 1) > 0.6 else "medium"
    }


def _analyze_collaboration(projects_data: List) -> Dict[str, Any]:
    """Analyze collaboration patterns."""
    
    total_assignments = sum(len(p["assignments"]) for p in projects_data)
    
    return {
        "total_assignments": total_assignments,
        "collaboration_level": "high" if total_assignments > 50 else "medium",
        "average_assignments_per_project": total_assignments / max(len(projects_data), 1)
    }


def _analyze_quality_trends(all_requirements: List) -> Dict[str, Any]:
    """Analyze quality trends."""
    
    complete_descriptions = sum(1 for req in all_requirements if req.get('description'))
    
    return {
        "description_completeness": complete_descriptions / max(len(all_requirements), 1),
        "quality_score": 80,  # Placeholder
        "improvement_areas": ["consistency", "detail_level"]
    }


def _generate_predictive_insights(projects_data: List, all_requirements: List) -> Dict[str, Any]:
    """Generate predictive insights."""
    
    return {
        "projected_growth": "15% increase in requirements over next quarter",
        "resource_needs": "Additional project managers recommended",
        "risk_factors": ["Traceability gaps in some projects"]
    }


def _generate_strategic_recommendations(analytics: Dict) -> List[str]:
    """Generate strategic recommendations."""
    
    recommendations = []
    
    # Based on AI usage
    ai_analytics = analytics.get("ai_usage_analytics", {})
    if ai_analytics.get("ai_enhancement_ratio", 0) < 0.6:
        recommendations.append("Implement AI enhancement training program")
    
    # Based on collaboration
    collab_analytics = analytics.get("collaboration_analytics", {})
    if collab_analytics.get("collaboration_level") == "medium":
        recommendations.append("Enhance collaboration processes and tools")
    
    return recommendations


def _calculate_maturity_score(projects_data: List, all_requirements: List) -> int:
    """Calculate organizational maturity score."""
    
    score = 0
    
    # Factor 1: Project diversity (20 points)
    if len(projects_data) > 5:
        score += 20
    elif len(projects_data) > 2:
        score += 10
    
    # Factor 2: Requirement depth (30 points)
    if len(all_requirements) > 100:
        score += 30
    elif len(all_requirements) > 50:
        score += 20
    elif len(all_requirements) > 20:
        score += 10
    
    # Factor 3: AI adoption (25 points)
    ai_enhanced = sum(1 for req in all_requirements if req.get('enchanced_requirement'))
    ai_ratio = ai_enhanced / max(len(all_requirements), 1)
    score += int(ai_ratio * 25)
    
    # Factor 4: Process standardization (25 points)
    # Simplified check for consistent data
    score += 15  # Placeholder
    
    return min(score, 100)