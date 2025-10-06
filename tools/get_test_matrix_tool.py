"""Get test matrix tool module"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def get_test_matrix_tool(organization_id: str, message: str) -> Any:
    """
    Generate comprehensive test coverage matrices showing relationships between requirements and tests.
    Provides detailed analysis of test coverage gaps, execution status, and quality metrics.
    
    Parameters
    ----------
    organization_id : str
        User's individual organization ID
    message : str
        User's request message specifying matrix scope and format preferences
        
    Returns
    -------
    Any
        Result containing test matrix data, coverage analysis, and recommendations
    """
    print(f"[get_test_matrix] Starting with organization_id: {organization_id}")
    print(f"[get_test_matrix] Message: {message}")
    
    try:
        # Create Supabase client
        print("[get_test_matrix] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Parse matrix parameters from message
        matrix_params = _parse_matrix_parameters(message)
        
        print(f"[get_test_matrix] Matrix parameters: {matrix_params}")
        
        # Get organization projects for context
        projects_response = supabase.table("projects").select("id, name, description").eq("organization_id", organization_id).execute()
        
        if not projects_response.data:
            return {
                "json": {
                    "error": "No projects found for the organization",
                    "message": message
                }
            }
        
        # Generate comprehensive test matrix
        matrix_result = _generate_test_matrix(supabase, organization_id, projects_response.data, matrix_params)
        
        # Generate coverage analysis
        coverage_analysis = _analyze_test_coverage(matrix_result)
        
        # Generate quality insights
        quality_insights = _generate_quality_insights(matrix_result)
        
        # Generate recommendations
        recommendations = _generate_matrix_recommendations(matrix_result, coverage_analysis)
        
        result = {
            "json": {
                "organization_id": organization_id,
                "matrix_generated_at": datetime.now().isoformat(),
                "scope": matrix_params["scope"],
                "projects_included": len(projects_response.data),
                "test_matrix": matrix_result,
                "coverage_analysis": coverage_analysis,
                "quality_insights": quality_insights,
                "recommendations": recommendations,
                "matrix_summary": _generate_matrix_summary(matrix_result, coverage_analysis),
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[get_test_matrix] Saving result to JSON file...")
        with open("get_test_matrix_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("[get_test_matrix] SUCCESS: Completed successfully")
        return result
        
    except Exception as e:
        print(f"[get_test_matrix] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def _parse_matrix_parameters(message: str) -> Dict[str, Any]:
    """Parse message to determine matrix generation parameters"""
    message_lower = message.lower()
    
    params = {
        "scope": "all_projects",
        "include_execution_status": True,
        "include_coverage_gaps": True,
        "include_test_details": True,
        "group_by": "project",
        "format": "detailed"
    }
    
    # Determine scope
    if "project" in message_lower and any(word for word in message.split() if len(word) == 36 and "-" in word):
        params["scope"] = "single_project"
        # Extract project ID
        for word in message.split():
            if len(word) == 36 and "-" in word:
                params["project_id"] = word
                break
    
    # Determine grouping
    if "requirement" in message_lower:
        params["group_by"] = "requirement"
    elif "test" in message_lower:
        params["group_by"] = "test"
    elif "priority" in message_lower:
        params["group_by"] = "priority"
    elif "status" in message_lower:
        params["group_by"] = "status"
    
    # Determine format
    if "summary" in message_lower or "overview" in message_lower:
        params["format"] = "summary"
    elif "detailed" in message_lower:
        params["format"] = "detailed"
    
    # Special inclusions
    if "gap" in message_lower:
        params["focus"] = "gaps"
    elif "coverage" in message_lower:
        params["focus"] = "coverage"
    elif "execution" in message_lower:
        params["focus"] = "execution"
    
    return params

def _generate_test_matrix(supabase, organization_id: str, projects: List[Dict], params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive test matrix data"""
    
    matrix_data = {
        "requirements": {},
        "tests": {},
        "requirement_test_mappings": [],
        "coverage_matrix": {},
        "execution_matrix": {},
        "statistics": {}
    }
    
    try:
        # Filter projects if single project scope
        if params["scope"] == "single_project" and "project_id" in params:
            projects = [p for p in projects if p["id"] == params["project_id"]]
        
        # Get all requirements for selected projects
        all_requirements = _get_requirements_for_projects(supabase, projects)
        matrix_data["requirements"] = {req["id"]: req for req in all_requirements}
        
        # Get all tests for selected projects
        all_tests = _get_tests_for_projects(supabase, projects)
        matrix_data["tests"] = {test["id"]: test for test in all_tests}
        
        # Get requirement-test mappings
        mappings = _get_requirement_test_mappings(supabase, list(matrix_data["tests"].keys()))
        matrix_data["requirement_test_mappings"] = mappings
        
        # Build coverage matrix
        matrix_data["coverage_matrix"] = _build_coverage_matrix(
            matrix_data["requirements"], 
            matrix_data["tests"], 
            mappings
        )
        
        # Build execution matrix if requested
        if params["include_execution_status"]:
            matrix_data["execution_matrix"] = _build_execution_matrix(mappings)
        
        # Generate statistics
        matrix_data["statistics"] = _generate_matrix_statistics(
            matrix_data["requirements"],
            matrix_data["tests"],
            mappings
        )
        
        # Group data according to parameters
        if params["group_by"] != "none":
            matrix_data["grouped_data"] = _group_matrix_data(matrix_data, params["group_by"])
        
        return matrix_data
        
    except Exception as e:
        print(f"[get_test_matrix] Error generating matrix: {str(e)}")
        return {"error": f"Matrix generation failed: {str(e)}"}

