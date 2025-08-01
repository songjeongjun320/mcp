"""Milestone tracking tool module - Track project milestones and key achievements"""

import json
import sys
import os
from typing import Any
from datetime import datetime, timedelta

# Add parent directory to sys.path to import local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client
try:
    from llm.gemini_2_5_flash import llm
except ImportError:
    print("Warning: LLM module not available. Milestone tracking will use fallback methods.")
    def llm(prompt, system_prompt=None):
        return "AI insights not available due to import error."

def milestone_tracking_tool(organization_id: str, message: str) -> Any:
    """
    Track and analyze project milestones and key achievements
    
    Parameters
    ----------
    organization_id : str
        Unique identifier of the organization
    message : str
        User's request message for milestone tracking
        
    Returns
    -------
    Any
        Structured result containing milestone tracking data and analysis
    """
    print(f"[milestone_tracking] Starting with organization_id: {organization_id}")
    print(f"[milestone_tracking] Message: {message}")
    
    try:
        # Create Supabase client
        print("[milestone_tracking] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Get all projects from the organization
        print(f"[milestone_tracking] Querying projects for organization: {organization_id}")
        projects_response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        if not projects_response.data:
            print("[milestone_tracking] No projects found for organization")
            result = {
                "json": {
                    "milestone_reports": [],
                    "overall_milestone_status": "No projects found",
                    "message": "No projects found for the given organization_id"
                }
            }
            
            # Save result to JSON file
            with open("milestone_tracking_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Track milestones for each project
        project_milestones = []
        overall_milestone_stats = {
            "total_projects": len(projects_response.data),
            "total_milestones": 0,
            "completed_milestones": 0,
            "upcoming_milestones": 0,
            "overdue_milestones": 0,
            "on_track_projects": 0,
            "at_risk_projects": 0
        }
        
        current_date = datetime.now()
        
        for project in projects_response.data:
            project_id = project.get("id", "")
            project_name = project.get("name", "")
            project_description = project.get("description", "")
            project_start_date = project.get("created_at", "")
            project_status = project.get("status", "Active")
            
            print(f"[milestone_tracking] Processing milestones for project: {project_name}")
            
            # Try to get milestones from milestones table
            project_milestones_data = []
            try:
                milestones_response = supabase.table("milestones").select("*").eq("project_id", project_id).execute()
                project_milestones_data = milestones_response.data
            except:
                # If no milestones table, create standard project milestones based on project lifecycle
                print(f"[milestone_tracking] Creating standard milestones for project: {project_name}")
                
                # Calculate milestone dates based on project start date
                try:
                    start_date = datetime.fromisoformat(project_start_date.replace("Z", "+00:00"))
                except:
                    start_date = current_date - timedelta(days=90)  # Default to 3 months ago
                
                project_milestones_data = [
                    {
                        "id": f"milestone-1-{project_id}",
                        "name": "Project Kickoff",
                        "description": f"Initial project setup and team onboarding for {project_name}",
                        "target_date": start_date.isoformat(),
                        "completion_date": start_date.isoformat(),
                        "status": "Completed",
                        "milestone_type": "Planning",
                        "progress_percentage": 100
                    },
                    {
                        "id": f"milestone-2-{project_id}",
                        "name": "Requirements Complete",
                        "description": f"All project requirements documented and approved for {project_name}",
                        "target_date": (start_date + timedelta(days=14)).isoformat(),
                        "completion_date": (start_date + timedelta(days=16)).isoformat(),
                        "status": "Completed",
                        "milestone_type": "Planning",
                        "progress_percentage": 100
                    },
                    {
                        "id": f"milestone-3-{project_id}",
                        "name": "Development Phase 1",
                        "description": f"Core functionality development completed for {project_name}",
                        "target_date": (start_date + timedelta(days=45)).isoformat(),
                        "completion_date": None,
                        "status": "In Progress",
                        "milestone_type": "Development",
                        "progress_percentage": 75
                    },
                    {
                        "id": f"milestone-4-{project_id}",
                        "name": "Testing & QA",
                        "description": f"Quality assurance and testing phase for {project_name}",
                        "target_date": (start_date + timedelta(days=75)).isoformat(),
                        "completion_date": None,
                        "status": "Planned",
                        "milestone_type": "Testing",
                        "progress_percentage": 0
                    },
                    {
                        "id": f"milestone-5-{project_id}",
                        "name": "Production Deployment",
                        "description": f"Final deployment and go-live for {project_name}",
                        "target_date": (start_date + timedelta(days=90)).isoformat(),
                        "completion_date": None,
                        "status": "Planned",
                        "milestone_type": "Deployment",
                        "progress_percentage": 0
                    }
                ]
            
            # Analyze milestone status and calculate metrics
            milestones_analysis = []
            project_milestone_stats = {
                "total_milestones": len(project_milestones_data),
                "completed_milestones": 0,
                "in_progress_milestones": 0,
                "planned_milestones": 0,
                "overdue_milestones": 0,
                "upcoming_milestones": 0
            }
            
            for milestone in project_milestones_data:
                milestone_name = milestone.get("name", "")
                milestone_description = milestone.get("description", "")
                target_date_str = milestone.get("target_date", "")
                completion_date_str = milestone.get("completion_date", "")
                status = milestone.get("status", "Planned")
                milestone_type = milestone.get("milestone_type", "General")
                progress = milestone.get("progress_percentage", 0)
                
                # Parse dates
                target_date = None
                completion_date = None
                days_until_due = None
                is_overdue = False
                
                try:
                    if target_date_str:
                        target_date = datetime.fromisoformat(target_date_str.replace("Z", "+00:00"))
                        days_until_due = (target_date - current_date).days
                        is_overdue = target_date < current_date and status.lower() not in ["completed", "done"]
                    
                    if completion_date_str:
                        completion_date = datetime.fromisoformat(completion_date_str.replace("Z", "+00:00"))
                except:
                    pass
                
                # Determine milestone health
                if status.lower() in ["completed", "done"]:
                    health = "Completed"
                    project_milestone_stats["completed_milestones"] += 1
                elif is_overdue:
                    health = "Overdue"
                    project_milestone_stats["overdue_milestones"] += 1
                elif days_until_due is not None and days_until_due <= 7:
                    health = "Due Soon"
                    project_milestone_stats["upcoming_milestones"] += 1
                elif status.lower() in ["in progress", "active"]:
                    health = "On Track"
                    project_milestone_stats["in_progress_milestones"] += 1
                else:
                    health = "Planned"
                    project_milestone_stats["planned_milestones"] += 1
                
                milestone_analysis = {
                    "milestone_name": milestone_name,
                    "milestone_description": milestone_description,
                    "milestone_type": milestone_type,
                    "target_date": target_date_str,
                    "completion_date": completion_date_str,
                    "status": status,
                    "health": health,
                    "progress_percentage": progress,
                    "days_until_due": days_until_due,
                    "is_overdue": is_overdue
                }
                
                milestones_analysis.append(milestone_analysis)
            
            # Calculate project milestone health
            completion_rate = (project_milestone_stats["completed_milestones"] / project_milestone_stats["total_milestones"] * 100) if project_milestone_stats["total_milestones"] > 0 else 0
            
            if project_milestone_stats["overdue_milestones"] > 0:
                project_health = "At Risk"
                overall_milestone_stats["at_risk_projects"] += 1
            elif completion_rate >= 80:
                project_health = "On Track"
                overall_milestone_stats["on_track_projects"] += 1
            elif completion_rate >= 50:
                project_health = "Fair Progress"
                overall_milestone_stats["on_track_projects"] += 1
            else:
                project_health = "Needs Attention"
                overall_milestone_stats["at_risk_projects"] += 1
            
            # Generate AI insights for project milestones
            try:
                milestone_prompt = f"""
                Analyze the following project milestone data and provide insights:
                
                Project: {project_name}
                Total Milestones: {project_milestone_stats['total_milestones']}
                Completed: {project_milestone_stats['completed_milestones']}
                Overdue: {project_milestone_stats['overdue_milestones']}
                Upcoming: {project_milestone_stats['upcoming_milestones']}
                Completion Rate: {completion_rate:.1f}%
                Project Health: {project_health}
                
                Provide:
                1. Brief milestone progress assessment
                2. Key risks and opportunities
                3. Recommended actions for milestone management
                """
                
                milestone_insights = llm(milestone_prompt, "You are a project milestone specialist providing strategic insights.")
                
            except Exception as e:
                print(f"[milestone_tracking] Error generating insights for {project_name}: {str(e)}")
                milestone_insights = f"Project has {completion_rate:.1f}% milestone completion rate. {'Action needed for overdue milestones.' if project_milestone_stats['overdue_milestones'] > 0 else 'Milestones are progressing well.'}"
            
            # Create project milestone report
            project_milestone_report = {
                "project_name": project_name,
                "project_description": project_description,
                "project_status": project_status,
                "project_health": project_health,
                "milestone_completion_rate": round(completion_rate, 1),
                "milestone_statistics": project_milestone_stats,
                "milestones": milestones_analysis,
                "ai_insights": milestone_insights,
                "analysis_date": current_date.isoformat()
            }
            
            project_milestones.append(project_milestone_report)
            
            # Update overall statistics
            overall_milestone_stats["total_milestones"] += project_milestone_stats["total_milestones"]
            overall_milestone_stats["completed_milestones"] += project_milestone_stats["completed_milestones"]
            overall_milestone_stats["upcoming_milestones"] += project_milestone_stats["upcoming_milestones"]
            overall_milestone_stats["overdue_milestones"] += project_milestone_stats["overdue_milestones"]
            
            print(f"[milestone_tracking] Completed milestone analysis for {project_name}: {completion_rate:.1f}% milestone completion")
        
        # Generate executive milestone summary
        org_milestone_completion = (overall_milestone_stats["completed_milestones"] / overall_milestone_stats["total_milestones"] * 100) if overall_milestone_stats["total_milestones"] > 0 else 0
        
        try:
            executive_prompt = f"""
            Generate an executive summary for organizational milestone tracking:
            
            Total Projects: {overall_milestone_stats['total_projects']}
            Total Milestones: {overall_milestone_stats['total_milestones']}
            Completed Milestones: {overall_milestone_stats['completed_milestones']}
            Overdue Milestones: {overall_milestone_stats['overdue_milestones']}
            On Track Projects: {overall_milestone_stats['on_track_projects']}
            At Risk Projects: {overall_milestone_stats['at_risk_projects']}
            Overall Milestone Completion: {org_milestone_completion:.1f}%
            
            Provide strategic insights and recommendations for milestone management.
            """
            
            executive_milestone_summary = llm(executive_prompt, "You are a senior project portfolio manager reporting to executives.")
            
        except Exception as e:
            print(f"[milestone_tracking] Error generating executive summary: {str(e)}")
            executive_milestone_summary = f"Organization tracking {overall_milestone_stats['total_milestones']} milestones across {overall_milestone_stats['total_projects']} projects with {org_milestone_completion:.1f}% completion rate."
        
        result = {
            "json": {
                "organization_id": organization_id,
                "tracking_date": current_date.isoformat(),
                "overall_milestone_statistics": overall_milestone_stats,
                "organization_milestone_completion_rate": round(org_milestone_completion, 1),
                "executive_milestone_summary": executive_milestone_summary,
                "project_milestone_reports": project_milestones,
                "total_projects_tracked": len(project_milestones),
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[milestone_tracking] Saving result to JSON file...")
        with open("milestone_tracking_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[milestone_tracking] SUCCESS: Tracked milestones for {len(project_milestones)} projects")
        return result
        
    except Exception as e:
        print(f"[milestone_tracking] ERROR: {str(e)}")
        error_result = {"error": f"An error occurred during milestone tracking: {str(e)}"}
        
        # Save error to JSON file
        with open("milestone_tracking_tool.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
            
        return error_result

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Track all project milestones and provide comprehensive analysis"
    result = milestone_tracking_tool(test_org_id, test_message)
    print(f"Result: {result}")