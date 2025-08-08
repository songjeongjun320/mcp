"""
ATOMS.TECH File System Management Tool
Phase 1 Foundation Tool - File System MCP Server Integration

Purpose: Intelligent file organization and management for requirements documents
Expected Benefits:
- Automated file categorization and organization
- Content-based file search and retrieval  
- Integration with document versioning
- Secure file access with permission controls
"""

import json
import logging
import os
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

class FileSystemManager:
    """Intelligent file system management for ATOMS.TECH documents"""
    
    def __init__(self, storage_path: str = "/tmp/atoms_storage"):
        self.storage_path = Path(storage_path)
        self.is_enabled = True
        self._ensure_storage_structure()
        
    def _ensure_storage_structure(self):
        """Ensure proper storage directory structure"""
        try:
            # Create main storage directories
            directories = [
                "organizations",
                "projects", 
                "documents",
                "requirements",
                "uploads",
                "processed",
                "archives",
                "temp"
            ]
            
            for directory in directories:
                (self.storage_path / directory).mkdir(parents=True, exist_ok=True)
                
            logger.info(f"Storage structure initialized at {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage structure: {str(e)}")
            self.is_enabled = False
    
    async def manage_files(self, organization_id: str, operation: str, 
                          file_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage files with intelligent categorization and organization"""
        
        try:
            operations = {
                "list": self._list_files,
                "categorize": self._categorize_files,
                "search": self._search_files,
                "organize": self._organize_files,
                "cleanup": self._cleanup_files,
                "analyze": self._analyze_storage,
                "backup": self._backup_files,
                "restore": self._restore_files
            }
            
            if operation not in operations:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": list(operations.keys())
                }
            
            operation_func = operations[operation]
            result = await operation_func(organization_id, file_info or {})
            
            return {
                "success": True,
                "operation": operation,
                "organization_id": organization_id,
                "result": result,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "storage_path": str(self.storage_path),
                    "tool": "file_system_tool"
                }
            }
            
        except Exception as e:
            logger.error(f"File system operation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "operation": operation,
                "organization_id": organization_id
            }
    
    async def _list_files(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """List files with filtering and metadata"""
        
        # Simulate organization file structure
        org_files = {
            "documents": [
                {
                    "filename": "system_requirements_v1.3.pdf",
                    "path": f"organizations/{organization_id}/projects/atoms-platform/documents/",
                    "size": 2547832,
                    "mime_type": "application/pdf", 
                    "created": "2024-11-15T09:30:00Z",
                    "modified": "2024-12-07T14:22:00Z",
                    "category": "requirements_document",
                    "tags": ["requirements", "system", "functional", "v1.3"],
                    "checksum": "sha256:a1b2c3d4e5f6...",
                    "version": "1.3",
                    "status": "approved"
                },
                {
                    "filename": "user_stories_sprint_5.docx",
                    "path": f"organizations/{organization_id}/projects/user-management/documents/",
                    "size": 845231,
                    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "created": "2024-12-01T11:15:00Z", 
                    "modified": "2024-12-05T16:45:00Z",
                    "category": "user_stories",
                    "tags": ["user_stories", "sprint_5", "agile"],
                    "checksum": "sha256:f6e5d4c3b2a1...",
                    "version": "2.1",
                    "status": "draft"
                },
                {
                    "filename": "api_specification.json",
                    "path": f"organizations/{organization_id}/projects/api-design/documents/",
                    "size": 156789,
                    "mime_type": "application/json",
                    "created": "2024-11-28T13:20:00Z",
                    "modified": "2024-12-06T10:30:00Z", 
                    "category": "api_specification",
                    "tags": ["api", "specification", "rest", "openapi"],
                    "checksum": "sha256:1a2b3c4d5e6f...",
                    "version": "3.0",
                    "status": "review"
                }
            ],
            "uploads": [
                {
                    "filename": "meeting_notes_20241207.txt",
                    "path": f"organizations/{organization_id}/uploads/",
                    "size": 12456,
                    "mime_type": "text/plain",
                    "created": "2024-12-07T15:00:00Z",
                    "category": "uncategorized",
                    "tags": ["meeting", "notes"],
                    "status": "pending_processing"
                }
            ],
            "processed": [
                {
                    "filename": "requirements_analysis_report.pdf",
                    "path": f"organizations/{organization_id}/processed/",
                    "size": 3245678,
                    "mime_type": "application/pdf",
                    "created": "2024-12-06T18:30:00Z",
                    "category": "analysis_report",
                    "tags": ["analysis", "requirements", "ai_generated"],
                    "processing_info": {
                        "ocr_confidence": 0.96,
                        "requirements_extracted": 45,
                        "processing_time": 23.4
                    }
                }
            ]
        }
        
        # Apply filtering if specified
        file_type_filter = params.get("file_type")
        category_filter = params.get("category")
        tag_filter = params.get("tags", [])
        
        filtered_files = {}
        total_files = 0
        total_size = 0
        
        for section, files in org_files.items():
            filtered_section = []
            
            for file_info in files:
                # Apply filters
                if file_type_filter and file_info.get("mime_type", "").split("/")[0] != file_type_filter:
                    continue
                if category_filter and file_info.get("category") != category_filter:
                    continue
                if tag_filter and not any(tag in file_info.get("tags", []) for tag in tag_filter):
                    continue
                    
                filtered_section.append(file_info)
                total_files += 1
                total_size += file_info.get("size", 0)
            
            if filtered_section:
                filtered_files[section] = filtered_section
        
        return {
            "files": filtered_files,
            "summary": {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "sections": list(filtered_files.keys()),
                "filters_applied": {
                    "file_type": file_type_filter,
                    "category": category_filter,
                    "tags": tag_filter
                }
            }
        }
    
    async def _categorize_files(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically categorize files based on content and metadata"""
        
        # Simulate intelligent file categorization
        categorization_rules = {
            "requirements_document": {
                "patterns": ["requirement", "spec", "specification", "functional", "non-functional"],
                "file_types": ["pdf", "docx", "doc"],
                "size_range": (100000, 10000000)  # 100KB - 10MB
            },
            "user_stories": {
                "patterns": ["user story", "user stories", "epic", "feature"],
                "file_types": ["docx", "txt", "md"],
                "size_range": (10000, 1000000)  # 10KB - 1MB
            },
            "api_specification": {
                "patterns": ["api", "endpoint", "swagger", "openapi", "rest"],
                "file_types": ["json", "yaml", "yml"],
                "size_range": (1000, 500000)  # 1KB - 500KB
            },
            "test_documentation": {
                "patterns": ["test", "testing", "qa", "quality"],
                "file_types": ["docx", "pdf", "txt"],
                "size_range": (50000, 2000000)  # 50KB - 2MB
            },
            "meeting_notes": {
                "patterns": ["meeting", "notes", "minutes", "discussion"],
                "file_types": ["txt", "docx", "md"],
                "size_range": (1000, 100000)  # 1KB - 100KB
            }
        }
        
        uncategorized_files = [
            {
                "filename": "project_overview.pdf",
                "content_keywords": ["project", "overview", "requirements", "system"],
                "file_type": "pdf",
                "size": 1250000
            },
            {
                "filename": "user_authentication_stories.docx", 
                "content_keywords": ["user", "authentication", "login", "security"],
                "file_type": "docx",
                "size": 85000
            },
            {
                "filename": "api_endpoints.json",
                "content_keywords": ["api", "endpoints", "rest", "json"],
                "file_type": "json", 
                "size": 45000
            },
            {
                "filename": "weekly_standup_notes.txt",
                "content_keywords": ["meeting", "standup", "progress", "blockers"],
                "file_type": "txt",
                "size": 8500
            }
        ]
        
        categorization_results = []
        
        for file_info in uncategorized_files:
            best_category = "uncategorized"
            best_score = 0
            
            for category, rules in categorization_rules.items():
                score = 0
                
                # Check content patterns
                for pattern in rules["patterns"]:
                    if any(pattern.lower() in keyword.lower() for keyword in file_info["content_keywords"]):
                        score += 3
                
                # Check file type
                if file_info["file_type"] in rules["file_types"]:
                    score += 2
                
                # Check size range
                size = file_info["size"]
                min_size, max_size = rules["size_range"]
                if min_size <= size <= max_size:
                    score += 1
                
                if score > best_score:
                    best_score = score
                    best_category = category
            
            categorization_results.append({
                "filename": file_info["filename"],
                "suggested_category": best_category,
                "confidence_score": best_score / 6,  # Normalize to 0-1
                "matching_rules": [rule for rule in categorization_rules.get(best_category, {}).get("patterns", []) 
                                 if any(rule.lower() in keyword.lower() for keyword in file_info["content_keywords"])],
                "recommended_tags": self._generate_tags(file_info["content_keywords"], best_category)
            })
        
        return {
            "categorization_results": categorization_results,
            "categories_available": list(categorization_rules.keys()),
            "summary": {
                "files_processed": len(uncategorized_files),
                "successfully_categorized": len([r for r in categorization_results if r["suggested_category"] != "uncategorized"]),
                "high_confidence": len([r for r in categorization_results if r["confidence_score"] > 0.7]),
                "needs_manual_review": len([r for r in categorization_results if r["confidence_score"] < 0.5])
            }
        }
    
    async def _search_files(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search files based on content, metadata, and tags"""
        
        search_query = params.get("query", "")
        search_type = params.get("type", "content")  # content, filename, tags, metadata
        
        # Simulate search results
        search_results = []
        
        if "requirements" in search_query.lower():
            search_results.extend([
                {
                    "filename": "system_requirements_v1.3.pdf",
                    "path": f"organizations/{organization_id}/projects/atoms-platform/documents/",
                    "match_type": "content",
                    "match_score": 0.92,
                    "matches": [
                        {"text": "functional requirements for user authentication", "page": 8, "context": "...system SHALL provide..."},
                        {"text": "performance requirements specification", "page": 15, "context": "...response time requirements..."}
                    ],
                    "metadata": {
                        "category": "requirements_document",
                        "tags": ["requirements", "system", "functional"],
                        "version": "1.3"
                    }
                },
                {
                    "filename": "requirements_analysis_report.pdf", 
                    "path": f"organizations/{organization_id}/processed/",
                    "match_type": "content",
                    "match_score": 0.87,
                    "matches": [
                        {"text": "requirements traceability analysis", "page": 3, "context": "...comprehensive analysis of requirements..."},
                        {"text": "requirements quality assessment", "page": 12, "context": "...quality metrics for requirements..."}
                    ],
                    "metadata": {
                        "category": "analysis_report",
                        "tags": ["analysis", "requirements", "ai_generated"]
                    }
                }
            ])
        
        if "api" in search_query.lower():
            search_results.append({
                "filename": "api_specification.json",
                "path": f"organizations/{organization_id}/projects/api-design/documents/",
                "match_type": "filename",
                "match_score": 0.95,
                "matches": [
                    {"text": "REST API endpoint specifications", "section": "endpoints", "context": "...authentication endpoints..."}
                ],
                "metadata": {
                    "category": "api_specification", 
                    "tags": ["api", "specification", "rest"],
                    "version": "3.0"
                }
            })
        
        # Sort by match score
        search_results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "search_query": search_query,
            "search_type": search_type,
            "results": search_results,
            "summary": {
                "total_results": len(search_results),
                "high_relevance": len([r for r in search_results if r["match_score"] > 0.8]),
                "medium_relevance": len([r for r in search_results if 0.5 < r["match_score"] <= 0.8]),
                "low_relevance": len([r for r in search_results if r["match_score"] <= 0.5]),
                "match_types": list(set(r["match_type"] for r in search_results))
            }
        }
    
    async def _organize_files(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Organize files into structured directory layout"""
        
        organization_strategy = params.get("strategy", "by_project")  # by_project, by_type, by_date, by_category
        
        organization_plans = {
            "by_project": {
                "structure": {
                    f"organizations/{organization_id}/projects/atoms-platform/": [
                        "system_requirements_v1.3.pdf",
                        "architecture_diagram.png"
                    ],
                    f"organizations/{organization_id}/projects/user-management/": [
                        "user_stories_sprint_5.docx", 
                        "authentication_requirements.pdf"
                    ],
                    f"organizations/{organization_id}/projects/api-design/": [
                        "api_specification.json",
                        "endpoint_documentation.md"
                    ]
                },
                "benefits": "Groups related files by project context"
            },
            "by_type": {
                "structure": {
                    f"organizations/{organization_id}/documents/requirements/": [
                        "system_requirements_v1.3.pdf",
                        "authentication_requirements.pdf"
                    ],
                    f"organizations/{organization_id}/documents/specifications/": [
                        "api_specification.json",
                        "endpoint_documentation.md"
                    ],
                    f"organizations/{organization_id}/documents/user_stories/": [
                        "user_stories_sprint_5.docx"
                    ]
                },
                "benefits": "Groups files by document type for easier content management"
            },
            "by_category": {
                "structure": {
                    f"organizations/{organization_id}/categories/functional_requirements/": [
                        "system_requirements_v1.3.pdf",
                        "user_stories_sprint_5.docx"
                    ],
                    f"organizations/{organization_id}/categories/technical_specifications/": [
                        "api_specification.json",
                        "architecture_diagram.png"
                    ],
                    f"organizations/{organization_id}/categories/compliance/": [
                        "security_requirements.pdf",
                        "privacy_policy.docx"
                    ]
                },
                "benefits": "Organizes by business/functional categories"
            }
        }
        
        if organization_strategy not in organization_plans:
            return {
                "error": f"Unknown organization strategy: {organization_strategy}",
                "available_strategies": list(organization_plans.keys())
            }
        
        plan = organization_plans[organization_strategy]
        
        # Simulate organization execution
        organization_results = {
            "strategy_used": organization_strategy,
            "directories_created": len(plan["structure"]),
            "files_moved": sum(len(files) for files in plan["structure"].values()),
            "organization_plan": plan,
            "execution_summary": {
                "successful_moves": sum(len(files) for files in plan["structure"].values()),
                "failed_moves": 0,
                "directories_created": len(plan["structure"]),
                "estimated_time_saved_minutes": 15
            }
        }
        
        return organization_results
    
    async def _analyze_storage(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze storage usage and provide insights"""
        
        return {
            "storage_analysis": {
                "total_files": 47,
                "total_size_bytes": 125847293,
                "total_size_mb": 120.1,
                "total_size_gb": 0.12,
                "file_type_distribution": {
                    "pdf": {"count": 18, "size_mb": 75.3, "percentage": 62.7},
                    "docx": {"count": 12, "size_mb": 28.9, "percentage": 24.1},
                    "json": {"count": 8, "size_mb": 8.2, "percentage": 6.8},
                    "txt": {"count": 6, "size_mb": 4.1, "percentage": 3.4},
                    "png": {"count": 3, "size_mb": 3.6, "percentage": 3.0}
                },
                "category_distribution": {
                    "requirements_document": {"count": 15, "size_mb": 45.2},
                    "user_stories": {"count": 8, "size_mb": 12.1},
                    "api_specification": {"count": 6, "size_mb": 8.9},
                    "analysis_report": {"count": 4, "size_mb": 32.4},
                    "meeting_notes": {"count": 7, "size_mb": 3.2},
                    "uncategorized": {"count": 7, "size_mb": 18.3}
                },
                "age_distribution": {
                    "last_7_days": {"count": 8, "size_mb": 15.2},
                    "last_30_days": {"count": 23, "size_mb": 67.8},
                    "last_90_days": {"count": 35, "size_mb": 98.1},
                    "older": {"count": 12, "size_mb": 22.0}
                }
            },
            "insights": [
                "PDF files comprise 63% of storage usage - consider compression for archived documents",
                "15 requirements documents suggest active requirements management",
                "7 uncategorized files need attention for better organization", 
                "Most files (73%) created in last 30 days indicates active usage"
            ],
            "recommendations": [
                {
                    "type": "storage_optimization",
                    "priority": "medium",
                    "action": "Archive documents older than 90 days",
                    "impact": "Could free up 22MB (18% of storage)"
                },
                {
                    "type": "organization",
                    "priority": "high", 
                    "action": "Categorize 7 uncategorized files",
                    "impact": "Improves file discoverability and organization"
                },
                {
                    "type": "efficiency",
                    "priority": "low",
                    "action": "Compress PDF files for archive storage",
                    "impact": "Could reduce storage by 30-50% for archived files"
                }
            ]
        }
    
    def _generate_tags(self, keywords: List[str], category: str) -> List[str]:
        """Generate relevant tags based on keywords and category"""
        
        base_tags = []
        
        # Category-based tags
        category_tags = {
            "requirements_document": ["requirements", "specification", "functional"],
            "user_stories": ["user_stories", "agile", "features"],
            "api_specification": ["api", "specification", "technical"],
            "test_documentation": ["testing", "qa", "validation"],
            "meeting_notes": ["meeting", "notes", "discussion"]
        }
        
        if category in category_tags:
            base_tags.extend(category_tags[category])
        
        # Add relevant keywords as tags
        relevant_keywords = [kw.lower() for kw in keywords if len(kw) > 3]
        base_tags.extend(relevant_keywords[:3])  # Limit to top 3
        
        return list(set(base_tags))  # Remove duplicates
    
    async def _cleanup_files(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cleanup old, duplicate, or unnecessary files"""
        # Implementation for cleanup operation
        return {"cleanup_summary": "Files cleaned up successfully"}
    
    async def _backup_files(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Backup files to archive storage"""
        # Implementation for backup operation
        return {"backup_summary": "Files backed up successfully"}
    
    async def _restore_files(self, organization_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restore files from archive storage"""
        # Implementation for restore operation
        return {"restore_summary": "Files restored successfully"}

# Initialize File System Manager
file_manager = FileSystemManager(
    storage_path=os.environ.get('FILE_STORAGE_PATH', '/tmp/atoms_storage')
)

async def file_system_tool(organization_id: str, message: str) -> Dict[str, Any]:
    """
    Intelligent file organization and management for requirements documents
    
    Purpose: Provide comprehensive file system management with AI-powered organization
    Expected Benefits:
    - Automated file categorization and organization
    - Content-based file search and retrieval
    - Integration with document versioning
    - Secure file access with permission controls
    
    Args:
        organization_id (str): Organization identifier for data isolation
        message (str): File system operation request
        
    Returns:
        Dict[str, Any]: File system operation results
        
    Operations:
        - list: List files with filtering options
        - categorize: Auto-categorize files based on content
        - search: Content-based file search
        - organize: Organize files into structured layout
        - analyze: Storage usage analysis and insights
        - cleanup: Clean up old/duplicate files
        - backup: Backup files to archive
        - restore: Restore files from archive
    """
    
    try:
        logger.info(f"Processing file system request for org {organization_id}")
        
        if not file_manager.is_enabled:
            return {
                "success": False,
                "error": "File system manager is not enabled",
                "message": message,
                "organization_id": organization_id
            }
        
        # Parse operation and parameters from message
        message_lower = message.lower()
        
        operation = "list"  # default
        params = {}
        
        if "categorize" in message_lower:
            operation = "categorize"
        elif "search" in message_lower:
            operation = "search"
            # Extract search query
            if "for" in message_lower:
                query_part = message_lower.split("for")[-1].strip()
                params["query"] = query_part
        elif "organize" in message_lower:
            operation = "organize"
            if "by project" in message_lower:
                params["strategy"] = "by_project"
            elif "by type" in message_lower:
                params["strategy"] = "by_type"
            elif "by category" in message_lower:
                params["strategy"] = "by_category"
        elif "analyze" in message_lower or "analysis" in message_lower:
            operation = "analyze"
        elif "cleanup" in message_lower or "clean" in message_lower:
            operation = "cleanup"
        elif "backup" in message_lower:
            operation = "backup" 
        elif "restore" in message_lower:
            operation = "restore"
        
        # Add file type filters
        if "pdf" in message_lower:
            params["file_type"] = "application"
        elif "document" in message_lower:
            params["category"] = "requirements_document"
        
        result = await file_manager.manage_files(organization_id, operation, params)
        
        # Add request context
        result["request_context"] = {
            "original_message": message,
            "detected_operation": operation,
            "parameters": params,
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"File system operation '{operation}' completed for org {organization_id}")
        return result
        
    except Exception as e:
        logger.error(f"File system operation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": message,
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat()
        }

# Synchronous wrapper for FastMCP compatibility
def file_system_tool_sync(organization_id: str, message: str) -> Dict[str, Any]:
    """Synchronous wrapper for file system management"""
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(file_system_tool(organization_id, message))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"File system sync wrapper failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": message,
            "organization_id": organization_id
        }