def _get_requirements_for_projects(supabase, projects: List[Dict]) -> List[Dict]:
    """Get all requirements for the specified projects"""
    all_requirements = []
    
    try:
        for project in projects:
            # Get documents in project
            docs_response = supabase.table("documents").select("id, name").eq("project_id", project["id"]).execute()
            
            for doc in docs_response.data:
                # Get requirements in document
                reqs_response = supabase.table("requirements").select(
                    "id, name, description, status, priority, level, type, external_id"
                ).eq("document_id", doc["id"]).eq("is_deleted", False).execute()
                
                for req in reqs_response.data:
                    req["project_id"] = project["id"]
                    req["project_name"] = project["name"]
                    req["document_id"] = doc["id"]
                    req["document_name"] = doc["name"]
                    all_requirements.append(req)
        
        return all_requirements
        
    except Exception as e:
        print(f"Error getting requirements: {str(e)}")
        return []

def _get_tests_for_projects(supabase, projects: List[Dict]) -> List[Dict]:
    """Get all tests for the specified projects"""
    all_tests = []
    
    try:
        for project in projects:
            tests_response = supabase.table("test_req").select(
                "id, test_id, title, description, test_type, priority, status, method, is_active"
            ).eq("project_id", project["id"]).eq("is_active", True).execute()
            
            for test in tests_response.data:
                test["project_id"] = project["id"]
                test["project_name"] = project["name"]
                all_tests.append(test)
        
        return all_tests
        
    except Exception as e:
        print(f"Error getting tests: {str(e)}")
        return []

def _get_requirement_test_mappings(supabase, test_ids: List[str]) -> List[Dict]:
    """Get requirement-test mappings with execution status"""
    try:
        if not test_ids:
            return []
        
        mappings_response = supabase.table("requirement_tests").select(
            "id, requirement_id, test_id, execution_status, result_notes, executed_at, executed_by, execution_environment"
        ).in_("test_id", test_ids).execute()
        
        return mappings_response.data if mappings_response.data else []
        
    except Exception as e:
        print(f"Error getting mappings: {str(e)}")
        return []

