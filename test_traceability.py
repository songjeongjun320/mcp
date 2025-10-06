"""
Test script for traceability_get_tree_tool.py
Run this independently to debug and see detailed output.
"""
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

os.environ["DEBUG_TRACEABILITY"] = "true"  # Enable debug mode

from tools.traceability_get_tree_tool import traceability_get_tree_tool
import json

# Test project IDs (replace with actual project IDs from your database)
TEST_PROJECTS = {
    "Automated Driving": "c41a1968-dafe-466b-98c2-bcf8a5e71584",
    "Super Charger Navigator": "8a911c12-1cc4-4949-a3e3-3b9a52291123"
}

def test_tree_view(project_name: str, project_id: str):
    """Test tree view for a specific project"""
    print("\n" + "=" * 100)
    print(f"TESTING: {project_name}")
    print("=" * 100)

    result = traceability_get_tree_tool(project_id, include_metadata=True)

    if result.get("success"):
        print("\nSUCCESS!")

        # Show hierarchy view
        if "hierarchy_view" in result:
            print("\nHIERARCHY VIEW:")
            print("-" * 80)
            for line in result["hierarchy_view"]:
                print(line)

        # Show metadata
        if "metadata" in result:
            print("\nMETADATA:")
            print("-" * 80)
            print(json.dumps(result["metadata"], indent=2))

        # Show raw tree data (first 5 nodes)
        if "tree" in result and len(result["tree"]) > 0:
            print("\nRAW TREE DATA (first 5 nodes):")
            print("-" * 80)
            print(json.dumps(result["tree"][:5], indent=2, default=str))
    else:
        print(f"\nFAILED: {result.get('error')}")
        print(f"Error Code: {result.get('error_code')}")

if __name__ == "__main__":
    print("Starting Traceability Tree View Tests")
    print("=" * 100)

    # Test all projects
    for project_name, project_id in TEST_PROJECTS.items():
        test_tree_view(project_name, project_id)

    print("\n" + "=" * 100)
    print("All tests completed!")
    print("=" * 100)
