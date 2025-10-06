"""Get project health tool module"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import statistics

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def get_project_health_tool(organization_id: str, message: str) -> Any:
    """
    Generate comprehensive project health dashboard with metrics, KPIs, and alerts.
    Provides executive-level insights into project status, risks, and performance indicators.
    
    Parameters
    ----------
    organization_id : str
        User's individual organization ID
    message : str
        User's request message specifying health analysis scope and focus areas
        
    Returns
    -------
    Any
        Result containing project health dashboard data, KPIs, and actionable insights
    """
    print(f"[get_project_health] Starting with organization_id: {organization_id}")
    print(f"[get_project_health] Message: {message}")
    
    try:
        # Create Supabase client
        print("[get_project_health] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Parse health analysis parameters from message
        health_params = _parse_health_parameters(message)
        
        print(f"[get_project_health] Health parameters: {health_params}")
        
        # Get organization projects with details
        projects_response = supabase.table("projects").select(
            "id, name, description, status, visibility, created_at, updated_at, version"
        ).eq("organization_id", organization_id).eq("is_deleted", False).execute()
        
        if not projects_response.data:
            return {
                "json": {
                    "error": "No projects found for the organization",
                    "message": message
                }
            }
        
        # Generate comprehensive project health analysis
        health_result = _generate_project_health_analysis(supabase, organization_id, projects_response.data, health_params)
        
        # Generate risk assessment
        risk_assessment = _generate_risk_assessment(health_result)
        
        # Generate KPI dashboard
        kpi_dashboard = _generate_kpi_dashboard(health_result)
        
        # Generate alerts and recommendations
        alerts = _generate_health_alerts(health_result, risk_assessment)
        recommendations = _generate_health_recommendations(health_result, risk_assessment)
        
        result = {
            "json": {
                "organization_id": organization_id,
                "health_analysis_timestamp": datetime.now().isoformat(),
                "analysis_scope": health_params["scope"],
                "projects_analyzed": len(projects_response.data),
                "health_overview": _generate_health_overview(health_result),
                "project_health_details": health_result,
                "kpi_dashboard": kpi_dashboard,
                "risk_assessment": risk_assessment,
                "alerts": alerts,
                "recommendations": recommendations,
                "executive_summary": _generate_executive_summary(health_result, kpi_dashboard, risk_assessment),
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[get_project_health] Saving result to JSON file...")
        with open("get_project_health_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("[get_project_health] SUCCESS: Completed successfully")
        return result
        
    except Exception as e:
        print(f"[get_project_health] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def _parse_health_parameters(message: str) -> Dict[str, Any]:
    """Parse message to determine health analysis parameters"""
    message_lower = message.lower()
    
    params = {
        "scope": "comprehensive",
        "include_kpis": True,
        "include_risks": True,
        "include_trends": True,
        "focus_area": "all",
        "detail_level": "standard"
    }
    
    # Determine scope
    if "overview" in message_lower or "summary" in message_lower:
        params["scope"] = "overview"
    elif "detailed" in message_lower or "comprehensive" in message_lower:
        params["scope"] = "comprehensive"
    elif "kpi" in message_lower or "metrics" in message_lower:
        params["scope"] = "kpis"
    elif "risk" in message_lower:
        params["scope"] = "risk"
    
    # Focus area
    if "requirement" in message_lower:
        params["focus_area"] = "requirements"
    elif "test" in message_lower:
        params["focus_area"] = "testing"
    elif "completion" in message_lower or "progress" in message_lower:
        params["focus_area"] = "progress"
    elif "quality" in message_lower:
        params["focus_area"] = "quality"
    
    # Detail level
    if "executive" in message_lower or "high-level" in message_lower:
        params["detail_level"] = "executive"
    elif "detailed" in message_lower:
        params["detail_level"] = "detailed"
    
    return params

def _generate_project_health_analysis(supabase, organization_id: str, projects: List[Dict], params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive project health analysis"""
    
    health_analysis = {
        "project_metrics": {},
        "organization_metrics": {},
        "health_scores": {},
        "performance_indicators": {},
        "activity_metrics": {}
    }
    
    try:
        # Analyze each project individually
        project_metrics = {}
        organization_totals = {
            "total_requirements": 0,
            "total_tests": 0,
            "total_documents": 0,
            "total_trace_links": 0,
            "active_projects": 0
        }
        
        for project in projects:
            print(f"[get_project_health] Analyzing project: {project['name']}")
            
            project_analysis = _analyze_individual_project(supabase, project)
            project_metrics[project["id"]] = {
                "project_info": {
                    "id": project["id"],
                    "name": project["name"],
                    "status": project.get("status", "unknown"),
                    "created_at": project.get("created_at"),
                    "updated_at": project.get("updated_at")
                },
                "metrics": project_analysis,
                "health_score": _calculate_project_health_score(project_analysis)
            }
            
            # Aggregate organization metrics
            metrics = project_analysis
            organization_totals["total_requirements"] += metrics.get("requirements_count", 0)
            organization_totals["total_tests"] += metrics.get("tests_count", 0)
            organization_totals["total_documents"] += metrics.get("documents_count", 0)
            organization_totals["total_trace_links"] += metrics.get("trace_links_count", 0)
            
            if project.get("status") == "active":
                organization_totals["active_projects"] += 1
        
        health_analysis["project_metrics"] = project_metrics
        health_analysis["organization_metrics"] = organization_totals
        
        # Calculate overall health scores
        project_health_scores = [pm["health_score"] for pm in project_metrics.values()]
        organization_health_score = statistics.mean(project_health_scores) if project_health_scores else 0
        
        health_analysis["health_scores"] = {
            "organization_health_score": round(organization_health_score, 1),
            "project_health_scores": {
                pid: pm["health_score"] for pid, pm in project_metrics.items()
            },
            "health_distribution": {
                "excellent": len([s for s in project_health_scores if s >= 90]),
                "good": len([s for s in project_health_scores if 80 <= s < 90]),
                "fair": len([s for s in project_health_scores if 60 <= s < 80]),
                "poor": len([s for s in project_health_scores if s < 60])
            }
        }
        
        # Generate performance indicators
        health_analysis["performance_indicators"] = _calculate_performance_indicators(project_metrics)
        
        # Generate activity metrics
        health_analysis["activity_metrics"] = _calculate_activity_metrics(supabase, organization_id, projects)
        
        return health_analysis
        
    except Exception as e:
        print(f"[get_project_health] Error generating health analysis: {str(e)}")
        return {"error": f"Health analysis failed: {str(e)}"}