def _build_coverage_matrix(requirements: Dict[str, Dict], tests: Dict[str, Dict], mappings: List[Dict]) -> Dict[str, Any]:
    """Build requirement-test coverage matrix"""
    
    coverage_matrix = {
        "requirements_with_tests": {},
        "tests_with_requirements": {},
        "uncovered_requirements": [],
        "unlinked_tests": []
    }
    
    # Build mapping indexes
    req_to_tests = {}
    test_to_reqs = {}
    
    for mapping in mappings:
        req_id = mapping["requirement_id"]
        test_id = mapping["test_id"]
        
        if req_id not in req_to_tests:
            req_to_tests[req_id] = []
        req_to_tests[req_id].append({
            "test_id": test_id,
            "test_title": tests.get(test_id, {}).get("title", "Unknown"),
            "test_type": tests.get(test_id, {}).get("test_type", "unknown"),
            "execution_status": mapping.get("execution_status", "not_executed")
        })
        
        if test_id not in test_to_reqs:
            test_to_reqs[test_id] = []
        test_to_reqs[test_id].append({
            "requirement_id": req_id,
            "requirement_name": requirements.get(req_id, {}).get("name", "Unknown"),
            "requirement_priority": requirements.get(req_id, {}).get("priority", "unknown")
        })
    
    # Build coverage data
    coverage_matrix["requirements_with_tests"] = req_to_tests
    coverage_matrix["tests_with_requirements"] = test_to_reqs
    
    # Find uncovered requirements
    for req_id, req_data in requirements.items():
        if req_id not in req_to_tests:
            coverage_matrix["uncovered_requirements"].append({
                "requirement_id": req_id,
                "requirement_name": req_data["name"],
                "priority": req_data.get("priority", "unknown"),
                "project_name": req_data.get("project_name", "Unknown")
            })
    
    # Find unlinked tests
    for test_id, test_data in tests.items():
        if test_id not in test_to_reqs:
            coverage_matrix["unlinked_tests"].append({
                "test_id": test_id,
                "test_title": test_data["title"],
                "test_type": test_data.get("test_type", "unknown"),
                "project_name": test_data.get("project_name", "Unknown")
            })
    
    return coverage_matrix

def _build_execution_matrix(mappings: List[Dict]) -> Dict[str, Any]:
    """Build test execution status matrix"""
    
    execution_matrix = {
        "execution_status_summary": {},
        "recent_executions": [],
        "execution_trends": {}
    }
    
    # Count execution statuses
    status_counts = {}
    recent_executions = []
    
    for mapping in mappings:
        status = mapping.get("execution_status", "not_executed")
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if mapping.get("executed_at"):
            recent_executions.append({
                "requirement_id": mapping["requirement_id"],
                "test_id": mapping["test_id"],
                "status": status,
                "executed_at": mapping["executed_at"],
                "executed_by": mapping.get("executed_by", "unknown"),
                "environment": mapping.get("execution_environment", "unknown")
            })
    
    # Sort recent executions by date
    recent_executions.sort(key=lambda x: x["executed_at"] or "", reverse=True)
    
    execution_matrix["execution_status_summary"] = status_counts
    execution_matrix["recent_executions"] = recent_executions[:20]  # Last 20 executions
    
    return execution_matrix

