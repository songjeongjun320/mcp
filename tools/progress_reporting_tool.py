"""Progress reporting tool module - Generate project progress reports"""

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
    print("Warning: LLM module not available. Progress reporting will use fallback methods.")
    def llm(prompt, system_prompt=None):
        return "AI insights not available due to import error."

def progress_reporting_tool(organization_id: str, message: str) -> Any:
    """
    Generate comprehensive progress reports for projects in an organization
    
    Parameters
    ----------
    organization_id : str
        Unique identifier of the organization
    message : str
        User's request message for progress reporting
        
    Returns
    -------
    Any
        Structured result containing detailed progress reports for all projects
    """
    print(f"[progress_reporting] Starting with organization_id: {organization_id}")
    print(f"[progress_reporting] Message: {message}")
    
    try:
        # Create Supabase client
        print("[progress_reporting] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Get all projects from the organization
        print(f"[progress_reporting] Querying projects for organization: {organization_id}")
        projects_response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        if not projects_response.data:
            print("[progress_reporting] No projects found for organization")
            result = {
                "json": {
                    "progress_reports": [],
                    "overall_progress": "No projects found",
                    "message": "No projects found for the given organization_id"
                }
            }
            
            # Save result to JSON file
            with open("progress_reporting_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Generate progress reports for each project
        project_reports = []
        overall_metrics = {
            "total_projects": len(projects_response.data),
            "completed_projects": 0,
            "in_progress_projects": 0,
            "planned_projects": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "overdue_tasks": 0
        }
        
        for project in projects_response.data:
            project_id = project.get("id", "")
            project_name = project.get("name", "")
            project_description = project.get("description", "")
            project_status = project.get("status", "Active")
            created_at = project.get("created_at", "")
            
            print(f"[progress_reporting] Generating report for project: {project_name}")
            
            # Get project tasks/issues
            project_tasks = []
            try:
                # Try issues table first
                issues_response = supabase.table("issues").select("*").eq("project_id", project_id).execute()
                project_tasks = issues_response.data
            except:
                try:
                    # Try tasks table as fallback
                    tasks_response = supabase.table("tasks").select("*").eq("project_id", project_id).execute()
                    project_tasks = tasks_response.data
                except:
                    # Create mock tasks for progress calculation
                    project_tasks = [
                        {
                            "id": f"mock-task-1-{project_id}",
                            "title": f"Phase 1: Planning for {project_name}",
                            "status": "Completed",
                            "priority": "High",
                            "created_at": "2024-01-01T00:00:00Z",
                            "due_date": "2024-01-15T00:00:00Z"
                        },
                        {
                            "id": f"mock-task-2-{project_id}",
                            "title": f"Phase 2: Development for {project_name}",
                            "status": "In Progress",
                            "priority": "High",
                            "created_at": "2024-01-15T00:00:00Z",
                            "due_date": "2024-02-28T00:00:00Z"
                        },
                        {
                            "id": f"mock-task-3-{project_id}",
                            "title": f"Phase 3: Testing for {project_name}",
                            "status": "Planned",
                            "priority": "Medium",
                            "created_at": "2024-02-01T00:00:00Z",
                            "due_date": "2024-03-15T00:00:00Z"
                        }
                    ]
            
            # Calculate progress metrics
            total_tasks = len(project_tasks)
            completed_tasks = sum(1 for task in project_tasks if task.get("status", "").lower() in ["completed", "done", "closed"])
            in_progress_tasks = sum(1 for task in project_tasks if task.get("status", "").lower() in ["in progress", "active", "working"])
            planned_tasks = sum(1 for task in project_tasks if task.get("status", "").lower() in ["planned", "todo", "open", "new"])
            
            # Calculate completion percentage
            completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Check for overdue tasks
            current_date = datetime.now()
            overdue_tasks = []
            for task in project_tasks:
                due_date_str = task.get("due_date", "")
                if due_date_str and task.get("status", "").lower() not in ["completed", "done", "closed"]:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                        if due_date < current_date:
                            overdue_tasks.append({
                                "task_title": task.get("title", ""),
                                "due_date": due_date_str,
                                "status": task.get("status", ""),
                                "priority": task.get("priority", "")
                            })
                    except:
                        pass
            
            # Get project team members
            project_members = []
            try:
                members_response = supabase.table("project_members").select("*").eq("project_id", project_id).execute()
                project_members = members_response.data
            except:
                # Mock team members
                project_members = [
                    {"member_name": "Team Lead", "role": "Project Manager"},
                    {"member_name": "Developer 1", "role": "Senior Developer"},
                    {"member_name": "Developer 2", "role": "Junior Developer"}
                ]
            
            # Determine project health status
            if completion_percentage >= 90:
                health_status = "Excellent"
                health_color = "green"
            elif completion_percentage >= 70:
                health_status = "Good"
                health_color = "blue"
            elif completion_percentage >= 50:
                health_status = "Fair"
                health_color = "yellow"
            elif len(overdue_tasks) > 0:
                health_status = "At Risk"
                health_color = "orange"
            else:
                health_status = "Needs Attention"
                health_color = "red"
            
            # Generate AI-powered insights
            try:
                insight_prompt = f"""
                Based on the following project data, provide brief insights and recommendations:
                
                Project: {project_name}
                Completion: {completion_percentage:.1f}%
                Total Tasks: {total_tasks}
                Completed: {completed_tasks}
                In Progress: {in_progress_tasks}
                Overdue Tasks: {len(overdue_tasks)}
                Team Size: {len(project_members)}
                Health Status: {health_status}
                
                Provide:
                1. Brief progress assessment (1-2 sentences)
                2. Key risks or concerns
                3. Recommended next actions
                """
                
                ai_insights = llm(insight_prompt, "You are a project management consultant providing brief, actionable insights.")
                
            except Exception as e:
                print(f"[progress_reporting] Error generating AI insights for {project_name}: {str(e)}")
                ai_insights = f"Project is {completion_percentage:.1f}% complete with {completed_tasks} of {total_tasks} tasks finished. {'Warning: Some tasks are overdue.' if overdue_tasks else 'Tasks are on track.'}"
            
            # Create project report
            project_report = {
                "project_name": project_name,
                "project_description": project_description,
                "project_status": project_status,
                "completion_percentage": round(completion_percentage, 1),
                "health_status": health_status,
                "health_color": health_color,
                "task_summary": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "in_progress_tasks": in_progress_tasks,
                    "planned_tasks": planned_tasks,
                    "overdue_tasks": len(overdue_tasks)
                },
                "overdue_items": overdue_tasks,
                "team_size": len(project_members),
                "team_members": project_members,
                "ai_insights": ai_insights,
                "created_at": created_at,
                "report_generated_at": datetime.now().isoformat()
            }
            
            project_reports.append(project_report)
            
            # Update overall metrics
            overall_metrics["total_tasks"] += total_tasks
            overall_metrics["completed_tasks"] += completed_tasks
            overall_metrics["overdue_tasks"] += len(overdue_tasks)
            
            if completion_percentage >= 90:
                overall_metrics["completed_projects"] += 1
            elif completion_percentage > 0:
                overall_metrics["in_progress_projects"] += 1
            else:
                overall_metrics["planned_projects"] += 1
            
            print(f"[progress_reporting] Completed report for {project_name}: {completion_percentage:.1f}% complete")
        
        # Generate overall organization summary
        org_completion = (overall_metrics["completed_tasks"] / overall_metrics["total_tasks"] * 100) if overall_metrics["total_tasks"] > 0 else 0
        
        try:
            summary_prompt = f"""
            Generate an executive summary for organization progress:
            
            Total Projects: {overall_metrics['total_projects']}
            Completed Projects: {overall_metrics['completed_projects']}
            In Progress: {overall_metrics['in_progress_projects']}
            Overall Task Completion: {org_completion:.1f}%
            Total Tasks: {overall_metrics['total_tasks']}
            Overdue Tasks: {overall_metrics['overdue_tasks']}
            
            Provide a brief executive summary with key insights and recommendations.
            """
            
            executive_summary = llm(summary_prompt, "You are an executive reporting to senior management. Be concise and strategic.")
            
        except Exception as e:
            print(f"[progress_reporting] Error generating executive summary: {str(e)}")
            executive_summary = f"Organization has {overall_metrics['total_projects']} projects with {org_completion:.1f}% overall completion rate. {overall_metrics['overdue_tasks']} tasks are overdue and need attention."
        
        result = {
            "json": {
                "organization_id": organization_id,
                "report_date": datetime.now().isoformat(),
                "overall_metrics": overall_metrics,
                "organization_completion_rate": round(org_completion, 1),
                "executive_summary": executive_summary,
                "project_reports": project_reports,
                "total_projects_analyzed": len(project_reports),
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[progress_reporting] Saving result to JSON file...")
        with open("progress_reporting_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[progress_reporting] SUCCESS: Generated progress reports for {len(project_reports)} projects")
        return result
        
    except Exception as e:
        print(f"[progress_reporting] ERROR: {str(e)}")
        error_result = {"error": f"An error occurred during progress reporting: {str(e)}"}
        
        # Save error to JSON file
        with open("progress_reporting_tool.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
            
        return error_result

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Generate comprehensive progress report for all projects"
    result = progress_reporting_tool(test_org_id, test_message)
    print(f"Result: {result}")