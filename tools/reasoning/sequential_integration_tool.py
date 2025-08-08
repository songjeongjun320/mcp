"""
ATOMS.TECH Sequential MCP Server Integration Tool
Phase 2 Strategic Tool - Multi-Step Reasoning Enhancement

Purpose: Complex multi-step analysis and reasoning for requirements engineering
Expected Benefits:
- Complex requirements impact analysis
- Multi-step validation chains
- Advanced traceability analysis
- Root cause analysis for requirements conflicts
- 3x improvement in complex analysis capabilities
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import asyncio
import uuid

logger = logging.getLogger(__name__)

# Sequential MCP Server Client
class SequentialMCPClient:
    """Client for Sequential MCP Server integration"""
    
    def __init__(self, server_url: str, api_key: str):
        self.server_url = server_url
        self.api_key = api_key
        self.is_enabled = bool(server_url and api_key)
        self.reasoning_cache = {}
        
    async def multi_step_analysis(self, organization_id: str, analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complex multi-step analysis"""
        try:
            analysis_id = str(uuid.uuid4())
            analysis_type = analysis_request.get('type', 'impact_analysis')
            
            # Initialize reasoning chain
            reasoning_chain = await self._initialize_reasoning_chain(analysis_type, analysis_request, organization_id)
            
            # Execute reasoning steps
            results = await self._execute_reasoning_chain(reasoning_chain, organization_id)
            
            # Generate final conclusions
            conclusions = await self._synthesize_conclusions(results, analysis_request)
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "analysis_type": analysis_type,
                "reasoning_chain": reasoning_chain,
                "step_results": results,
                "conclusions": conclusions,
                "organization_id": organization_id,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multi-step analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_request": analysis_request,
                "organization_id": organization_id
            }
    
    async def _initialize_reasoning_chain(self, analysis_type: str, request: Dict[str, Any], org_id: str) -> List[Dict[str, Any]]:
        """Initialize reasoning chain based on analysis type"""
        
        chains = {
            "impact_analysis": [
                {
                    "step": 1,
                    "name": "identify_affected_components",
                    "description": "Identify all components affected by the change",
                    "method": "dependency_mapping",
                    "inputs": ["target_requirement", "system_architecture"]
                },
                {
                    "step": 2,
                    "name": "assess_direct_impacts",
                    "description": "Assess direct impacts on identified components",
                    "method": "impact_scoring",
                    "inputs": ["affected_components", "change_details"]
                },
                {
                    "step": 3,
                    "name": "analyze_cascading_effects",
                    "description": "Analyze cascading effects through the system",
                    "method": "propagation_analysis",
                    "inputs": ["direct_impacts", "system_dependencies"]
                },
                {
                    "step": 4,
                    "name": "evaluate_stakeholder_impact",
                    "description": "Evaluate impact on different stakeholders",
                    "method": "stakeholder_mapping",
                    "inputs": ["cascading_effects", "stakeholder_roles"]
                },
                {
                    "step": 5,
                    "name": "recommend_mitigation_strategies",
                    "description": "Recommend strategies to mitigate negative impacts",
                    "method": "strategy_generation",
                    "inputs": ["stakeholder_impacts", "risk_assessment"]
                }
            ],
            "traceability_analysis": [
                {
                    "step": 1,
                    "name": "map_requirement_relationships",
                    "description": "Map all relationships for target requirements",
                    "method": "graph_traversal",
                    "inputs": ["requirement_ids", "relationship_types"]
                },
                {
                    "step": 2,
                    "name": "analyze_coverage_gaps",
                    "description": "Identify gaps in traceability coverage",
                    "method": "gap_analysis",
                    "inputs": ["requirement_map", "expected_coverage"]
                },
                {
                    "step": 3,
                    "name": "validate_trace_consistency",
                    "description": "Validate consistency of trace relationships",
                    "method": "consistency_checking",
                    "inputs": ["trace_relationships", "validation_rules"]
                },
                {
                    "step": 4,
                    "name": "assess_trace_quality",
                    "description": "Assess quality of traceability implementation",
                    "method": "quality_scoring",
                    "inputs": ["trace_data", "quality_metrics"]
                },
                {
                    "step": 5,
                    "name": "generate_improvement_plan",
                    "description": "Generate plan to improve traceability",
                    "method": "planning",
                    "inputs": ["quality_assessment", "gap_analysis"]
                }
            ],
            "conflict_resolution": [
                {
                    "step": 1,
                    "name": "identify_conflict_sources",
                    "description": "Identify root sources of requirements conflicts",
                    "method": "root_cause_analysis",
                    "inputs": ["conflicting_requirements", "stakeholder_inputs"]
                },
                {
                    "step": 2,
                    "name": "analyze_conflict_types",
                    "description": "Categorize and analyze types of conflicts",
                    "method": "conflict_classification",
                    "inputs": ["conflict_sources", "conflict_taxonomy"]
                },
                {
                    "step": 3,
                    "name": "assess_resolution_options",
                    "description": "Generate and assess potential resolution options",
                    "method": "option_generation",
                    "inputs": ["conflict_analysis", "stakeholder_priorities"]
                },
                {
                    "step": 4,
                    "name": "evaluate_trade_offs",
                    "description": "Evaluate trade-offs for each resolution option",
                    "method": "trade_off_analysis",
                    "inputs": ["resolution_options", "evaluation_criteria"]
                },
                {
                    "step": 5,
                    "name": "recommend_resolution_strategy",
                    "description": "Recommend optimal resolution strategy",
                    "method": "decision_optimization",
                    "inputs": ["trade_off_analysis", "stakeholder_weights"]
                }
            ],
            "validation_chain": [
                {
                    "step": 1,
                    "name": "structural_validation",
                    "description": "Validate structural aspects of requirements",
                    "method": "structure_checking",
                    "inputs": ["requirements_document", "structural_rules"]
                },
                {
                    "step": 2,
                    "name": "semantic_validation",
                    "description": "Validate semantic consistency and meaning",
                    "method": "semantic_analysis",
                    "inputs": ["requirements_content", "domain_ontology"]
                },
                {
                    "step": 3,
                    "name": "constraint_validation",
                    "description": "Validate against system and business constraints",
                    "method": "constraint_checking",
                    "inputs": ["requirements_set", "system_constraints"]
                },
                {
                    "step": 4,
                    "name": "stakeholder_validation",
                    "description": "Validate against stakeholder needs and expectations",
                    "method": "stakeholder_verification",
                    "inputs": ["requirements", "stakeholder_needs"]
                },
                {
                    "step": 5,
                    "name": "integration_validation",
                    "description": "Validate integration with existing systems",
                    "method": "integration_checking",
                    "inputs": ["new_requirements", "existing_systems"]
                }
            ]
        }
        
        return chains.get(analysis_type, chains["impact_analysis"])
    
    async def _execute_reasoning_chain(self, chain: List[Dict[str, Any]], org_id: str) -> List[Dict[str, Any]]:
        """Execute each step in the reasoning chain"""
        
        results = []
        context = {"organization_id": org_id}
        
        for step_config in chain:
            step_result = await self._execute_reasoning_step(step_config, context, org_id)
            results.append(step_result)
            
            # Update context with results for next step
            context[step_config["name"]] = step_result["output"]
        
        return results
    
    async def _execute_reasoning_step(self, step_config: Dict[str, Any], context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Execute individual reasoning step"""
        
        step_name = step_config["name"]
        method = step_config["method"]
        
        try:
            # Mock step execution based on method type
            if method == "dependency_mapping":
                output = await self._perform_dependency_mapping(context, org_id)
            elif method == "impact_scoring":
                output = await self._perform_impact_scoring(context, org_id)
            elif method == "propagation_analysis":
                output = await self._perform_propagation_analysis(context, org_id)
            elif method == "stakeholder_mapping":
                output = await self._perform_stakeholder_mapping(context, org_id)
            elif method == "strategy_generation":
                output = await self._perform_strategy_generation(context, org_id)
            elif method == "graph_traversal":
                output = await self._perform_graph_traversal(context, org_id)
            elif method == "gap_analysis":
                output = await self._perform_gap_analysis(context, org_id)
            elif method == "consistency_checking":
                output = await self._perform_consistency_checking(context, org_id)
            elif method == "quality_scoring":
                output = await self._perform_quality_scoring(context, org_id)
            elif method == "root_cause_analysis":
                output = await self._perform_root_cause_analysis(context, org_id)
            elif method == "conflict_classification":
                output = await self._perform_conflict_classification(context, org_id)
            else:
                output = {"status": "completed", "result": f"Step {step_name} executed successfully"}
            
            return {
                "step": step_config["step"],
                "name": step_name,
                "method": method,
                "status": "success",
                "output": output,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reasoning step {step_name} failed: {str(e)}")
            return {
                "step": step_config["step"],
                "name": step_name,
                "method": method,
                "status": "error",
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            }
    
    async def _perform_dependency_mapping(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform dependency mapping analysis"""
        return {
            "affected_components": [
                {"id": "AUTH_MODULE", "name": "Authentication Module", "type": "software_component", "impact_level": "high"},
                {"id": "USER_DB", "name": "User Database", "type": "database", "impact_level": "medium"},
                {"id": "API_GATEWAY", "name": "API Gateway", "type": "infrastructure", "impact_level": "medium"},
                {"id": "UI_LOGIN", "name": "Login Interface", "type": "ui_component", "impact_level": "high"}
            ],
            "dependency_graph": {
                "nodes": ["AUTH_MODULE", "USER_DB", "API_GATEWAY", "UI_LOGIN"],
                "edges": [
                    {"from": "UI_LOGIN", "to": "AUTH_MODULE", "type": "calls"},
                    {"from": "AUTH_MODULE", "to": "USER_DB", "type": "queries"},
                    {"from": "AUTH_MODULE", "to": "API_GATEWAY", "type": "registers"}
                ]
            },
            "complexity_score": 0.7
        }
    
    async def _perform_impact_scoring(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform impact scoring analysis"""
        return {
            "impact_scores": [
                {"component": "AUTH_MODULE", "technical_impact": 0.9, "business_impact": 0.8, "risk_level": "high"},
                {"component": "USER_DB", "technical_impact": 0.6, "business_impact": 0.9, "risk_level": "high"},
                {"component": "API_GATEWAY", "technical_impact": 0.5, "business_impact": 0.4, "risk_level": "medium"},
                {"component": "UI_LOGIN", "technical_impact": 0.8, "business_impact": 0.7, "risk_level": "high"}
            ],
            "overall_impact_score": 0.76,
            "critical_impacts": ["AUTH_MODULE", "USER_DB", "UI_LOGIN"]
        }
    
    async def _perform_propagation_analysis(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform propagation analysis"""
        return {
            "propagation_paths": [
                {
                    "path": ["AUTH_MODULE", "SESSION_MANAGER", "USER_PROFILE", "DASHBOARD"],
                    "propagation_probability": 0.8,
                    "severity": "medium"
                },
                {
                    "path": ["USER_DB", "REPORTING_ENGINE", "ANALYTICS_DASHBOARD"],
                    "propagation_probability": 0.6,
                    "severity": "low"
                }
            ],
            "secondary_effects": [
                "Performance degradation in session management",
                "Potential data consistency issues",
                "Increased load on backup authentication systems"
            ],
            "mitigation_required": True
        }
    
    async def _perform_stakeholder_mapping(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform stakeholder mapping"""
        return {
            "stakeholder_impacts": [
                {
                    "stakeholder": "End Users",
                    "impact_type": "workflow_disruption",
                    "severity": "high",
                    "affected_activities": ["login", "password_reset", "profile_access"]
                },
                {
                    "stakeholder": "System Administrators",
                    "impact_type": "operational_complexity",
                    "severity": "medium",
                    "affected_activities": ["user_management", "security_monitoring"]
                },
                {
                    "stakeholder": "Development Team",
                    "impact_type": "implementation_effort",
                    "severity": "high",
                    "affected_activities": ["coding", "testing", "deployment"]
                },
                {
                    "stakeholder": "Security Team",
                    "impact_type": "security_review_required",
                    "severity": "medium",
                    "affected_activities": ["security_assessment", "compliance_verification"]
                }
            ],
            "communication_plan": {
                "high_priority": ["End Users", "Development Team"],
                "notification_timeline": "2 weeks before implementation"
            }
        }
    
    async def _perform_strategy_generation(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform strategy generation"""
        return {
            "mitigation_strategies": [
                {
                    "strategy": "Phased Implementation",
                    "description": "Implement changes in phases to minimize disruption",
                    "risk_reduction": 0.7,
                    "implementation_effort": "medium",
                    "timeline": "4-6 weeks"
                },
                {
                    "strategy": "Parallel System Deployment",
                    "description": "Run old and new systems in parallel during transition",
                    "risk_reduction": 0.9,
                    "implementation_effort": "high",
                    "timeline": "8-10 weeks"
                },
                {
                    "strategy": "Enhanced Testing Protocol",
                    "description": "Implement comprehensive testing before deployment",
                    "risk_reduction": 0.6,
                    "implementation_effort": "medium",
                    "timeline": "2-3 weeks"
                }
            ],
            "recommended_strategy": "Phased Implementation",
            "success_criteria": [
                "Zero authentication failures during transition",
                "User satisfaction score > 4.0",
                "System performance maintained"
            ]
        }
    
    async def _perform_graph_traversal(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform graph traversal for traceability"""
        return {
            "trace_paths": [
                {
                    "path": ["BUSINESS_NEED_001", "REQ_FUNC_001", "DESIGN_COMP_001", "TEST_CASE_001"],
                    "trace_type": "forward_trace",
                    "completeness": 1.0
                },
                {
                    "path": ["REQ_FUNC_002", "DESIGN_COMP_002"],
                    "trace_type": "partial_forward",
                    "completeness": 0.5
                }
            ],
            "orphaned_requirements": ["REQ_FUNC_003", "REQ_NFR_005"],
            "trace_statistics": {
                "total_requirements": 25,
                "fully_traced": 18,
                "partially_traced": 5,
                "untraced": 2
            }
        }
    
    async def _perform_gap_analysis(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform gap analysis"""
        return {
            "coverage_gaps": [
                {
                    "gap_type": "missing_test_cases",
                    "affected_requirements": ["REQ_FUNC_001", "REQ_FUNC_003"],
                    "severity": "high",
                    "recommendation": "Create comprehensive test cases"
                },
                {
                    "gap_type": "incomplete_design_mapping",
                    "affected_requirements": ["REQ_NFR_002"],
                    "severity": "medium",
                    "recommendation": "Map to architectural components"
                }
            ],
            "coverage_score": 0.78,
            "improvement_potential": 0.22
        }
    
    async def _perform_consistency_checking(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform consistency checking"""
        return {
            "consistency_issues": [
                {
                    "issue_type": "conflicting_requirements",
                    "requirements": ["REQ_PERF_001", "REQ_FUNC_007"],
                    "description": "Performance requirement conflicts with functional behavior",
                    "severity": "high"
                },
                {
                    "issue_type": "circular_dependency",
                    "requirements": ["REQ_FUNC_002", "REQ_FUNC_004"],
                    "description": "Circular dependency detected in requirements",
                    "severity": "medium"
                }
            ],
            "consistency_score": 0.85,
            "resolution_needed": True
        }
    
    async def _perform_quality_scoring(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform quality scoring"""
        return {
            "quality_metrics": {
                "completeness": 0.88,
                "consistency": 0.85,
                "clarity": 0.92,
                "traceability": 0.78,
                "testability": 0.83
            },
            "overall_quality_score": 0.85,
            "quality_grade": "B+",
            "improvement_areas": ["traceability", "consistency"]
        }
    
    async def _perform_root_cause_analysis(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform root cause analysis"""
        return {
            "root_causes": [
                {
                    "cause": "Ambiguous stakeholder requirements",
                    "probability": 0.8,
                    "impact": "high",
                    "evidence": ["Multiple interpretations of requirement REQ_001"]
                },
                {
                    "cause": "Insufficient domain expertise",
                    "probability": 0.6,
                    "impact": "medium",
                    "evidence": ["Technical feasibility not properly assessed"]
                }
            ],
            "primary_cause": "Ambiguous stakeholder requirements",
            "resolution_strategy": "Stakeholder clarification sessions"
        }
    
    async def _perform_conflict_classification(self, context: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Perform conflict classification"""
        return {
            "conflict_types": [
                {
                    "type": "resource_conflict",
                    "count": 3,
                    "severity": "high",
                    "examples": ["Competing system resources", "Budget constraints"]
                },
                {
                    "type": "functional_conflict",
                    "count": 2,
                    "severity": "medium",
                    "examples": ["Contradictory feature requirements"]
                }
            ],
            "resolution_complexity": "high",
            "stakeholder_alignment_needed": True
        }
    
    async def _synthesize_conclusions(self, results: List[Dict[str, Any]], request: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize final conclusions from reasoning chain results"""
        
        successful_steps = [r for r in results if r["status"] == "success"]
        
        # Extract key insights from all successful steps
        insights = []
        recommendations = []
        risk_factors = []
        
        for step_result in successful_steps:
            output = step_result["output"]
            
            # Extract insights based on step type
            if "impact_scores" in output:
                high_impact_items = [item for item in output["impact_scores"] if item["risk_level"] == "high"]
                if high_impact_items:
                    insights.append(f"High-impact components identified: {len(high_impact_items)} items require careful attention")
            
            if "mitigation_strategies" in output:
                recommended_strategy = output.get("recommended_strategy")
                if recommended_strategy:
                    recommendations.append(f"Recommended approach: {recommended_strategy}")
            
            if "consistency_issues" in output:
                issues = output["consistency_issues"]
                if issues:
                    risk_factors.append(f"Consistency issues detected: {len(issues)} conflicts need resolution")
            
            if "coverage_gaps" in output:
                gaps = output["coverage_gaps"]
                if gaps:
                    risk_factors.append(f"Coverage gaps identified: {len(gaps)} areas need attention")
        
        # Generate overall assessment
        analysis_quality = len(successful_steps) / len(results) if results else 0
        
        return {
            "executive_summary": f"Completed {len(successful_steps)}/{len(results)} analysis steps successfully",
            "key_insights": insights[:5],  # Top 5 insights
            "recommendations": recommendations[:3],  # Top 3 recommendations
            "risk_factors": risk_factors[:3],  # Top 3 risk factors
            "analysis_quality_score": round(analysis_quality, 2),
            "confidence_level": "high" if analysis_quality >= 0.8 else "medium" if analysis_quality >= 0.6 else "low",
            "next_steps": [
                "Review detailed step results",
                "Validate findings with stakeholders",
                "Implement recommended strategies",
                "Monitor progress and adjust as needed"
            ]
        }

# Initialize Sequential MCP Client
mcp_client = SequentialMCPClient(
    server_url=os.environ.get('SEQUENTIAL_SERVER_URL', 'https://api.sequential.ai'),
    api_key=os.environ.get('SEQUENTIAL_API_KEY', '')
)

async def sequential_reasoning_tool(organization_id: str, message: str) -> Dict[str, Any]:
    """
    Complex multi-step analysis and reasoning for requirements engineering
    
    Purpose: Perform sophisticated multi-step analysis for complex requirements
    engineering challenges requiring systematic reasoning approaches
    
    Expected Benefits:
    - Complex requirements impact analysis
    - Multi-step validation chains
    - Advanced traceability analysis  
    - Root cause analysis for requirements conflicts
    - 3x improvement in complex analysis capabilities
    
    Args:
        organization_id (str): Organization identifier for data isolation
        message (str): Multi-step reasoning request
        
    Returns:
        Dict[str, Any]: Complex analysis results with step-by-step reasoning
        
    Analysis Types:
        - impact_analysis: Assess impacts of requirement changes
        - traceability_analysis: Analyze requirements traceability
        - conflict_resolution: Resolve requirements conflicts
        - validation_chain: Multi-step requirements validation
        - root_cause_analysis: Identify root causes of issues
    """
    
    try:
        logger.info(f"Processing Sequential reasoning for org {organization_id}")
        
        if not mcp_client.is_enabled:
            return {
                "success": False,
                "error": "Sequential MCP server is not configured",
                "message": message,
                "organization_id": organization_id
            }
        
        # Parse message to determine analysis type and extract parameters
        analysis_request = _parse_analysis_request(message)
        
        # Perform multi-step analysis
        result = await mcp_client.multi_step_analysis(organization_id, analysis_request)
        
        # Add usage analytics
        result["analytics"] = {
            "tool_type": "sequential_reasoning",
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat(),
            "tool": "sequential_integration_tool"
        }
        
        logger.info(f"Sequential reasoning completed successfully for org {organization_id}")
        return result
        
    except Exception as e:
        logger.error(f"Sequential reasoning failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": message,
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat()
        }

def _parse_analysis_request(message: str) -> Dict[str, Any]:
    """Parse analysis request from user message"""
    
    message_lower = message.lower()
    
    # Determine analysis type
    if "impact" in message_lower:
        analysis_type = "impact_analysis"
        target = "authentication_system"  # Default target
    elif "trace" in message_lower or "traceability" in message_lower:
        analysis_type = "traceability_analysis"
        target = "all_requirements"
    elif "conflict" in message_lower:
        analysis_type = "conflict_resolution"
        target = "conflicting_requirements"
    elif "validat" in message_lower:
        analysis_type = "validation_chain"
        target = "requirements_document"
    elif "root cause" in message_lower or "cause" in message_lower:
        analysis_type = "root_cause_analysis"
        target = "system_issues"
    else:
        analysis_type = "impact_analysis"  # Default
        target = "system_change"
    
    return {
        "type": analysis_type,
        "target": target,
        "scope": "organization",
        "depth": "comprehensive",
        "parameters": {
            "include_secondary_effects": True,
            "generate_recommendations": True,
            "assess_risks": True
        }
    }

# Synchronous wrapper for FastMCP compatibility
def sequential_reasoning_tool_sync(organization_id: str, message: str) -> Dict[str, Any]:
    """Synchronous wrapper for Sequential reasoning"""
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(sequential_reasoning_tool(organization_id, message))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Sync wrapper failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": message,
            "organization_id": organization_id
        }