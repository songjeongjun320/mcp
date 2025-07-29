"""Auto-generated tool module."""

import os
from typing import Any
from supabase import create_client, Client

def pull_projects(organization_id: str) -> Any:
    """
    Get projects's information, names, and descriptions from database

    Parameters
    ----------
        organization_id (str): Unique identifier of the organization to pull project ids from database

    Returns
    -------
    Any
        Result of the tool.
    """
    try:
        # Supabase 클라이언트 생성
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            return {"error": "Supabase credentials not found in environment variables"}
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # projects 테이블에서 organization_id로 필터링하여 데이터 가져오기
        response = supabase.table("projects").select("*").or_(
            f"organization_id.eq.{organization_id},name.eq.{organization_id},id.eq.{organization_id}"
        ).execute()
        
        if response.data:
            return {"success": True, "projects": response.data}
        else:
            return {"success": False, "message": "No projects found for the given organization_id"}
            
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    result = pull_projects(test_org_id)
    print(f"Result: {result}")
