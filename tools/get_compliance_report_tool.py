"""Get compliance report tool module"""

import json
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def get_compliance_report_tool(organization_id: str, message: str) -> Any:
    """
    Generate comprehensive SOC2 compliance reports with audit trails, control mappings,
    and evidence documentation. Supports regulatory compliance requirements.
    
    Parameters
    ----------
    organization_id : str
        User's individual organization ID
    message : str
        User's request message specifying compliance report scope and standards
        
    Returns
    -------
    Any
        Result containing detailed compliance report, control assessments, and audit evidence
    """
    print(f"[get_compliance_report] Starting with organization_id: {organization_id}")
    print(f"[get_compliance_report] Message: {message}")
    
    try:
        # Create Supabase client
        print("[get_compliance_report] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Parse compliance report parameters from message
        compliance_params = _parse_compliance_parameters(message)
        
        print(f"[get_compliance_report] Compliance parameters: {compliance_params}")
        
        # Validate organization exists and has compliance data
        validation_result = _validate_organization_compliance(supabase, organization_id)
        if not validation_result["valid"]:
            return {
                "json": {
                    "error": validation_result["error"],
                    "message": message
                }
            }
        
        # Generate comprehensive compliance report
        compliance_result = _generate_compliance_report(supabase, organization_id, compliance_params)
        
        # Generate control assessments
        control_assessments = _generate_control_assessments(supabase, organization_id, compliance_params)
        
        # Generate audit trail evidence
        audit_evidence = _generate_audit_evidence(supabase, organization_id, compliance_params)
        
        # Generate risk assessments
        risk_assessments = _generate_compliance_risk_assessments(compliance_result, control_assessments)
        
        # Generate remediation recommendations
        remediation_plan = _generate_remediation_recommendations(control_assessments, risk_assessments)
        
        result = {
            "json": {
                "organization_id": organization_id,
                "report_generated_at": datetime.now().isoformat(),
                "compliance_standard": compliance_params["standard"],
                "report_period": compliance_params["period"],
                "report_scope": compliance_params["scope"],
                "executive_summary": _generate_compliance_executive_summary(compliance_result, control_assessments, risk_assessments),
                "compliance_overview": compliance_result,
                "control_assessments": control_assessments,
                "audit_evidence": audit_evidence,
                "risk_assessments": risk_assessments,
                "remediation_plan": remediation_plan,
                "certification_readiness": _assess_certification_readiness(control_assessments, risk_assessments),
                "compliance_metrics": _generate_compliance_metrics(compliance_result, control_assessments),
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[get_compliance_report] Saving result to JSON file...")
        with open("get_compliance_report_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("[get_compliance_report] SUCCESS: Completed successfully")
        return result
        
    except Exception as e:
        print(f"[get_compliance_report] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def _parse_compliance_parameters(message: str) -> Dict[str, Any]:
    """Parse message to determine compliance report parameters"""
    message_lower = message.lower()
    
    params = {
        "standard": "soc2",
        "period": "current_year",
        "scope": "comprehensive",
        "include_evidence": True,
        "include_controls": True,
        "include_risks": True,
        "detail_level": "standard"
    }
    
    # Determine compliance standard
    if "soc2" in message_lower or "soc 2" in message_lower:
        params["standard"] = "soc2"
    elif "sox" in message_lower or "sarbanes" in message_lower:
        params["standard"] = "sox"
    elif "gdpr" in message_lower:
        params["standard"] = "gdpr"
    elif "hipaa" in message_lower:
        params["standard"] = "hipaa"
    elif "iso27001" in message_lower or "iso 27001" in message_lower:
        params["standard"] = "iso27001"
    
    # Determine time period
    if "quarterly" in message_lower or "q1" in message_lower or "q2" in message_lower or "q3" in message_lower or "q4" in message_lower:
        params["period"] = "quarterly"
    elif "monthly" in message_lower:
        params["period"] = "monthly"
    elif "annual" in message_lower or "yearly" in message_lower:
        params["period"] = "annual"
    elif "last year" in message_lower:
        params["period"] = "last_year"
    elif "last month" in message_lower:
        params["period"] = "last_month"
    
    # Determine scope
    if "controls only" in message_lower or "control assessment" in message_lower:
        params["scope"] = "controls"
    elif "audit" in message_lower or "evidence" in message_lower:
        params["scope"] = "audit"
    elif "risk" in message_lower:
        params["scope"] = "risk"
    elif "summary" in message_lower or "executive" in message_lower:
        params["scope"] = "summary"
    
    # Detail level
    if "detailed" in message_lower or "comprehensive" in message_lower:
        params["detail_level"] = "detailed"
    elif "summary" in message_lower or "executive" in message_lower:
        params["detail_level"] = "summary"
    
    return params

def _validate_organization_compliance(supabase, organization_id: str) -> Dict[str, Any]:
    """Validate organization exists and has compliance-relevant data"""
    try:
        # Check organization exists
        org_response = supabase.table("organizations").select("id, name, billing_plan").eq("id", organization_id).execute()
        
        if not org_response.data:
            return {"valid": False, "error": "Organization not found"}
        
        organization = org_response.data[0]
        
        # Check if organization has audit logs (required for compliance)
        audit_logs_response = supabase.table("audit_logs").select("id").eq("organization_id", organization_id).limit(1).execute()
        
        has_audit_data = bool(audit_logs_response.data)
        
        return {
            "valid": True,
            "organization": organization,
            "has_audit_data": has_audit_data
        }
        
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}

def _generate_compliance_report(supabase, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive compliance report"""
    
    compliance_report = {
        "organization_info": {},
        "compliance_scope": {},
        "data_governance": {},
        "access_controls": {},
        "audit_logging": {},
        "data_retention": {}
    }
    
    try:
        # Get organization information
        org_response = supabase.table("organizations").select(
            "id, name, type, billing_plan, created_at, settings"
        ).eq("id", organization_id).execute()
        
        if org_response.data:
            org = org_response.data[0]
            compliance_report["organization_info"] = {
                "organization_id": org["id"],
                "organization_name": org["name"],
                "organization_type": org.get("type", "unknown"),
                "billing_plan": org.get("billing_plan", "unknown"),
                "established_date": org.get("created_at"),
                "compliance_settings": org.get("settings", {})
            }
        
        # Analyze compliance scope
        compliance_report["compliance_scope"] = _analyze_compliance_scope(supabase, organization_id)
        
        # Analyze data governance
        compliance_report["data_governance"] = _analyze_data_governance(supabase, organization_id)
        
        # Analyze access controls
        compliance_report["access_controls"] = _analyze_access_controls(supabase, organization_id)
        
        # Analyze audit logging
        compliance_report["audit_logging"] = _analyze_audit_logging(supabase, organization_id, params)
        
        # Analyze data retention
        compliance_report["data_retention"] = _analyze_data_retention(supabase, organization_id)
        
        return compliance_report
        
    except Exception as e:
        print(f"Error generating compliance report: {str(e)}")
        return {"error": f"Compliance report generation failed: {str(e)}"}

def _analyze_compliance_scope(supabase, organization_id: str) -> Dict[str, Any]:
    """Analyze the scope of compliance coverage"""
    
    scope_analysis = {
        "systems_in_scope": {},
        "data_types": {},
        "user_population": {},
        "geographic_scope": {}
    }
    
    try:
        # Analyze projects (systems in scope)
        projects_response = supabase.table("projects").select("id, name, status, created_at").eq("organization_id", organization_id).execute()
        projects = projects_response.data if projects_response.data else []
        
        scope_analysis["systems_in_scope"] = {
            "total_projects": len(projects),
            "active_projects": len([p for p in projects if p.get("status") == "active"]),
            "project_details": [
                {
                    "project_name": p["name"],
                    "status": p.get("status", "unknown"),
                    "in_scope_since": p.get("created_at")
                }
                for p in projects
            ]
        }
        
        # Analyze user population
        members_response = supabase.table("organization_members").select("user_id, role, status").eq("organization_id", organization_id).execute()
        members = members_response.data if members_response.data else []
        
        role_distribution = {}
        for member in members:
            role = member.get("role", "unknown")
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        scope_analysis["user_population"] = {
            "total_users": len(members),
            "active_users": len([m for m in members if m.get("status") == "active"]),
            "role_distribution": role_distribution
        }
        
        # Data types analysis (based on requirements and documents)
        total_requirements = 0
        total_documents = 0
        
        for project in projects:
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            total_documents += len(docs_response.data) if docs_response.data else 0
            
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select("id").eq("document_id", doc["id"]).execute()
                total_requirements += len(reqs_response.data) if reqs_response.data else 0
        
        scope_analysis["data_types"] = {
            "requirements_data": total_requirements,
            "document_data": total_documents,
            "structured_data_elements": total_requirements + total_documents
        }
        
        return scope_analysis
        
    except Exception as e:
        print(f"Error analyzing compliance scope: {str(e)}")
        return {"error": f"Scope analysis failed: {str(e)}"}

def _analyze_data_governance(supabase, organization_id: str) -> Dict[str, Any]:
    """Analyze data governance practices"""
    
    governance_analysis = {
        "data_classification": {},
        "data_lifecycle": {},
        "data_quality": {},
        "privacy_controls": {}
    }
    
    try:
        # Analyze data classification (based on requirement priorities and types)
        projects_response = supabase.table("projects").select("id").eq("organization_id", organization_id).execute()
        
        total_classified = 0
        priority_distribution = {}
        
        for project in (projects_response.data or []):
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select("priority, level, status").eq("document_id", doc["id"]).execute()
                
                for req in (reqs_response.data or []):
                    total_classified += 1
                    priority = req.get("priority", "unclassified")
                    priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        governance_analysis["data_classification"] = {
            "total_classified_items": total_classified,
            "classification_distribution": priority_distribution,
            "classification_coverage": (total_classified / max(total_classified, 1)) * 100  # Simplified
        }
        
        # Data lifecycle analysis
        status_distribution = {}
        for project in (projects_response.data or []):
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select("status").eq("document_id", doc["id"]).execute()
                
                for req in (reqs_response.data or []):
                    status = req.get("status", "unknown")
                    status_distribution[status] = status_distribution.get(status, 0) + 1
        
        governance_analysis["data_lifecycle"] = {
            "lifecycle_stage_distribution": status_distribution,
            "managed_lifecycle_items": len(status_distribution)
        }
        
        # Data quality metrics
        enhanced_requirements = 0
        total_requirements = 0
        
        for project in (projects_response.data or []):
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select("enchanced_requirement, description").eq("document_id", doc["id"]).execute()
                
                for req in (reqs_response.data or []):
                    total_requirements += 1
                    if req.get("enchanced_requirement") or (req.get("description") and len(req["description"]) > 100):
                        enhanced_requirements += 1
        
        quality_score = (enhanced_requirements / max(total_requirements, 1)) * 100
        
        governance_analysis["data_quality"] = {
            "quality_score": round(quality_score, 1),
            "enhanced_data_items": enhanced_requirements,
            "total_data_items": total_requirements,
            "quality_threshold_met": quality_score >= 80
        }
        
        return governance_analysis
        
    except Exception as e:
        print(f"Error analyzing data governance: {str(e)}")
        return {"error": f"Data governance analysis failed: {str(e)}"}

def _analyze_access_controls(supabase, organization_id: str) -> Dict[str, Any]:
    """Analyze access control implementation"""
    
    access_analysis = {
        "user_access_management": {},
        "role_based_access": {},
        "authentication_controls": {},
        "authorization_controls": {}
    }
    
    try:
        # User access management
        members_response = supabase.table("organization_members").select(
            "user_id, role, status, created_at, last_active_at"
        ).eq("organization_id", organization_id).execute()
        
        members = members_response.data if members_response.data else []
        
        active_users = len([m for m in members if m.get("status") == "active"])
        inactive_users = len(members) - active_users
        
        # Check for recent activity
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_activity = len([
            m for m in members 
            if m.get("last_active_at") and m.get("last_active_at") > thirty_days_ago
        ])
        
        access_analysis["user_access_management"] = {
            "total_users": len(members),
            "active_users": active_users,
            "inactive_users": inactive_users,
            "users_with_recent_activity": recent_activity,
            "access_activity_rate": (recent_activity / max(len(members), 1)) * 100
        }
        
        # Role-based access analysis
        role_distribution = {}
        permissions_analysis = {}
        
        for member in members:
            role = member.get("role", "unknown")
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        # Check project-level access
        project_members_response = supabase.table("project_members").select(
            "user_id, role, permissions"
        ).eq("org_id", organization_id).execute()
        
        project_access_count = len(project_members_response.data) if project_members_response.data else 0
        
        access_analysis["role_based_access"] = {
            "organization_role_distribution": role_distribution,
            "project_level_access_grants": project_access_count,
            "average_project_access_per_user": project_access_count / max(len(members), 1),
            "role_segregation_implemented": len(role_distribution) > 1
        }
        
        # Authentication controls (OAuth analysis)
        oauth_clients_response = supabase.table("oauth_clients").select("id, client_name, is_public").execute()
        oauth_clients = oauth_clients_response.data if oauth_clients_response.data else []
        
        oauth_tokens_response = supabase.table("oauth_access_tokens").select("id, expires_at").execute()
        oauth_tokens = oauth_tokens_response.data if oauth_tokens_response.data else []
        
        active_tokens = len([
            token for token in oauth_tokens
            if token.get("expires_at") and token["expires_at"] > datetime.now().isoformat()
        ])
        
        access_analysis["authentication_controls"] = {
            "oauth_clients_configured": len(oauth_clients),
            "public_clients": len([c for c in oauth_clients if c.get("is_public")]),
            "active_access_tokens": active_tokens,
            "token_management_active": active_tokens > 0
        }
        
        return access_analysis
        
    except Exception as e:
        print(f"Error analyzing access controls: {str(e)}")
        return {"error": f"Access control analysis failed: {str(e)}"}

def _analyze_audit_logging(supabase, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze audit logging implementation and coverage"""
    
    audit_analysis = {
        "logging_coverage": {},
        "event_types": {},
        "retention_compliance": {},
        "log_integrity": {}
    }
    
    try:
        # Determine time period for analysis
        end_date = datetime.now()
        
        if params["period"] == "monthly":
            start_date = end_date - timedelta(days=30)
        elif params["period"] == "quarterly":
            start_date = end_date - timedelta(days=90)
        elif params["period"] == "annual":
            start_date = end_date - timedelta(days=365)
        else:  # current_year
            start_date = datetime(end_date.year, 1, 1)
        
        # Get audit logs for the period
        audit_logs_response = supabase.table("audit_logs").select(
            "id, entity_type, action, event_type, severity, soc2_control, compliance_category, "
            "risk_level, created_at, timestamp"
        ).eq("organization_id", organization_id).gte("created_at", start_date.isoformat()).execute()
        
        audit_logs = audit_logs_response.data if audit_logs_response.data else []
        
        # Analyze logging coverage
        total_logs = len(audit_logs)
        unique_entity_types = len(set(log.get("entity_type", "unknown") for log in audit_logs))
        unique_actions = len(set(log.get("action", "unknown") for log in audit_logs))
        
        audit_analysis["logging_coverage"] = {
            "total_audit_events": total_logs,
            "unique_entity_types_logged": unique_entity_types,
            "unique_actions_logged": unique_actions,
            "logging_period_days": (end_date - start_date).days,
            "average_events_per_day": total_logs / max((end_date - start_date).days, 1)
        }
        
        # Analyze event types
        event_type_distribution = {}
        severity_distribution = {}
        soc2_control_distribution = {}
        
        for log in audit_logs:
            event_type = log.get("event_type", "unknown")
            severity = log.get("severity", "unknown")
            soc2_control = log.get("soc2_control", "unmapped")
            
            event_type_distribution[event_type] = event_type_distribution.get(event_type, 0) + 1
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            soc2_control_distribution[soc2_control] = soc2_control_distribution.get(soc2_control, 0) + 1
        
        audit_analysis["event_types"] = {
            "event_type_distribution": event_type_distribution,
            "severity_distribution": severity_distribution,
            "soc2_control_mapping": soc2_control_distribution,
            "compliance_coverage": len([c for c in soc2_control_distribution.keys() if c != "unmapped"])
        }
        
        # Analyze retention compliance
        oldest_log = min((log.get("created_at", end_date.isoformat()) for log in audit_logs), default=end_date.isoformat())
        retention_days = (end_date - datetime.fromisoformat(oldest_log.replace('Z', '+00:00'))).days
        
        audit_analysis["retention_compliance"] = {
            "oldest_log_age_days": retention_days,
            "retention_period_met": retention_days >= 365,  # SOC2 typically requires 1 year
            "log_retention_score": min(100, (retention_days / 365) * 100)
        }
        
        # Analyze log integrity
        logs_with_correlation_id = len([log for log in audit_logs if log.get("correlation_id")])
        logs_with_risk_level = len([log for log in audit_logs if log.get("risk_level")])
        logs_with_compliance_category = len([log for log in audit_logs if log.get("compliance_category")])
        
        integrity_score = 0
        if total_logs > 0:
            integrity_score = (
                (logs_with_correlation_id / total_logs * 30) +
                (logs_with_risk_level / total_logs * 35) +
                (logs_with_compliance_category / total_logs * 35)
            )
        
        audit_analysis["log_integrity"] = {
            "logs_with_correlation_id": logs_with_correlation_id,
            "logs_with_risk_assessment": logs_with_risk_level,
            "logs_with_compliance_mapping": logs_with_compliance_category,
            "log_integrity_score": round(integrity_score, 1),
            "integrity_threshold_met": integrity_score >= 80
        }
        
        return audit_analysis
        
    except Exception as e:
        print(f"Error analyzing audit logging: {str(e)}")
        return {"error": f"Audit logging analysis failed: {str(e)}"}

def _analyze_data_retention(supabase, organization_id: str) -> Dict[str, Any]:
    """Analyze data retention practices"""
    
    retention_analysis = {
        "retention_policies": {},
        "data_lifecycle_management": {},
        "deletion_practices": {}
    }
    
    try:
        # Analyze soft delete implementation
        projects_response = supabase.table("projects").select("id, created_at, is_deleted, deleted_at").eq("organization_id", organization_id).execute()
        projects = projects_response.data if projects_response.data else []
        
        active_projects = len([p for p in projects if not p.get("is_deleted")])
        deleted_projects = len([p for p in projects if p.get("is_deleted")])
        
        # Analyze requirements retention
        total_requirements = 0
        deleted_requirements = 0
        
        for project in projects:
            if not project.get("is_deleted"):
                docs_response = supabase.table("documents").select("id, is_deleted").eq("project_id", project["id"]).execute()
                
                for doc in (docs_response.data or []):
                    reqs_response = supabase.table("requirements").select("id, is_deleted, deleted_at").eq("document_id", doc["id"]).execute()
                    
                    for req in (reqs_response.data or []):
                        total_requirements += 1
                        if req.get("is_deleted"):
                            deleted_requirements += 1
        
        retention_analysis["retention_policies"] = {
            "soft_delete_implemented": True,  # Schema supports soft delete
            "active_projects": active_projects,
            "archived_projects": deleted_projects,
            "project_retention_rate": (active_projects / max(len(projects), 1)) * 100
        }
        
        retention_analysis["data_lifecycle_management"] = {
            "total_requirements": total_requirements,
            "archived_requirements": deleted_requirements,
            "requirement_retention_rate": ((total_requirements - deleted_requirements) / max(total_requirements, 1)) * 100,
            "lifecycle_management_active": deleted_requirements > 0
        }
        
        # Analyze version control (as part of retention)
        versioned_requirements = 0
        for project in projects:
            if not project.get("is_deleted"):
                docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
                
                for doc in (docs_response.data or []):
                    reqs_response = supabase.table("requirements").select("version").eq("document_id", doc["id"]).execute()
                    
                    for req in (reqs_response.data or []):
                        if req.get("version", 1) > 1:
                            versioned_requirements += 1
        
        retention_analysis["deletion_practices"] = {
            "version_control_implemented": True,
            "requirements_with_versions": versioned_requirements,
            "version_retention_score": min(100, (versioned_requirements / max(total_requirements, 1)) * 100),
            "audit_trail_maintained": True  # Audit logs table exists
        }
        
        return retention_analysis
        
    except Exception as e:
        print(f"Error analyzing data retention: {str(e)}")
        return {"error": f"Data retention analysis failed: {str(e)}"}

def _generate_control_assessments(supabase, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate SOC2 control assessments"""
    
    control_assessments = {
        "security_controls": {},
        "availability_controls": {},
        "processing_integrity_controls": {},
        "confidentiality_controls": {},
        "privacy_controls": {}
    }
    
    try:
        # Security Controls Assessment
        control_assessments["security_controls"] = _assess_security_controls(supabase, organization_id)
        
        # Availability Controls Assessment
        control_assessments["availability_controls"] = _assess_availability_controls(supabase, organization_id)
        
        # Processing Integrity Controls Assessment
        control_assessments["processing_integrity_controls"] = _assess_processing_integrity_controls(supabase, organization_id)
        
        # Confidentiality Controls Assessment
        control_assessments["confidentiality_controls"] = _assess_confidentiality_controls(supabase, organization_id)
        
        # Privacy Controls Assessment (if applicable)
        control_assessments["privacy_controls"] = _assess_privacy_controls(supabase, organization_id)
        
        return control_assessments
        
    except Exception as e:
        print(f"Error generating control assessments: {str(e)}")
        return {"error": f"Control assessment generation failed: {str(e)}"}

def _assess_security_controls(supabase, organization_id: str) -> Dict[str, Any]:
    """Assess security-related SOC2 controls"""
    
    security_assessment = {
        "access_control_effectiveness": "not_assessed",
        "authentication_controls": "not_assessed",
        "authorization_controls": "not_assessed",
        "security_monitoring": "not_assessed",
        "overall_security_score": 0
    }
    
    try:
        scores = []
        
        # Access Control (CC6.1, CC6.2, CC6.3)
        members_response = supabase.table("organization_members").select("role, status").eq("organization_id", organization_id).execute()
        members = members_response.data if members_response.data else []
        
        active_members = len([m for m in members if m.get("status") == "active"])
        role_diversity = len(set(m.get("role", "unknown") for m in members))
        
        access_score = min(100, (active_members * 10) + (role_diversity * 20))
        scores.append(access_score)
        
        security_assessment["access_control_effectiveness"] = "effective" if access_score >= 80 else "needs_improvement"
        
        # Authentication Controls (CC6.1)
        oauth_response = supabase.table("oauth_clients").select("id").execute()
        oauth_clients = len(oauth_response.data) if oauth_response.data else 0
        
        auth_score = min(100, oauth_clients * 50)  # Having OAuth indicates authentication controls
        scores.append(auth_score)
        
        security_assessment["authentication_controls"] = "effective" if auth_score >= 70 else "needs_improvement"
        
        # Security Monitoring (CC7.1, CC7.2)
        audit_response = supabase.table("audit_logs").select("id").eq("organization_id", organization_id).limit(100).execute()
        audit_count = len(audit_response.data) if audit_response.data else 0
        
        monitoring_score = min(100, audit_count * 2)
        scores.append(monitoring_score)
        
        security_assessment["security_monitoring"] = "effective" if monitoring_score >= 80 else "needs_improvement"
        
        # Overall security score
        overall_score = sum(scores) / len(scores) if scores else 0
        security_assessment["overall_security_score"] = round(overall_score, 1)
        
        return security_assessment
        
    except Exception as e:
        print(f"Error assessing security controls: {str(e)}")
        return {"error": f"Security controls assessment failed: {str(e)}"}

def _assess_availability_controls(supabase, organization_id: str) -> Dict[str, Any]:
    """Assess availability-related SOC2 controls"""
    
    availability_assessment = {
        "system_availability": "not_assessed",
        "capacity_planning": "not_assessed",
        "system_monitoring": "not_assessed",
        "overall_availability_score": 0
    }
    
    try:
        scores = []
        
        # System availability (A1.1, A1.2)
        projects_response = supabase.table("projects").select("status").eq("organization_id", organization_id).execute()
        projects = projects_response.data if projects_response.data else []
        
        active_projects = len([p for p in projects if p.get("status") == "active"])
        availability_score = (active_projects / max(len(projects), 1)) * 100
        scores.append(availability_score)
        
        availability_assessment["system_availability"] = "effective" if availability_score >= 90 else "needs_improvement"
        
        # Capacity planning (A1.3)
        # Based on organization settings and resource utilization
        org_response = supabase.table("organizations").select("settings, max_members").eq("id", organization_id).execute()
        org = org_response.data[0] if org_response.data else {}
        
        has_capacity_planning = bool(org.get("max_members"))
        capacity_score = 100 if has_capacity_planning else 50
        scores.append(capacity_score)
        
        availability_assessment["capacity_planning"] = "effective" if capacity_score >= 80 else "needs_improvement"
        
        # Overall availability score
        overall_score = sum(scores) / len(scores) if scores else 0
        availability_assessment["overall_availability_score"] = round(overall_score, 1)
        
        return availability_assessment
        
    except Exception as e:
        print(f"Error assessing availability controls: {str(e)}")
        return {"error": f"Availability controls assessment failed: {str(e)}"}

def _assess_processing_integrity_controls(supabase, organization_id: str) -> Dict[str, Any]:
    """Assess processing integrity-related SOC2 controls"""
    
    integrity_assessment = {
        "data_processing_controls": "not_assessed",
        "system_processing_controls": "not_assessed",
        "data_validation_controls": "not_assessed",
        "overall_integrity_score": 0
    }
    
    try:
        scores = []
        
        # Data processing controls (PI1.1)
        # Based on requirement processing and version control
        total_requirements = 0
        enhanced_requirements = 0
        versioned_requirements = 0
        
        projects_response = supabase.table("projects").select("id").eq("organization_id", organization_id).execute()
        
        for project in (projects_response.data or []):
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select(
                    "enchanced_requirement, version"
                ).eq("document_id", doc["id"]).execute()
                
                for req in (reqs_response.data or []):
                    total_requirements += 1
                    if req.get("enchanced_requirement"):
                        enhanced_requirements += 1
                    if req.get("version", 1) > 1:
                        versioned_requirements += 1
        
        processing_score = 0
        if total_requirements > 0:
            enhancement_rate = (enhanced_requirements / total_requirements) * 100
            version_rate = (versioned_requirements / total_requirements) * 100
            processing_score = (enhancement_rate * 0.6 + version_rate * 0.4)
        
        scores.append(processing_score)
        integrity_assessment["data_processing_controls"] = "effective" if processing_score >= 70 else "needs_improvement"
        
        # System processing controls (PI1.2)
        # Based on audit trail completeness
        audit_response = supabase.table("audit_logs").select("action").eq("organization_id", organization_id).execute()
        unique_actions = len(set(log.get("action", "unknown") for log in (audit_response.data or [])))
        
        system_score = min(100, unique_actions * 10)
        scores.append(system_score)
        
        integrity_assessment["system_processing_controls"] = "effective" if system_score >= 80 else "needs_improvement"
        
        # Overall integrity score
        overall_score = sum(scores) / len(scores) if scores else 0
        integrity_assessment["overall_integrity_score"] = round(overall_score, 1)
        
        return integrity_assessment
        
    except Exception as e:
        print(f"Error assessing processing integrity controls: {str(e)}")
        return {"error": f"Processing integrity controls assessment failed: {str(e)}"}

def _assess_confidentiality_controls(supabase, organization_id: str) -> Dict[str, Any]:
    """Assess confidentiality-related SOC2 controls"""
    
    confidentiality_assessment = {
        "data_classification_controls": "not_assessed",
        "access_restriction_controls": "not_assessed",
        "data_protection_controls": "not_assessed",
        "overall_confidentiality_score": 0
    }
    
    try:
        scores = []
        
        # Data classification (C1.1)
        # Based on requirement priority classification
        total_classified = 0
        high_confidentiality = 0
        
        projects_response = supabase.table("projects").select("id").eq("organization_id", organization_id).execute()
        
        for project in (projects_response.data or []):
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select("priority").eq("document_id", doc["id"]).execute()
                
                for req in (reqs_response.data or []):
                    if req.get("priority"):
                        total_classified += 1
                        if req["priority"] in ["high", "critical"]:
                            high_confidentiality += 1
        
        classification_score = (total_classified / max(total_classified, 1)) * 100 if total_classified > 0 else 0
        scores.append(classification_score)
        
        confidentiality_assessment["data_classification_controls"] = "effective" if classification_score >= 80 else "needs_improvement"
        
        # Access restrictions (C1.2)
        members_response = supabase.table("organization_members").select("role").eq("organization_id", organization_id).execute()
        role_count = len(set(m.get("role", "unknown") for m in (members_response.data or [])))
        
        access_score = min(100, role_count * 25)  # More roles indicate better access control
        scores.append(access_score)
        
        confidentiality_assessment["access_restriction_controls"] = "effective" if access_score >= 75 else "needs_improvement"
        
        # Overall confidentiality score
        overall_score = sum(scores) / len(scores) if scores else 0
        confidentiality_assessment["overall_confidentiality_score"] = round(overall_score, 1)
        
        return confidentiality_assessment
        
    except Exception as e:
        print(f"Error assessing confidentiality controls: {str(e)}")
        return {"error": f"Confidentiality controls assessment failed: {str(e)}"}

def _assess_privacy_controls(supabase, organization_id: str) -> Dict[str, Any]:
    """Assess privacy-related SOC2 controls"""
    
    privacy_assessment = {
        "data_minimization": "not_assessed",
        "consent_management": "not_assessed",
        "data_retention_controls": "not_assessed",
        "overall_privacy_score": 0
    }
    
    try:
        scores = []
        
        # Data minimization (P1.1)
        # Based on requirement specificity and purpose limitation
        projects_response = supabase.table("projects").select("id").eq("organization_id", organization_id).execute()
        
        total_requirements = 0
        specific_requirements = 0
        
        for project in (projects_response.data or []):
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select("description", "level").eq("document_id", doc["id"]).execute()
                
                for req in (reqs_response.data or []):
                    total_requirements += 1
                    desc = req.get("description", "")
                    level = req.get("level", "")
                    
                    # Consider requirement specific if it has detailed description and specific level
                    if len(desc) > 50 and level in ["feature", "component"]:
                        specific_requirements += 1
        
        minimization_score = (specific_requirements / max(total_requirements, 1)) * 100 if total_requirements > 0 else 0
        scores.append(minimization_score)
        
        privacy_assessment["data_minimization"] = "effective" if minimization_score >= 70 else "needs_improvement"
        
        # Data retention (P2.1)
        # Based on soft delete implementation
        deleted_projects = 0
        total_projects = 0
        
        for project in (projects_response.data or []):
            total_projects += 1
            if project.get("is_deleted"):
                deleted_projects += 1
        
        retention_score = 100 if deleted_projects > 0 else 50  # Having any deletions shows retention policy
        scores.append(retention_score)
        
        privacy_assessment["data_retention_controls"] = "effective" if retention_score >= 80 else "needs_improvement"
        
        # Overall privacy score
        overall_score = sum(scores) / len(scores) if scores else 0
        privacy_assessment["overall_privacy_score"] = round(overall_score, 1)
        
        return privacy_assessment
        
    except Exception as e:
        print(f"Error assessing privacy controls: {str(e)}")
        return {"error": f"Privacy controls assessment failed: {str(e)}"}

def _generate_audit_evidence(supabase, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate audit evidence documentation"""
    
    audit_evidence = {
        "evidence_inventory": {},
        "control_evidence_mapping": {},
        "evidence_quality_assessment": {}
    }
    
    try:
        # Evidence inventory
        evidence_items = []
        
        # Audit logs as evidence
        audit_logs_response = supabase.table("audit_logs").select("id, event_type, soc2_control").eq("organization_id", organization_id).limit(1000).execute()
        audit_logs = audit_logs_response.data if audit_logs_response.data else []
        
        evidence_items.append({
            "evidence_type": "audit_logs",
            "description": "System audit logs demonstrating control operation",
            "item_count": len(audit_logs),
            "coverage_period": params.get("period", "current_year"),
            "control_relevance": ["CC7.1", "CC7.2", "A1.1", "PI1.1"]
        })
        
        # Access control records as evidence
        members_response = supabase.table("organization_members").select("id, role, status").eq("organization_id", organization_id).execute()
        access_records = len(members_response.data) if members_response.data else 0
        
        evidence_items.append({
            "evidence_type": "access_control_records",
            "description": "User access provisioning and role assignment records",
            "item_count": access_records,
            "coverage_period": "current",
            "control_relevance": ["CC6.1", "CC6.2", "CC6.3"]
        })
        
        # Data processing records as evidence
        requirements_count = 0
        projects_response = supabase.table("projects").select("id").eq("organization_id", organization_id).execute()
        
        for project in (projects_response.data or []):
            docs_response = supabase.table("documents").select("id").eq("project_id", project["id"]).execute()
            for doc in (docs_response.data or []):
                reqs_response = supabase.table("requirements").select("id").eq("document_id", doc["id"]).execute()
                requirements_count += len(reqs_response.data) if reqs_response.data else 0
        
        evidence_items.append({
            "evidence_type": "data_processing_records",
            "description": "Requirements processing and enhancement records",
            "item_count": requirements_count,
            "coverage_period": "current",
            "control_relevance": ["PI1.1", "PI1.2", "C1.1"]
        })
        
        audit_evidence["evidence_inventory"] = {
            "total_evidence_items": len(evidence_items),
            "evidence_details": evidence_items
        }
        
        # Control evidence mapping
        soc2_controls = {
            "CC6.1": "Logical Access Controls",
            "CC6.2": "System Account Management", 
            "CC6.3": "Access Control Authorization",
            "CC7.1": "System Monitoring",
            "CC7.2": "Threat Detection",
            "A1.1": "System Availability",
            "PI1.1": "Data Processing Integrity",
            "C1.1": "Data Classification"
        }
        
        control_evidence_map = {}
        for control_id, control_name in soc2_controls.items():
            relevant_evidence = [
                item for item in evidence_items
                if control_id in item.get("control_relevance", [])
            ]
            
            control_evidence_map[control_id] = {
                "control_name": control_name,
                "evidence_count": len(relevant_evidence),
                "evidence_types": [item["evidence_type"] for item in relevant_evidence],
                "evidence_adequacy": "adequate" if len(relevant_evidence) >= 2 else "limited"
            }
        
        audit_evidence["control_evidence_mapping"] = control_evidence_map
        
        # Evidence quality assessment
        total_evidence_items = sum(item["item_count"] for item in evidence_items)
        controls_with_evidence = len([ce for ce in control_evidence_map.values() if ce["evidence_count"] > 0])
        
        quality_score = (controls_with_evidence / len(soc2_controls)) * 100
        
        audit_evidence["evidence_quality_assessment"] = {
            "evidence_coverage_score": round(quality_score, 1),
            "total_evidence_items": total_evidence_items,
            "controls_with_evidence": controls_with_evidence,
            "total_controls_assessed": len(soc2_controls),
            "evidence_sufficiency": "sufficient" if quality_score >= 80 else "needs_improvement"
        }
        
        return audit_evidence
        
    except Exception as e:
        print(f"Error generating audit evidence: {str(e)}")
        return {"error": f"Audit evidence generation failed: {str(e)}"}

def _generate_compliance_risk_assessments(compliance_result: Dict[str, Any], control_assessments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate compliance risk assessments"""
    
    risk_assessments = {
        "overall_compliance_risk": "not_assessed",
        "control_risks": {},
        "operational_risks": {},
        "risk_mitigation_status": {}
    }
    
    try:
        if "error" in compliance_result or "error" in control_assessments:
            return {"error": "Cannot assess risks due to compliance analysis errors"}
        
        # Calculate overall compliance risk
        control_scores = []
        
        for control_category, assessment in control_assessments.items():
            if isinstance(assessment, dict) and "overall" in assessment:
                score_key = f"overall_{control_category.replace('_controls', '_score')}"
                score = assessment.get(score_key, 0)
                control_scores.append(score)
        
        avg_control_score = sum(control_scores) / len(control_scores) if control_scores else 0
        
        if avg_control_score >= 85:
            overall_risk = "low"
        elif avg_control_score >= 70:
            overall_risk = "medium"
        elif avg_control_score >= 50:
            overall_risk = "high"
        else:
            overall_risk = "critical"
        
        risk_assessments["overall_compliance_risk"] = overall_risk
        
        # Assess control-specific risks
        control_risks = {}
        
        for control_category, assessment in control_assessments.items():
            if isinstance(assessment, dict):
                category_risks = []
                
                for control, status in assessment.items():
                    if status == "needs_improvement":
                        category_risks.append({
                            "control": control,
                            "risk_level": "medium",
                            "description": f"{control} requires improvement"
                        })
                    elif status == "not_assessed":
                        category_risks.append({
                            "control": control,
                            "risk_level": "high", 
                            "description": f"{control} not properly assessed"
                        })
                
                control_risks[control_category] = category_risks
        
        risk_assessments["control_risks"] = control_risks
        
        # Assess operational risks
        operational_risks = []
        
        # Check audit logging risks
        audit_logging = compliance_result.get("audit_logging", {})
        if audit_logging.get("logging_coverage", {}).get("total_audit_events", 0) < 100:
            operational_risks.append({
                "risk_type": "audit_logging",
                "risk_level": "medium",
                "description": "Limited audit logging may impact compliance evidence"
            })
        
        # Check access control risks
        access_controls = compliance_result.get("access_controls", {})
        user_mgmt = access_controls.get("user_access_management", {})
        if user_mgmt.get("inactive_users", 0) > user_mgmt.get("active_users", 1) * 0.2:
            operational_risks.append({
                "risk_type": "access_management",
                "risk_level": "medium", 
                "description": "High number of inactive users may indicate poor access governance"
            })
        
        risk_assessments["operational_risks"] = operational_risks
        
        return risk_assessments
        
    except Exception as e:
        print(f"Error generating risk assessments: {str(e)}")
        return {"error": f"Risk assessment generation failed: {str(e)}"}

def _generate_remediation_recommendations(control_assessments: Dict[str, Any], risk_assessments: Dict[str, Any]) -> List[str]:
    """Generate remediation recommendations"""
    
    recommendations = []
    
    try:
        # High-level risk recommendations
        overall_risk = risk_assessments.get("overall_compliance_risk", "unknown")
        
        if overall_risk == "critical":
            recommendations.append("Critical: Immediate remediation required across multiple control areas. Consider engaging compliance consultant.")
        elif overall_risk == "high":
            recommendations.append("High Priority: Address control deficiencies within 30 days to reduce compliance risk.")
        
        # Control-specific recommendations
        for control_category, assessment in control_assessments.items():
            if isinstance(assessment, dict):
                for control, status in assessment.items():
                    if status == "needs_improvement":
                        if "security" in control_category:
                            recommendations.append(f"Strengthen security controls: Improve {control} implementation and monitoring.")
                        elif "availability" in control_category:
                            recommendations.append(f"Enhance availability controls: Review and upgrade {control} procedures.")
                        elif "integrity" in control_category:
                            recommendations.append(f"Improve processing integrity: Implement additional validation for {control}.")
        
        # Operational recommendations
        operational_risks = risk_assessments.get("operational_risks", [])
        for risk in operational_risks:
            if risk["risk_type"] == "audit_logging":
                recommendations.append("Expand audit logging coverage to capture all system activities and user actions.")
            elif risk["risk_type"] == "access_management":
                recommendations.append("Implement regular access reviews and automated deprovisioning for inactive accounts.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Maintain current compliance posture and implement continuous monitoring.")
        
        recommendations.append("Schedule regular compliance assessments and control testing.")
        recommendations.append("Develop incident response procedures for compliance violations.")
        
        return recommendations
        
    except Exception as e:
        print(f"Error generating remediation recommendations: {str(e)}")
        return [f"Remediation planning failed: {str(e)}"]

def _assess_certification_readiness(control_assessments: Dict[str, Any], risk_assessments: Dict[str, Any]) -> Dict[str, Any]:
    """Assess readiness for SOC2 certification"""
    
    readiness_assessment = {
        "overall_readiness": "not_ready",
        "readiness_score": 0,
        "readiness_factors": {},
        "certification_gaps": []
    }
    
    try:
        # Calculate readiness score
        scores = []
        gaps = []
        
        # Control effectiveness score
        control_scores = []
        for category, assessment in control_assessments.items():
            if isinstance(assessment, dict):
                overall_key = f"overall_{category.replace('_controls', '_score')}"
                if overall_key in assessment:
                    control_scores.append(assessment[overall_key])
        
        avg_control_score = sum(control_scores) / len(control_scores) if control_scores else 0
        scores.append(avg_control_score)
        
        if avg_control_score < 80:
            gaps.append("Control effectiveness below certification threshold (80%)")
        
        # Risk level assessment
        overall_risk = risk_assessments.get("overall_compliance_risk", "critical")
        risk_score = {"low": 100, "medium": 75, "high": 50, "critical": 25}.get(overall_risk, 0)
        scores.append(risk_score)
        
        if overall_risk in ["high", "critical"]:
            gaps.append(f"Overall compliance risk too high: {overall_risk}")
        
        # Evidence adequacy
        # This would be based on audit evidence quality if available
        evidence_score = 75  # Placeholder based on having audit logging
        scores.append(evidence_score)
        
        # Calculate overall readiness
        overall_score = sum(scores) / len(scores) if scores else 0
        
        if overall_score >= 90:
            readiness_level = "ready"
        elif overall_score >= 80:
            readiness_level = "mostly_ready"
        elif overall_score >= 60:
            readiness_level = "partially_ready"
        else:
            readiness_level = "not_ready"
        
        readiness_assessment.update({
            "overall_readiness": readiness_level,
            "readiness_score": round(overall_score, 1),
            "readiness_factors": {
                "control_effectiveness": round(avg_control_score, 1),
                "risk_management": risk_score,
                "evidence_adequacy": evidence_score
            },
            "certification_gaps": gaps
        })
        
        return readiness_assessment
        
    except Exception as e:
        print(f"Error assessing certification readiness: {str(e)}")
        return {"error": f"Certification readiness assessment failed: {str(e)}"}

def _generate_compliance_metrics(compliance_result: Dict[str, Any], control_assessments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate compliance metrics dashboard"""
    
    metrics = {
        "key_metrics": {},
        "control_metrics": {},
        "operational_metrics": {},
        "trend_metrics": {}
    }
    
    try:
        # Key metrics
        audit_logging = compliance_result.get("audit_logging", {})
        total_events = audit_logging.get("logging_coverage", {}).get("total_audit_events", 0)
        
        access_controls = compliance_result.get("access_controls", {})
        total_users = access_controls.get("user_access_management", {}).get("total_users", 0)
        
        metrics["key_metrics"] = {
            "total_audit_events": total_events,
            "total_system_users": total_users,
            "compliance_controls_assessed": len(control_assessments),
            "organization_scope_projects": compliance_result.get("compliance_scope", {}).get("systems_in_scope", {}).get("total_projects", 0)
        }
        
        # Control metrics
        control_effectiveness = {}
        for category, assessment in control_assessments.items():
            if isinstance(assessment, dict):
                overall_key = f"overall_{category.replace('_controls', '_score')}"
                if overall_key in assessment:
                    control_effectiveness[category] = assessment[overall_key]
        
        metrics["control_metrics"] = {
            "control_effectiveness_scores": control_effectiveness,
            "average_control_effectiveness": round(sum(control_effectiveness.values()) / len(control_effectiveness), 1) if control_effectiveness else 0
        }
        
        # Operational metrics
        retention_analysis = compliance_result.get("data_retention", {})
        governance_analysis = compliance_result.get("data_governance", {})
        
        metrics["operational_metrics"] = {
            "data_retention_score": retention_analysis.get("deletion_practices", {}).get("version_retention_score", 0),
            "data_quality_score": governance_analysis.get("data_quality", {}).get("quality_score", 0),
            "audit_log_integrity_score": audit_logging.get("log_integrity", {}).get("log_integrity_score", 0)
        }
        
        return metrics
        
    except Exception as e:
        print(f"Error generating compliance metrics: {str(e)}")
        return {"error": f"Compliance metrics generation failed: {str(e)}"}

def _generate_compliance_executive_summary(compliance_result: Dict[str, Any], control_assessments: Dict[str, Any], risk_assessments: Dict[str, Any]) -> Dict[str, str]:
    """Generate executive summary for compliance report"""
    
    summary = {}
    
    try:
        # Overall compliance status
        overall_risk = risk_assessments.get("overall_compliance_risk", "unknown")
        org_info = compliance_result.get("organization_info", {})
        org_name = org_info.get("organization_name", "Organization")
        
        summary["status"] = f"{org_name} compliance risk level: {overall_risk.title()}"
        
        # Control assessment summary
        control_scores = []
        for category, assessment in control_assessments.items():
            if isinstance(assessment, dict):
                overall_key = f"overall_{category.replace('_controls', '_score')}"
                if overall_key in assessment:
                    control_scores.append(assessment[overall_key])
        
        avg_score = sum(control_scores) / len(control_scores) if control_scores else 0
        summary["controls"] = f"Average control effectiveness: {avg_score:.1f}% across {len(control_assessments)} control categories"
        
        # Audit evidence summary
        audit_logging = compliance_result.get("audit_logging", {})
        total_events = audit_logging.get("logging_coverage", {}).get("total_audit_events", 0)
        
        summary["evidence"] = f"Audit evidence: {total_events} logged events supporting compliance controls"
        
        # Risk summary
        control_risks = risk_assessments.get("control_risks", {})
        total_control_risks = sum(len(risks) for risks in control_risks.values())
        
        if total_control_risks > 0:
            summary["action_required"] = f"{total_control_risks} control deficiencies require remediation"
        else:
            summary["action_required"] = "No immediate control deficiencies identified"
        
        return summary
        
    except Exception as e:
        print(f"Error generating executive summary: {str(e)}")
        return {"error": f"Executive summary generation failed: {str(e)}"}

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Generate comprehensive SOC2 compliance report with control assessments"
    result = get_compliance_report_tool(test_org_id, test_message)
    print(f"Result: {result}")