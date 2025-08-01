"""Analyze document tool module with LLM integration"""

import json
import sys
import os
from typing import Any

# Add parent directory to sys.path to import local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client
try:
    from llm.gemini_2_5_flash import llm
except ImportError:
    print("Warning: LLM module not available. AI analysis will use fallback methods.")
    def llm(prompt, system_prompt=None):
        return "AI analysis not available due to import error."

def analyze_doc_tool(organization_id: str, message: str) -> Any:
    """
    Analyze document content and provide AI-powered summary and insights
    
    Parameters
    ----------
    organization_id : str
        Unique identifier of the organization
    message : str
        User's request message specifying which document to analyze
        
    Returns
    -------
    Any
        Structured result containing document analysis and AI-generated summary
    """
    print(f"[analyze_doc] Starting with organization_id: {organization_id}")
    print(f"[analyze_doc] Message: {message}")
    
    try:
        # Create Supabase client
        print("[analyze_doc] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Get all projects from the organization first
        print(f"[analyze_doc] Querying projects for organization: {organization_id}")
        projects_response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        if not projects_response.data:
            print("[analyze_doc] No projects found for organization")
            result = {
                "json": {
                    "analyzed_documents": [],
                    "analysis_summary": "No projects or documents found for analysis",
                    "message": "No projects found for the given organization_id"
                }
            }
            
            # Save result to JSON file
            with open("analyze_doc_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Extract project IDs
        project_ids = [project.get("id", "") for project in projects_response.data]
        print(f"[analyze_doc] Found {len(project_ids)} projects")
        
        # Get all documents from all projects
        all_documents = []
        for project in projects_response.data:
            project_id = project.get("id", "")
            project_name = project.get("name", "")
            
            # Query documents for this project
            docs_response = supabase.table("documents").select("*").eq("project_id", project_id).execute()
            
            for doc in docs_response.data:
                doc_info = {
                    "document_id": doc.get("id", ""),
                    "document_name": doc.get("name", ""),
                    "document_description": doc.get("description", ""),
                    "document_content": doc.get("content", ""),
                    "document_type": doc.get("type", ""),
                    "project_name": project_name,
                    "project_id": project_id,
                    "created_at": doc.get("created_at", ""),
                    "updated_at": doc.get("updated_at", "")
                }
                all_documents.append(doc_info)
        
        print(f"[analyze_doc] Found {len(all_documents)} documents to analyze")
        
        # Analyze documents using LLM
        analyzed_documents = []
        overall_insights = []
        
        for doc in all_documents:
            doc_name = doc.get("document_name", "")
            doc_description = doc.get("document_description", "")
            doc_content = doc.get("document_content", "")
            project_name = doc.get("project_name", "")
            
            print(f"[analyze_doc] Analyzing document: {doc_name}")
            
            # Prepare content for analysis
            content_to_analyze = f"""
            Document Name: {doc_name}
            Project: {project_name}
            Description: {doc_description}
            Content: {doc_content}
            """
            
            # Create analysis prompt
            analysis_prompt = f"""
            Please analyze the following document and provide:
            1. A concise summary (2-3 sentences)
            2. Key insights or important points
            3. Document type classification
            4. Potential action items or recommendations
            5. Overall assessment score (1-10)
            
            Document to analyze:
            {content_to_analyze}
            """
            
            system_prompt = "You are a professional document analyst. Provide clear, actionable insights and summaries for business documents."
            
            try:
                # Get AI analysis
                ai_analysis = llm(analysis_prompt, system_prompt)
                
                analysis_result = {
                    "document_name": doc_name,
                    "project_name": project_name,
                    "document_type": doc.get("document_type", ""),
                    "original_description": doc_description,
                    "ai_analysis": ai_analysis,
                    "analysis_timestamp": doc.get("updated_at", ""),
                    "content_length": len(doc_content) if doc_content else 0
                }
                
                analyzed_documents.append(analysis_result)
                overall_insights.append(f"[{project_name}]{doc_name}: {ai_analysis[:100]}...")
                
            except Exception as e:
                print(f"[analyze_doc] Error analyzing document {doc_name}: {str(e)}")
                
                # Fallback analysis without LLM
                fallback_analysis = f"""
                Summary: {doc_description[:200]}...
                Document Type: {doc.get('document_type', 'Unknown')}
                Content Length: {len(doc_content) if doc_content else 0} characters
                Status: Analysis completed without AI processing due to technical issues
                """
                
                analysis_result = {
                    "document_name": doc_name,
                    "project_name": project_name,
                    "document_type": doc.get("document_type", ""),
                    "original_description": doc_description,
                    "ai_analysis": fallback_analysis,
                    "analysis_timestamp": doc.get("updated_at", ""),
                    "content_length": len(doc_content) if doc_content else 0,
                    "analysis_error": str(e)
                }
                
                analyzed_documents.append(analysis_result)
        
        # Generate overall summary using LLM
        try:
            summary_prompt = f"""
            Based on the analysis of {len(analyzed_documents)} documents across {len(projects_response.data)} projects, 
            please provide an executive summary including:
            1. Overall document quality assessment
            2. Key themes across projects
            3. Recommendations for document management
            4. Priority areas for attention
            
            Documents analyzed: {', '.join([doc['document_name'] for doc in analyzed_documents[:10]])}
            {"..." if len(analyzed_documents) > 10 else ""}
            """
            
            overall_summary = llm(summary_prompt, "You are an executive assistant providing high-level document analysis summaries.")
            
        except Exception as e:
            print(f"[analyze_doc] Error generating overall summary: {str(e)}")
            overall_summary = f"Analyzed {len(analyzed_documents)} documents across {len(projects_response.data)} projects. Technical summary generation encountered issues."
        
        result = {
            "json": {
                "organization_id": organization_id,
                "total_documents_analyzed": len(analyzed_documents),
                "total_projects": len(projects_response.data),
                "analyzed_documents": analyzed_documents,
                "executive_summary": overall_summary,
                "analysis_insights": overall_insights[:10],  # Top 10 insights
                "message": message,
                "analysis_completed_at": "2024-01-01T00:00:00Z"
            }
        }
        
        # Save result to JSON file
        print("[analyze_doc] Saving result to JSON file...")
        with open("analyze_doc_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[analyze_doc] SUCCESS: Analyzed {len(analyzed_documents)} documents with AI insights")
        return result
        
    except Exception as e:
        print(f"[analyze_doc] ERROR: {str(e)}")
        error_result = {"error": f"An error occurred during document analysis: {str(e)}"}
        
        # Save error to JSON file
        with open("analyze_doc_tool.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
            
        return error_result

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "Analyze all documents and provide insights and summaries"
    result = analyze_doc_tool(test_org_id, test_message)
    print(f"Result: {result}")