def _analyze_individual_project(supabase, project: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze health metrics for an individual project"""
    
    metrics = {
        "requirements_count": 0,
        "documents_count": 0,
        "tests_count": 0,
        "trace_links_count": 0,
        "completion_metrics": {},
        "quality_indicators": {},
        "activity_indicators": {}
    }
    
    try:
        project_id = project["id"]
        
        # Get documents count
        docs_response = supabase.table("documents").select("id, created_at, updated_at").eq("project_id", project_id).eq("is_deleted", False).execute()
        documents = docs_response.data if docs_response.data else []
        metrics["documents_count"] = len(documents)
        
        # Get requirements with details
        requirements = []
        for doc in documents:
            reqs_response = supabase.table("requirements").select(
                "id, name, status, priority, level, created_at, updated_at, version"
            ).eq("document_id", doc["id"]).eq("is_deleted", False).execute()
            
            if reqs_response.data:
                requirements.extend(reqs_response.data)
        
        metrics["requirements_count"] = len(requirements)
        
        # Analyze requirement completion
        if requirements:
            status_counts = {}
            priority_counts = {}
            for req in requirements:
                status = req.get("status", "unknown")
                priority = req.get("priority", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Calculate completion percentage
            completed_statuses = ["approved", "implemented", "verified", "closed"]
            completed_count = sum(status_counts.get(status, 0) for status in completed_statuses)
            completion_percentage = (completed_count / len(requirements) * 100) if requirements else 0
            
            metrics["completion_metrics"] = {
                "completion_percentage": round(completion_percentage, 1),
                "completed_requirements": completed_count,
                "total_requirements": len(requirements),
                "status_distribution": status_counts,
                "priority_distribution": priority_counts
            }
            
            # Quality indicators
            with_names = len([r for r in requirements if r.get("name")])
            high_priority = priority_counts.get("high", 0) + priority_counts.get("critical", 0)
            
            metrics["quality_indicators"] = {
                "requirements_with_names_percentage": (with_names / len(requirements) * 100) if requirements else 0,
                "high_priority_requirements": high_priority,
                "high_priority_percentage": (high_priority / len(requirements) * 100) if requirements else 0,
                "average_version": statistics.mean([r.get("version", 1) for r in requirements]) if requirements else 1
            }
        
        # Get tests count
        tests_response = supabase.table("test_req").select("id, status, priority").eq("project_id", project_id).eq("is_active", True).execute()
        tests = tests_response.data if tests_response.data else []
        metrics["tests_count"] = len(tests)
        
        # Get trace links count (approximation)
        req_ids = [req["id"] for req in requirements]
        if req_ids:
            trace_links_response = supabase.table("trace_links").select("id").in_("source_id", req_ids).eq("is_deleted", False).execute()
            metrics["trace_links_count"] = len(trace_links_response.data) if trace_links_response.data else 0
        
        # Activity indicators
        now = datetime.now()
        recent_activity = 0
        
        # Check recent requirement updates
        for req in requirements:
            updated_at = req.get("updated_at")
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    if updated_date > now - timedelta(days=30):
                        recent_activity += 1
                except:
                    continue
        
        metrics["activity_indicators"] = {
            "recent_requirement_updates": recent_activity,
            "activity_score": min(100, (recent_activity / len(requirements) * 100)) if requirements else 0,
            "last_project_update": project.get("updated_at")
        }
        
        return metrics
        
    except Exception as e:
        print(f"Error analyzing project {project.get('name', 'Unknown')}: {str(e)}")
        return metrics

def _calculate_project_health_score(metrics: Dict[str, Any]) -> float:
    """Calculate overall health score for a project (0-100)"""
    
    try:
        scores = []
        weights = []
        
        # Completion score (30% weight)
        completion_metrics = metrics.get("completion_metrics", {})
        completion_pct = completion_metrics.get("completion_percentage", 0)
        scores.append(completion_pct)
        weights.append(30)
        
        # Quality score (25% weight)
        quality_indicators = metrics.get("quality_indicators", {})
        names_pct = quality_indicators.get("requirements_with_names_percentage", 0)
        avg_version = quality_indicators.get("average_version", 1)
        version_score = min(100, 50 + (avg_version - 1) * 25)  # Higher versions indicate active maintenance
        
        quality_score = (names_pct * 0.7 + version_score * 0.3)
        scores.append(quality_score)
        weights.append(25)
        
        # Activity score (20% weight)
        activity_indicators = metrics.get("activity_indicators", {})
        activity_score = activity_indicators.get("activity_score", 0)
        scores.append(activity_score)
        weights.append(20)
        
        # Coverage score (15% weight) - based on tests and trace links
        reqs_count = metrics.get("requirements_count", 1)
        tests_count = metrics.get("tests_count", 0)
        trace_links_count = metrics.get("trace_links_count", 0)
        
        test_coverage = min(100, (tests_count / reqs_count * 100)) if reqs_count > 0 else 0
        trace_coverage = min(100, (trace_links_count / reqs_count * 100)) if reqs_count > 0 else 0
        
        coverage_score = (test_coverage * 0.6 + trace_coverage * 0.4)
        scores.append(coverage_score)
        weights.append(15)
        
        # Content score (10% weight) - based on having requirements and documents
        has_requirements = 100 if reqs_count > 0 else 0
        has_documents = 100 if metrics.get("documents_count", 0) > 0 else 0
        
        content_score = (has_requirements * 0.8 + has_documents * 0.2)
        scores.append(content_score)
        weights.append(10)
        
        # Calculate weighted average
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        health_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        return round(health_score, 1)
        
    except Exception as e:
        print(f"Error calculating health score: {str(e)}")
        return 0.0

def _calculate_performance_indicators(project_metrics: Dict[str, Dict]) -> Dict[str, Any]:
    """Calculate organization-level performance indicators"""
    
    indicators = {
        "productivity_metrics": {},
        "efficiency_metrics": {},
        "quality_metrics": {}
    }
    
    try:
        all_projects = list(project_metrics.values())
        
        if not all_projects:
            return indicators
        
        # Productivity metrics
        total_requirements = sum(pm["metrics"].get("requirements_count", 0) for pm in all_projects)
        total_tests = sum(pm["metrics"].get("tests_count", 0) for pm in all_projects)
        total_projects = len(all_projects)
        
        indicators["productivity_metrics"] = {
            "avg_requirements_per_project": round(total_requirements / total_projects, 1) if total_projects > 0 else 0,
            "avg_tests_per_project": round(total_tests / total_projects, 1) if total_projects > 0 else 0,
            "requirements_to_tests_ratio": round(total_requirements / total_tests, 2) if total_tests > 0 else 0,
            "total_project_count": total_projects
        }
        
        # Efficiency metrics
        completion_rates = [
            pm["metrics"].get("completion_metrics", {}).get("completion_percentage", 0)
            for pm in all_projects
        ]
        
        activity_scores = [
            pm["metrics"].get("activity_indicators", {}).get("activity_score", 0)
            for pm in all_projects
        ]
        
        indicators["efficiency_metrics"] = {
            "avg_completion_rate": round(statistics.mean(completion_rates), 1) if completion_rates else 0,
            "avg_activity_score": round(statistics.mean(activity_scores), 1) if activity_scores else 0,
            "high_performing_projects": len([r for r in completion_rates if r >= 80]),
            "underperforming_projects": len([r for r in completion_rates if r < 50])
        }
        
        # Quality metrics
        quality_scores = [
            pm["metrics"].get("quality_indicators", {}).get("requirements_with_names_percentage", 0)
            for pm in all_projects
        ]
        
        high_priority_counts = [
            pm["metrics"].get("quality_indicators", {}).get("high_priority_requirements", 0)
            for pm in all_projects
        ]
        
        indicators["quality_metrics"] = {
            "avg_requirement_quality_score": round(statistics.mean(quality_scores), 1) if quality_scores else 0,
            "total_high_priority_requirements": sum(high_priority_counts),
            "avg_high_priority_per_project": round(statistics.mean(high_priority_counts), 1) if high_priority_counts else 0,
            "quality_consistency": round(statistics.stdev(quality_scores), 1) if len(quality_scores) > 1 else 0
        }
        
        return indicators
        
    except Exception as e:
        print(f"Error calculating performance indicators: {str(e)}")
        return indicators

def _calculate_activity_metrics(supabase, organization_id: str, projects: List[Dict]) -> Dict[str, Any]:
    """Calculate organization activity metrics"""
    
    activity_metrics = {
        "recent_activity": {},
        "growth_trends": {},
        "engagement_metrics": {}
    }
    
    try:
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)
        
        # Recent activity analysis
        recent_projects = 0
        recent_requirements = 0
        recent_tests = 0
        
        for project in projects:
            project_updated = project.get("updated_at")
            if project_updated:
                try:
                    update_date = datetime.fromisoformat(project_updated.replace('Z', '+00:00'))
                    if update_date > thirty_days_ago:
                        recent_projects += 1
                except:
                    continue
        
        # Get recent requirements and tests (simplified query)
        # Note: This is a simplified approach. In production, you might want more sophisticated queries
        
        activity_metrics["recent_activity"] = {
            "projects_updated_last_30_days": recent_projects,
            "project_activity_rate": (recent_projects / len(projects) * 100) if projects else 0,
            "analysis_date": now.isoformat(),
            "active_project_percentage": (recent_projects / len(projects) * 100) if projects else 0
        }
        
        # Growth trends (simplified)
        creation_dates = []
        for project in projects:
            created_at = project.get("created_at")
            if created_at:
                try:
                    creation_dates.append(datetime.fromisoformat(created_at.replace('Z', '+00:00')))
                except:
                    continue
        
        if creation_dates:
            creation_dates.sort()
            recent_creations = len([d for d in creation_dates if d > thirty_days_ago])
            
            activity_metrics["growth_trends"] = {
                "new_projects_last_30_days": recent_creations,
                "project_creation_rate": (recent_creations / len(projects) * 100) if projects else 0,
                "oldest_project_age_days": (now - min(creation_dates)).days if creation_dates else 0,
                "newest_project_age_days": (now - max(creation_dates)).days if creation_dates else 0
            }
        
        return activity_metrics
        
    except Exception as e:
        print(f"Error calculating activity metrics: {str(e)}")
        return activity_metrics

def _generate_risk_assessment(health_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate risk assessment based on health analysis"""
    
    if "error" in health_result:
        return {"error": "Cannot assess risks due to health analysis error"}
    
    risk_assessment = {
        "overall_risk_level": "low",
        "risk_factors": [],
        "critical_risks": [],
        "project_risks": {},
        "mitigation_priorities": []
    }
    
    try:
        # Analyze organization-level risks
        health_scores = health_result.get("health_scores", {})
        org_health = health_scores.get("organization_health_score", 100)
        
        project_metrics = health_result.get("project_metrics", {})
        performance_indicators = health_result.get("performance_indicators", {})
        
        # Overall risk level
        if org_health < 50:
            risk_assessment["overall_risk_level"] = "critical"
        elif org_health < 70:
            risk_assessment["overall_risk_level"] = "high"
        elif org_health < 85:
            risk_assessment["overall_risk_level"] = "medium"
        
        # Identify risk factors
        risk_factors = []
        
        # Low completion rates
        efficiency_metrics = performance_indicators.get("efficiency_metrics", {})
        avg_completion = efficiency_metrics.get("avg_completion_rate", 100)
        if avg_completion < 60:
            risk_factors.append({
                "type": "completion_risk",
                "severity": "high" if avg_completion < 40 else "medium",
                "description": f"Low average completion rate: {avg_completion:.1f}%",
                "impact": "Project delivery delays and quality issues"
            })
        
        # Underperforming projects
        underperforming = efficiency_metrics.get("underperforming_projects", 0)
        total_projects = len(project_metrics)
        if underperforming > total_projects * 0.3:  # More than 30% underperforming
            risk_factors.append({
                "type": "performance_risk", 
                "severity": "high",
                "description": f"{underperforming} out of {total_projects} projects underperforming",
                "impact": "Portfolio-wide performance degradation"
            })
        
        # Low activity
        activity_metrics = health_result.get("activity_metrics", {})
        recent_activity = activity_metrics.get("recent_activity", {})
        activity_rate = recent_activity.get("project_activity_rate", 100)
        if activity_rate < 30:
            risk_factors.append({
                "type": "activity_risk",
                "severity": "medium",
                "description": f"Low project activity rate: {activity_rate:.1f}%",
                "impact": "Stagnant project progress and stakeholder disengagement"
            })
        
        # Quality risks
        quality_metrics = performance_indicators.get("quality_metrics", {})
        quality_score = quality_metrics.get("avg_requirement_quality_score", 100)
        if quality_score < 70:
            risk_factors.append({
                "type": "quality_risk",
                "severity": "medium" if quality_score < 50 else "low",
                "description": f"Low requirement quality score: {quality_score:.1f}%",
                "impact": "Poor requirement clarity leading to implementation issues"
            })
        
        risk_assessment["risk_factors"] = risk_factors
        
        # Identify critical risks
        critical_risks = [rf for rf in risk_factors if rf["severity"] == "high"]
        risk_assessment["critical_risks"] = critical_risks
        
        # Project-specific risks
        project_risks = {}
        for project_id, project_data in project_metrics.items():
            health_score = project_data["health_score"]
            project_name = project_data["project_info"]["name"]
            
            if health_score < 50:
                project_risks[project_id] = {
                    "project_name": project_name,
                    "risk_level": "critical",
                    "health_score": health_score,
                    "primary_concerns": _identify_project_concerns(project_data["metrics"])
                }
            elif health_score < 70:
                project_risks[project_id] = {
                    "project_name": project_name,
                    "risk_level": "high",
                    "health_score": health_score,
                    "primary_concerns": _identify_project_concerns(project_data["metrics"])
                }
        
        risk_assessment["project_risks"] = project_risks
        
        # Mitigation priorities
        priorities = []
        if critical_risks:
            priorities.append("Address critical risk factors immediately")
        if len(project_risks) > 0:
            priorities.append(f"Focus on {len(project_risks)} at-risk projects")
        if avg_completion < 70:
            priorities.append("Improve overall completion rates")
        
        risk_assessment["mitigation_priorities"] = priorities
        
        return risk_assessment
        
    except Exception as e:
        print(f"Error generating risk assessment: {str(e)}")
        return {"error": f"Risk assessment failed: {str(e)}"}

def _identify_project_concerns(project_metrics: Dict[str, Any]) -> List[str]:
    """Identify primary concerns for a project based on its metrics"""
    
    concerns = []
    
    completion_metrics = project_metrics.get("completion_metrics", {})
    completion_pct = completion_metrics.get("completion_percentage", 0)
    
    quality_indicators = project_metrics.get("quality_indicators", {})
    quality_pct = quality_indicators.get("requirements_with_names_percentage", 0)
    
    activity_indicators = project_metrics.get("activity_indicators", {})
    activity_score = activity_indicators.get("activity_score", 0)
    
    if completion_pct < 30:
        concerns.append("Very low completion rate")
    elif completion_pct < 60:
        concerns.append("Low completion rate")
    
    if quality_pct < 50:
        concerns.append("Poor requirement quality")
    elif quality_pct < 80:
        concerns.append("Moderate requirement quality issues")
    
    if activity_score < 20:
        concerns.append("Inactive project")
    elif activity_score < 50:
        concerns.append("Low project activity")
    
    if project_metrics.get("requirements_count", 0) == 0:
        concerns.append("No requirements defined")
    
    if project_metrics.get("tests_count", 0) == 0:
        concerns.append("No tests created")
    
    return concerns

def _generate_kpi_dashboard(health_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate KPI dashboard from health analysis"""
    
    if "error" in health_result:
        return {"error": "Cannot generate KPIs due to health analysis error"}
    
    kpi_dashboard = {
        "key_metrics": {},
        "performance_indicators": {},
        "quality_indicators": {},
        "trend_indicators": {}
    }
    
    try:
        organization_metrics = health_result.get("organization_metrics", {})
        health_scores = health_result.get("health_scores", {})
        performance_indicators = health_result.get("performance_indicators", {})
        activity_metrics = health_result.get("activity_metrics", {})
        
        # Key metrics
        kpi_dashboard["key_metrics"] = {
            "organization_health_score": health_scores.get("organization_health_score", 0),
            "total_projects": len(health_result.get("project_metrics", {})),
            "total_requirements": organization_metrics.get("total_requirements", 0),
            "total_tests": organization_metrics.get("total_tests", 0),
            "active_projects": organization_metrics.get("active_projects", 0)
        }
        
        # Performance indicators
        efficiency_metrics = performance_indicators.get("efficiency_metrics", {})
        productivity_metrics = performance_indicators.get("productivity_metrics", {})
        
        kpi_dashboard["performance_indicators"] = {
            "avg_completion_rate": efficiency_metrics.get("avg_completion_rate", 0),
            "avg_activity_score": efficiency_metrics.get("avg_activity_score", 0),
            "avg_requirements_per_project": productivity_metrics.get("avg_requirements_per_project", 0),
            "requirements_to_tests_ratio": productivity_metrics.get("requirements_to_tests_ratio", 0),
            "high_performing_projects": efficiency_metrics.get("high_performing_projects", 0)
        }
        
        # Quality indicators
        quality_metrics = performance_indicators.get("quality_metrics", {})
        health_distribution = health_scores.get("health_distribution", {})
        
        kpi_dashboard["quality_indicators"] = {
            "avg_requirement_quality_score": quality_metrics.get("avg_requirement_quality_score", 0),
            "total_high_priority_requirements": quality_metrics.get("total_high_priority_requirements", 0),
            "excellent_health_projects": health_distribution.get("excellent", 0),
            "poor_health_projects": health_distribution.get("poor", 0)
        }
        
        # Trend indicators
        recent_activity = activity_metrics.get("recent_activity", {})
        growth_trends = activity_metrics.get("growth_trends", {})
        
        kpi_dashboard["trend_indicators"] = {
            "project_activity_rate": recent_activity.get("project_activity_rate", 0),
            "new_projects_last_30_days": growth_trends.get("new_projects_last_30_days", 0),
            "projects_updated_last_30_days": recent_activity.get("projects_updated_last_30_days", 0)
        }
        
        return kpi_dashboard
        
    except Exception as e:
        print(f"Error generating KPI dashboard: {str(e)}")
        return {"error": f"KPI dashboard generation failed: {str(e)}"}

def _generate_health_alerts(health_result: Dict[str, Any], risk_assessment: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate health alerts based on analysis"""
    
    alerts = []
    
    try:
        # Critical health alerts
        health_scores = health_result.get("health_scores", {})
        org_health = health_scores.get("organization_health_score", 100)
        
        if org_health < 50:
            alerts.append({
                "type": "critical",
                "title": "Organization Health Critical",
                "description": f"Overall health score is {org_health:.1f}%. Immediate action required.",
                "priority": "high"
            })
        elif org_health < 70:
            alerts.append({
                "type": "warning", 
                "title": "Organization Health Low",
                "description": f"Overall health score is {org_health:.1f}%. Review and improvement needed.",
                "priority": "medium"
            })
        
        # Project-specific alerts
        project_metrics = health_result.get("project_metrics", {})
        poor_health_projects = [
            pm for pm in project_metrics.values() 
            if pm["health_score"] < 60
        ]
        
        if poor_health_projects:
            alerts.append({
                "type": "warning",
                "title": f"{len(poor_health_projects)} Projects Need Attention",
                "description": f"Projects with health scores below 60%: {', '.join([p['project_info']['name'] for p in poor_health_projects[:3]])}",
                "priority": "medium"
            })
        
        # Performance alerts
        performance_indicators = health_result.get("performance_indicators", {})
        efficiency_metrics = performance_indicators.get("efficiency_metrics", {})
        
        avg_completion = efficiency_metrics.get("avg_completion_rate", 100)
        if avg_completion < 50:
            alerts.append({
                "type": "critical",
                "title": "Low Completion Rate",
                "description": f"Average completion rate is {avg_completion:.1f}%. Projects may be at risk.",
                "priority": "high"
            })
        
        underperforming = efficiency_metrics.get("underperforming_projects", 0)
        total_projects = len(project_metrics)
        if underperforming > total_projects * 0.4:
            alerts.append({
                "type": "warning",
                "title": "Multiple Underperforming Projects",
                "description": f"{underperforming} out of {total_projects} projects are underperforming.",
                "priority": "medium"
            })
        
        # Activity alerts
        activity_metrics = health_result.get("activity_metrics", {})
        recent_activity = activity_metrics.get("recent_activity", {})
        activity_rate = recent_activity.get("project_activity_rate", 100)
        
        if activity_rate < 25:
            alerts.append({
                "type": "info",
                "title": "Low Project Activity",
                "description": f"Only {activity_rate:.1f}% of projects have recent activity. Consider engagement review.",
                "priority": "low"
            })
        
        return alerts
        
    except Exception as e:
        print(f"Error generating alerts: {str(e)}")
        return [{"type": "error", "title": "Alert Generation Failed", "description": str(e), "priority": "medium"}]

def _generate_health_recommendations(health_result: Dict[str, Any], risk_assessment: Dict[str, Any]) -> List[str]:
    """Generate actionable health recommendations"""
    
    recommendations = []
    
    try:
        # Risk-based recommendations
        overall_risk = risk_assessment.get("overall_risk_level", "low")
        
        if overall_risk in ["critical", "high"]:
            recommendations.append("Immediate Action Required: Implement emergency project recovery procedures for critical health issues.")
        
        critical_risks = risk_assessment.get("critical_risks", [])
        if critical_risks:
            recommendations.append(f"Address {len(critical_risks)} critical risk factors immediately to prevent project failures.")
        
        # Project-specific recommendations
        project_risks = risk_assessment.get("project_risks", {})
        if project_risks:
            critical_projects = [pr for pr in project_risks.values() if pr["risk_level"] == "critical"]
            if critical_projects:
                recommendations.append(f"Prioritize recovery of {len(critical_projects)} critical projects: {', '.join([cp['project_name'] for cp in critical_projects[:3]])}")
        
        # Performance recommendations
        performance_indicators = health_result.get("performance_indicators", {})
        efficiency_metrics = performance_indicators.get("efficiency_metrics", {})
        
        avg_completion = efficiency_metrics.get("avg_completion_rate", 100)
        if avg_completion < 70:
            recommendations.append("Improve completion rates by implementing milestone tracking and progress reviews.")
        
        underperforming = efficiency_metrics.get("underperforming_projects", 0)
        if underperforming > 0:
            recommendations.append(f"Provide additional support and resources to {underperforming} underperforming projects.")
        
        # Quality recommendations
        quality_metrics = performance_indicators.get("quality_metrics", {})
        quality_score = quality_metrics.get("avg_requirement_quality_score", 100)
        
        if quality_score < 80:
            recommendations.append("Improve requirement quality through training, templates, and review processes.")
        
        # Activity recommendations
        activity_metrics = health_result.get("activity_metrics", {})
        recent_activity = activity_metrics.get("recent_activity", {})
        activity_rate = recent_activity.get("project_activity_rate", 100)
        
        if activity_rate < 50:
            recommendations.append("Increase project engagement through regular check-ins and stakeholder communication.")
        
        # Growth recommendations
        growth_trends = activity_metrics.get("growth_trends", {})
        new_projects = growth_trends.get("new_projects_last_30_days", 0)
        
        if new_projects == 0:
            recommendations.append("Consider initiating new projects to maintain organizational growth and momentum.")
        
        return recommendations
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return [f"Recommendation generation failed: {str(e)}"]

def _generate_health_overview(health_result: Dict[str, Any]) -> Dict[str, str]:
    """Generate high-level health overview"""
    
    overview = {}
    
    try:
        health_scores = health_result.get("health_scores", {})
        organization_metrics = health_result.get("organization_metrics", {})
        
        org_health = health_scores.get("organization_health_score", 0)
        total_projects = len(health_result.get("project_metrics", {}))
        total_requirements = organization_metrics.get("total_requirements", 0)
        
        # Health status
        if org_health >= 90:
            health_status = "Excellent"
        elif org_health >= 80:
            health_status = "Good"
        elif org_health >= 60:
            health_status = "Fair"
        else:
            health_status = "Poor"
        
        overview["health_status"] = f"Organization health: {org_health:.1f}% ({health_status})"
        overview["project_portfolio"] = f"Managing {total_projects} projects with {total_requirements} total requirements"
        
        # Project distribution
        health_distribution = health_scores.get("health_distribution", {})
        excellent = health_distribution.get("excellent", 0)
        poor = health_distribution.get("poor", 0)
        
        if excellent > 0 and poor == 0:
            overview["project_distribution"] = f"{excellent} projects in excellent health, no projects at risk"
        elif poor > 0:
            overview["project_distribution"] = f"{poor} projects need attention, {excellent} projects performing well"
        else:
            overview["project_distribution"] = "Mixed project health across portfolio"
        
        return overview
        
    except Exception as e:
        print(f"Error generating health overview: {str(e)}")
        return {"error": f"Overview generation failed: {str(e)}"}

def _generate_executive_summary(health_result: Dict[str, Any], kpi_dashboard: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, str]:
    """Generate executive summary for leadership"""
    
    summary = {}
    
    try:
        # Overall status
        health_scores = health_result.get("health_scores", {})
        org_health = health_scores.get("organization_health_score", 0)
        
        key_metrics = kpi_dashboard.get("key_metrics", {})
        total_projects = key_metrics.get("total_projects", 0)
        
        summary["status"] = f"Organization health at {org_health:.1f}% across {total_projects} projects"
        
        # Performance summary
        performance_indicators = kpi_dashboard.get("performance_indicators", {})
        completion_rate = performance_indicators.get("avg_completion_rate", 0)
        high_performing = performance_indicators.get("high_performing_projects", 0)
        
        summary["performance"] = f"Average completion rate: {completion_rate:.1f}% with {high_performing} high-performing projects"
        
        # Risk summary
        risk_level = risk_assessment.get("overall_risk_level", "unknown")
        critical_risks = len(risk_assessment.get("critical_risks", []))
        
        if critical_risks > 0:
            summary["risks"] = f"Risk level: {risk_level.title()} with {critical_risks} critical risks requiring immediate attention"
        else:
            summary["risks"] = f"Risk level: {risk_level.title()} with no critical risks identified"
        
        # Action items
        project_risks = risk_assessment.get("project_risks", {})
        if project_risks:
            summary["action_required"] = f"{len(project_risks)} projects require leadership attention and intervention"
        else:
            summary["action_required"] = "No immediate action required - all projects within acceptable parameters"
        
        return summary
        
    except Exception as e:
        print(f"Error generating executive summary: {str(e)}")
        return {"error": f"Executive summary generation failed: {str(e)}"}

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Generate comprehensive project health dashboard with KPIs and risk assessment"
    result = get_project_health_tool(test_org_id, test_message)
    print(f"Result: {result}")