def _generate_matrix_statistics(requirements: Dict, tests: Dict, mappings: List[Dict]) -> Dict[str, Any]:
    """Generate comprehensive matrix statistics"""
    
    total_requirements = len(requirements)
    total_tests = len(tests)
    total_mappings = len(mappings)
    
    # Coverage statistics
    covered_requirements = len(set(m["requirement_id"] for m in mappings))
    coverage_percentage = (covered_requirements / total_requirements * 100) if total_requirements > 0 else 0
    
    # Test utilization
    used_tests = len(set(m["test_id"] for m in mappings))
    test_utilization = (used_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Execution statistics
    executed_mappings = [m for m in mappings if m.get("execution_status") not in ["not_executed", None]]
    execution_rate = (len(executed_mappings) / total_mappings * 100) if total_mappings > 0 else 0
    
    # Success rate
    passed_executions = [m for m in executed_mappings if m.get("execution_status") == "passed"]
    success_rate = (len(passed_executions) / len(executed_mappings) * 100) if executed_mappings else 0
    
    # Requirements by priority coverage
    priority_coverage = {}
    for req in requirements.values():
        priority = req.get("priority", "unknown")
        if priority not in priority_coverage:
            priority_coverage[priority] = {"total": 0, "covered": 0}
        priority_coverage[priority]["total"] += 1
        
        if any(m["requirement_id"] == req["id"] for m in mappings):
            priority_coverage[priority]["covered"] += 1
    
    # Add coverage percentages
    for priority_data in priority_coverage.values():
        priority_data["coverage_percentage"] = (
            priority_data["covered"] / priority_data["total"] * 100 
            if priority_data["total"] > 0 else 0
        )
    
    return {
        "total_requirements": total_requirements,
        "total_tests": total_tests,
        "total_mappings": total_mappings,
        "coverage_statistics": {
            "covered_requirements": covered_requirements,
            "uncovered_requirements": total_requirements - covered_requirements,
            "coverage_percentage": round(coverage_percentage, 1)
        },
        "test_utilization": {
            "used_tests": used_tests,
            "unused_tests": total_tests - used_tests,
            "utilization_percentage": round(test_utilization, 1)
        },
        "execution_statistics": {
            "executed_mappings": len(executed_mappings),
            "unexecuted_mappings": total_mappings - len(executed_mappings),
            "execution_rate_percentage": round(execution_rate, 1),
            "success_rate_percentage": round(success_rate, 1)
        },
        "priority_coverage": priority_coverage
    }

def _group_matrix_data(matrix_data: Dict, group_by: str) -> Dict[str, Any]:
    """Group matrix data by specified criteria"""
    
    grouped_data = {}
    
    if group_by == "project":
        # Group by project
        for req in matrix_data["requirements"].values():
            project_name = req.get("project_name", "Unknown")
            if project_name not in grouped_data:
                grouped_data[project_name] = {
                    "requirements": [],
                    "tests": [],
                    "mappings": []
                }
            grouped_data[project_name]["requirements"].append(req)
        
        for test in matrix_data["tests"].values():
            project_name = test.get("project_name", "Unknown")
            if project_name not in grouped_data:
                grouped_data[project_name] = {
                    "requirements": [],
                    "tests": [],
                    "mappings": []
                }
            grouped_data[project_name]["tests"].append(test)
    
    elif group_by == "priority":
        # Group by priority
        for req in matrix_data["requirements"].values():
            priority = req.get("priority", "unknown")
            if priority not in grouped_data:
                grouped_data[priority] = {
                    "requirements": [],
                    "coverage": {"covered": 0, "total": 0}
                }
            grouped_data[priority]["requirements"].append(req)
            grouped_data[priority]["coverage"]["total"] += 1
            
            # Check if covered
            if any(m["requirement_id"] == req["id"] for m in matrix_data["requirement_test_mappings"]):
                grouped_data[priority]["coverage"]["covered"] += 1
    
    return grouped_data

def _analyze_test_coverage(matrix_result: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze test coverage from matrix result"""
    
    if "error" in matrix_result:
        return {"error": "Cannot analyze coverage due to matrix generation error"}
    
    stats = matrix_result.get("statistics", {})
    coverage_matrix = matrix_result.get("coverage_matrix", {})
    
    analysis = {
        "overall_coverage": stats.get("coverage_statistics", {}),
        "coverage_gaps": {
            "high_priority_uncovered": [],
            "critical_gaps": [],
            "recommendations_priority": []
        },
        "test_efficiency": {
            "test_utilization": stats.get("test_utilization", {}),
            "duplicate_coverage": [],
            "over_tested_requirements": []
        }
    }
    
    # Analyze high-priority uncovered requirements
    uncovered = coverage_matrix.get("uncovered_requirements", [])
    high_priority_uncovered = [
        req for req in uncovered 
        if req.get("priority") in ["high", "critical"]
    ]
    analysis["coverage_gaps"]["high_priority_uncovered"] = high_priority_uncovered
    
    # Find over-tested requirements (more than 3 tests)
    req_test_counts = {}
    for mapping in matrix_result.get("requirement_test_mappings", []):
        req_id = mapping["requirement_id"]
        req_test_counts[req_id] = req_test_counts.get(req_id, 0) + 1
    
    over_tested = [
        {"requirement_id": req_id, "test_count": count}
        for req_id, count in req_test_counts.items()
        if count > 3
    ]
    analysis["test_efficiency"]["over_tested_requirements"] = over_tested
    
    return analysis

def _generate_quality_insights(matrix_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate quality insights from matrix data"""
    
    if "error" in matrix_result:
        return {"error": "Cannot generate insights due to matrix error"}
    
    insights = {
        "test_distribution": {},
        "execution_patterns": {},
        "risk_assessment": {}
    }
    
    # Test type distribution
    test_types = {}
    for test in matrix_result.get("tests", {}).values():
        test_type = test.get("test_type", "unknown")
        test_types[test_type] = test_types.get(test_type, 0) + 1
    
    insights["test_distribution"]["by_type"] = test_types
    
    # Execution patterns
    execution_matrix = matrix_result.get("execution_matrix", {})
    insights["execution_patterns"] = execution_matrix.get("execution_status_summary", {})
    
    # Risk assessment based on coverage and execution
    stats = matrix_result.get("statistics", {})
    coverage_pct = stats.get("coverage_statistics", {}).get("coverage_percentage", 0)
    execution_pct = stats.get("execution_statistics", {}).get("execution_rate_percentage", 0)
    success_pct = stats.get("execution_statistics", {}).get("success_rate_percentage", 0)
    
    risk_level = "low"
    if coverage_pct < 70 or execution_pct < 50 or success_pct < 80:
        risk_level = "high"
    elif coverage_pct < 85 or execution_pct < 70 or success_pct < 90:
        risk_level = "medium"
    
    insights["risk_assessment"] = {
        "overall_risk": risk_level,
        "coverage_risk": coverage_pct < 80,
        "execution_risk": execution_pct < 60,
        "quality_risk": success_pct < 85
    }
    
    return insights

def _generate_matrix_recommendations(matrix_result: Dict[str, Any], coverage_analysis: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations based on matrix analysis"""
    
    recommendations = []
    
    if "error" in matrix_result or "error" in coverage_analysis:
        return ["Unable to generate recommendations due to analysis errors"]
    
    # Coverage-based recommendations
    coverage_stats = matrix_result.get("statistics", {}).get("coverage_statistics", {})
    coverage_pct = coverage_stats.get("coverage_percentage", 0)
    
    if coverage_pct < 70:
        recommendations.append("Critical: Low test coverage detected. Create additional test cases to achieve minimum 80% coverage.")
    elif coverage_pct < 85:
        recommendations.append("Moderate: Test coverage below recommended threshold. Consider adding tests for uncovered requirements.")
    
    # High-priority gaps
    high_priority_uncovered = coverage_analysis.get("coverage_gaps", {}).get("high_priority_uncovered", [])
    if high_priority_uncovered:
        recommendations.append(f"High Priority: {len(high_priority_uncovered)} high-priority requirements lack test coverage. Address these immediately.")
    
    # Test utilization
    test_util = matrix_result.get("statistics", {}).get("test_utilization", {})
    util_pct = test_util.get("utilization_percentage", 0)
    
    if util_pct < 60:
        unused_tests = test_util.get("unused_tests", 0)
        recommendations.append(f"Test Efficiency: {unused_tests} tests are not linked to requirements. Consider linking or removing unused tests.")
    
    # Execution recommendations
    execution_stats = matrix_result.get("statistics", {}).get("execution_statistics", {})
    execution_rate = execution_stats.get("execution_rate_percentage", 0)
    success_rate = execution_stats.get("success_rate_percentage", 0)
    
    if execution_rate < 50:
        recommendations.append("Execution Gap: Low test execution rate. Implement regular test execution cycles.")
    
    if success_rate < 80:
        recommendations.append("Quality Alert: Low test success rate indicates potential quality issues. Review failing tests.")
    
    # Over-testing recommendations
    over_tested = coverage_analysis.get("test_efficiency", {}).get("over_tested_requirements", [])
    if over_tested:
        recommendations.append(f"Efficiency: {len(over_tested)} requirements have excessive test coverage. Consider consolidating tests.")
    
    return recommendations

def _generate_matrix_summary(matrix_result: Dict[str, Any], coverage_analysis: Dict[str, Any]) -> Dict[str, str]:
    """Generate human-readable matrix summary"""
    
    if "error" in matrix_result:
        return {"error": "Matrix generation failed"}
    
    stats = matrix_result.get("statistics", {})
    
    summary = {}
    
    # Overall summary
    total_reqs = stats.get("total_requirements", 0)
    total_tests = stats.get("total_tests", 0)
    total_mappings = stats.get("total_mappings", 0)
    
    summary["overview"] = f"Matrix contains {total_reqs} requirements, {total_tests} tests, and {total_mappings} requirement-test relationships"
    
    # Coverage summary
    coverage_stats = stats.get("coverage_statistics", {})
    coverage_pct = coverage_stats.get("coverage_percentage", 0)
    uncovered = coverage_stats.get("uncovered_requirements", 0)
    
    summary["coverage"] = f"Test coverage: {coverage_pct:.1f}% ({uncovered} requirements uncovered)"
    
    # Execution summary
    execution_stats = stats.get("execution_statistics", {})
    execution_pct = execution_stats.get("execution_rate_percentage", 0)
    success_pct = execution_stats.get("success_rate_percentage", 0)
    
    summary["execution"] = f"Execution rate: {execution_pct:.1f}% with {success_pct:.1f}% success rate"
    
    return summary

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Generate detailed test matrix for all projects with coverage analysis"
    result = get_test_matrix_tool(test_org_id, test_message)
    print(f"Result: {result}")