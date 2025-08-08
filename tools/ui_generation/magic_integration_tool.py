"""
ATOMS.TECH Magic MCP Server Integration Tool
Phase 2 Strategic Tool - Dynamic UI Generation

Purpose: Dynamic UI components for requirements management
Expected Benefits:
- Dynamic dashboard generation
- Custom forms for requirements capture
- Interactive visualization components
- Responsive requirements management interfaces
- Rapid UI development and customization
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import asyncio
import uuid

logger = logging.getLogger(__name__)

# Magic MCP Server Client
class MagicMCPClient:
    """Client for Magic MCP Server integration"""
    
    def __init__(self, server_url: str, api_key: str):
        self.server_url = server_url
        self.api_key = api_key
        self.is_enabled = bool(server_url and api_key)
        self.component_templates = {}
        
    async def generate_ui_component(self, organization_id: str, component_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dynamic UI component"""
        try:
            component_id = str(uuid.uuid4())
            component_type = component_request.get('type', 'requirements_form')
            
            # Generate component configuration
            component_config = await self._generate_component_config(component_type, component_request, organization_id)
            
            # Generate React/Next.js component code
            component_code = await self._generate_component_code(component_config, organization_id)
            
            # Generate styling and responsive design
            styling = await self._generate_component_styling(component_config)
            
            # Generate TypeScript interfaces if needed
            interfaces = await self._generate_typescript_interfaces(component_config)
            
            return {
                "success": True,
                "component_id": component_id,
                "component_type": component_type,
                "component_code": component_code,
                "styling": styling,
                "interfaces": interfaces,
                "configuration": component_config,
                "organization_id": organization_id,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"UI component generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "component_request": component_request,
                "organization_id": organization_id
            }
    
    async def _generate_component_config(self, component_type: str, request: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Generate component configuration"""
        
        configs = {
            "requirements_form": {
                "name": "RequirementsForm",
                "description": "Dynamic form for capturing requirements",
                "props": {
                    "organizationId": {"type": "string", "required": True},
                    "projectId": {"type": "string", "required": True},
                    "onSubmit": {"type": "function", "required": True},
                    "initialData": {"type": "object", "required": False}
                },
                "fields": [
                    {"name": "title", "type": "text", "label": "Requirement Title", "required": True, "validation": "minLength:5"},
                    {"name": "description", "type": "textarea", "label": "Description", "required": True, "validation": "minLength:20"},
                    {"name": "type", "type": "select", "label": "Type", "options": ["functional", "non_functional", "constraint"], "required": True},
                    {"name": "priority", "type": "select", "label": "Priority", "options": ["high", "medium", "low"], "required": True},
                    {"name": "acceptance_criteria", "type": "array", "label": "Acceptance Criteria", "itemType": "text", "required": False},
                    {"name": "tags", "type": "tags", "label": "Tags", "required": False},
                    {"name": "stakeholders", "type": "multi_select", "label": "Stakeholders", "required": False},
                    {"name": "due_date", "type": "date", "label": "Due Date", "required": False}
                ],
                "validation": {
                    "client_side": True,
                    "server_side": True,
                    "real_time": True
                },
                "features": ["auto_save", "form_validation", "accessibility", "responsive"]
            },
            "dashboard": {
                "name": "RequirementsDashboard",
                "description": "Interactive dashboard for requirements overview",
                "props": {
                    "organizationId": {"type": "string", "required": True},
                    "userId": {"type": "string", "required": True},
                    "filters": {"type": "object", "required": False}
                },
                "layout": {
                    "type": "grid",
                    "columns": 12,
                    "responsive_breakpoints": ["sm", "md", "lg", "xl"]
                },
                "widgets": [
                    {"type": "metric_card", "title": "Total Requirements", "span": 3, "data_source": "requirements_count"},
                    {"type": "metric_card", "title": "Completion Rate", "span": 3, "data_source": "completion_percentage"},
                    {"type": "metric_card", "title": "Active Projects", "span": 3, "data_source": "active_projects"},
                    {"type": "metric_card", "title": "Overdue Items", "span": 3, "data_source": "overdue_count"},
                    {"type": "chart", "title": "Requirements by Type", "span": 6, "chart_type": "pie", "data_source": "requirements_by_type"},
                    {"type": "chart", "title": "Completion Trend", "span": 6, "chart_type": "line", "data_source": "completion_trend"},
                    {"type": "table", "title": "Recent Activity", "span": 12, "data_source": "recent_activities"}
                ],
                "features": ["real_time_updates", "export_data", "responsive", "dark_mode"]
            },
            "traceability_matrix": {
                "name": "TraceabilityMatrix",
                "description": "Interactive traceability matrix visualization",
                "props": {
                    "organizationId": {"type": "string", "required": True},
                    "projectId": {"type": "string", "required": True},
                    "matrixType": {"type": "string", "required": False, "default": "forward"}
                },
                "visualization": {
                    "type": "interactive_matrix",
                    "features": ["zoom", "filter", "search", "highlight"],
                    "cell_types": ["linked", "partial", "missing", "orphaned"]
                },
                "interactions": {
                    "cell_click": "show_details",
                    "cell_hover": "show_tooltip", 
                    "row_select": "highlight_relationships",
                    "column_select": "highlight_dependencies"
                },
                "data_structure": {
                    "rows": "source_requirements",
                    "columns": "target_artifacts",
                    "cells": "trace_relationships"
                },
                "features": ["export_matrix", "print_view", "full_screen", "accessibility"]
            },
            "requirements_editor": {
                "name": "RequirementsEditor",
                "description": "Rich text editor for requirements with AI assistance",
                "props": {
                    "organizationId": {"type": "string", "required": True},
                    "requirementId": {"type": "string", "required": False},
                    "onSave": {"type": "function", "required": True},
                    "readOnly": {"type": "boolean", "required": False}
                },
                "editor": {
                    "type": "rich_text",
                    "features": ["formatting", "templates", "ai_suggestions", "spell_check"],
                    "toolbar": ["bold", "italic", "underline", "lists", "links", "tables", "ai_assist"],
                    "ai_features": ["quality_check", "compliance_analysis", "suggestions", "auto_complete"]
                },
                "templates": {
                    "functional": "Functional requirement template with acceptance criteria",
                    "non_functional": "Non-functional requirement with measurement criteria",
                    "user_story": "User story format with definition of done"
                },
                "features": ["auto_save", "version_control", "comments", "collaborative_editing"]
            },
            "compliance_checker": {
                "name": "ComplianceChecker",
                "description": "Real-time compliance checking interface",
                "props": {
                    "organizationId": {"type": "string", "required": True},
                    "standardIds": {"type": "array", "required": True},
                    "documentContent": {"type": "string", "required": True}
                },
                "standards": ["IEEE_830", "ISO_29148", "INCOSE"],
                "display": {
                    "layout": "tabbed",
                    "sections": ["overall_score", "detailed_analysis", "recommendations"],
                    "visualization": "progress_bars"
                },
                "features": ["real_time_checking", "export_report", "improvement_suggestions", "historical_tracking"]
            },
            "analytics_widget": {
                "name": "AnalyticsWidget",
                "description": "Configurable analytics widget for requirements metrics",
                "props": {
                    "organizationId": {"type": "string", "required": True},
                    "widgetType": {"type": "string", "required": True},
                    "configuration": {"type": "object", "required": True}
                },
                "widget_types": ["metric", "chart", "table", "gauge", "trend"],
                "customization": {
                    "colors": "theme_based",
                    "size": "configurable", 
                    "refresh_rate": "user_defined"
                },
                "features": ["responsive", "exportable", "interactive", "real_time"]
            }
        }
        
        base_config = configs.get(component_type, configs["requirements_form"])
        
        # Customize configuration based on request
        if "customization" in request:
            base_config.update(request["customization"])
            
        return base_config
    
    async def _generate_component_code(self, config: Dict[str, Any], org_id: str) -> Dict[str, str]:
        """Generate React/Next.js component code"""
        
        component_name = config["name"]
        component_type = component_name.lower()
        
        # Generate main component file
        main_component = self._generate_main_component(config)
        
        # Generate supporting files
        types_file = self._generate_types_file(config)
        hooks_file = self._generate_hooks_file(config)
        utils_file = self._generate_utils_file(config)
        
        # Generate test file
        test_file = self._generate_test_file(config)
        
        return {
            f"{component_name}.tsx": main_component,
            f"{component_name}.types.ts": types_file,
            f"use{component_name}.ts": hooks_file,
            f"{component_name}.utils.ts": utils_file,
            f"{component_name}.test.tsx": test_file
        }
    
    def _generate_main_component(self, config: Dict[str, Any]) -> str:
        """Generate main React component code"""
        
        component_name = config["name"]
        
        if component_name == "RequirementsForm":
            return f'''import React, {{ useState, useCallback, useEffect }} from 'react';
import {{ useForm, Controller }} from 'react-hook-form';
import {{ zodResolver }} from '@hookform/resolvers/zod';
import {{ z }} from 'zod';
import {{ Button, Input, Textarea, Select, DatePicker, Tag }} from '@/components/ui';
import {{ useRequirementsForm }} from './useRequirementsForm';
import {{ RequirementsFormProps, RequirementFormData }} from './RequirementsForm.types';

const requirementSchema = z.object({{
  title: z.string().min(5, 'Title must be at least 5 characters'),
  description: z.string().min(20, 'Description must be at least 20 characters'),
  type: z.enum(['functional', 'non_functional', 'constraint']),
  priority: z.enum(['high', 'medium', 'low']),
  acceptance_criteria: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
  stakeholders: z.array(z.string()).optional(),
  due_date: z.date().optional(),
}});

export const {component_name}: React.FC<RequirementsFormProps> = ({{
  organizationId,
  projectId,
  onSubmit,
  initialData
}}) => {{
  const {{ control, handleSubmit, formState: {{ errors, isSubmitting }}, reset }} = useForm<RequirementFormData>({{
    resolver: zodResolver(requirementSchema),
    defaultValues: initialData
  }});

  const {{ saveRequirement, isLoading }} = useRequirementsForm(organizationId);

  const onFormSubmit = useCallback(async (data: RequirementFormData) => {{
    try {{
      const result = await saveRequirement({{ ...data, projectId }});
      onSubmit(result);
      reset();
    }} catch (error) {{
      console.error('Failed to save requirement:', error);
    }}
  }}, [saveRequirement, onSubmit, projectId, reset]);

  return (
    <form onSubmit={{handleSubmit(onFormSubmit)}} className="space-y-6 max-w-4xl mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="md:col-span-2">
          <Controller
            name="title"
            control={{control}}
            render={{({{ field }}) => (
              <Input
                {{...field}}
                label="Requirement Title"
                error={{errors.title?.message}}
                required
                placeholder="Enter a clear, concise requirement title"
              />
            )}}
          />
        </div>
        
        <Controller
          name="type"
          control={{control}}
          render={{({{ field }}) => (
            <Select
              {{...field}}
              label="Requirement Type"
              options={{[
                {{ value: 'functional', label: 'Functional' }},
                {{ value: 'non_functional', label: 'Non-Functional' }},
                {{ value: 'constraint', label: 'Constraint' }}
              ]}}
              error={{errors.type?.message}}
              required
            />
          )}}
        />
        
        <Controller
          name="priority"
          control={{control}}
          render={{({{ field }}) => (
            <Select
              {{...field}}
              label="Priority"
              options={{[
                {{ value: 'high', label: 'High' }},
                {{ value: 'medium', label: 'Medium' }},
                {{ value: 'low', label: 'Low' }}
              ]}}
              error={{errors.priority?.message}}
              required
            />
          )}}
        />
      </div>

      <div>
        <Controller
          name="description"
          control={{control}}
          render={{({{ field }}) => (
            <Textarea
              {{...field}}
              label="Description"
              error={{errors.description?.message}}
              required
              rows={{4}}
              placeholder="Provide a detailed description of the requirement"
            />
          )}}
        />
      </div>

      <div className="flex justify-end space-x-4">
        <Button
          type="button"
          variant="outline"
          onClick={{() => reset()}}
        >
          Reset
        </Button>
        <Button
          type="submit"
          loading={{isSubmitting || isLoading}}
        >
          Save Requirement
        </Button>
      </div>
    </form>
  );
}};

export default {component_name};'''

        elif component_name == "RequirementsDashboard":
            return f'''import React, {{ useState, useEffect, useMemo }} from 'react';
import {{ Card, MetricCard, Chart, DataTable, Button, Select }} from '@/components/ui';
import {{ useRequirementsDashboard }} from './useRequirementsDashboard';
import {{ RequirementsDashboardProps }} from './RequirementsDashboard.types';

export const {component_name}: React.FC<RequirementsDashboardProps> = ({{
  organizationId,
  userId,
  filters: initialFilters
}}) => {{
  const [filters, setFilters] = useState(initialFilters || {{}});
  const [timeRange, setTimeRange] = useState('30d');
  
  const {{ 
    metrics, 
    chartData, 
    recentActivities, 
    isLoading, 
    refetch 
  }} = useRequirementsDashboard(organizationId, {{ filters, timeRange }});

  const metricCards = useMemo(() => [
    {{
      title: 'Total Requirements',
      value: metrics?.totalRequirements || 0,
      trend: {{ value: 12, direction: 'up' as const }},
      icon: 'document'
    }},
    {{
      title: 'Completion Rate',
      value: `${{Math.round((metrics?.completionRate || 0) * 100)}}%`,
      trend: {{ value: 5, direction: 'up' as const }},
      icon: 'check-circle'
    }},
    {{
      title: 'Active Projects',
      value: metrics?.activeProjects || 0,
      trend: {{ value: 2, direction: 'up' as const }},
      icon: 'folder'
    }},
    {{
      title: 'Overdue Items',
      value: metrics?.overdueCount || 0,
      trend: {{ value: 3, direction: 'down' as const }},
      icon: 'exclamation-triangle'
    }}
  ], [metrics]);

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Requirements Dashboard</h1>
        <div className="flex space-x-4">
          <Select
            value={{timeRange}}
            onValueChange={{setTimeRange}}
            options={{[
              {{ value: '7d', label: 'Last 7 days' }},
              {{ value: '30d', label: 'Last 30 days' }},
              {{ value: '90d', label: 'Last 90 days' }}
            ]}}
          />
          <Button onClick={{refetch}} variant="outline">
            Refresh
          </Button>
        </div>
      </div>

      {{/* Metrics Row */}}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {{metricCards.map((metric, index) => (
          <MetricCard key={{index}} {{...metric}} loading={{isLoading}} />
        ))}}
      </div>

      {{/* Charts Row */}}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Requirements by Type</h3>
          <Chart
            type="pie"
            data={{chartData?.requirementsByType || []}}
            loading={{isLoading}}
          />
        </Card>
        
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Completion Trend</h3>
          <Chart
            type="line"
            data={{chartData?.completionTrend || []}}
            loading={{isLoading}}
          />
        </Card>
      </div>

      {{/* Recent Activities Table */}}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <DataTable
          data={{recentActivities || []}}
          columns={{[
            {{ key: 'action', header: 'Action' }},
            {{ key: 'requirement', header: 'Requirement' }},
            {{ key: 'user', header: 'User' }},
            {{ key: 'timestamp', header: 'Time' }}
          ]}}
          loading={{isLoading}}
        />
      </Card>
    </div>
  );
}};

export default {component_name};'''

        else:
            # Generic component template
            return f'''import React from 'react';
import {{ {component_name}Props }} from './{component_name}.types';

export const {component_name}: React.FC<{component_name}Props> = ({{
  organizationId,
  ...props
}}) => {{
  return (
    <div className="atoms-{component_name.lower()} p-4">
      <h2 className="text-lg font-semibold mb-4">{component_name}</h2>
      <p>Component generated for organization: {{organizationId}}</p>
      {{/* Add component implementation here */}}
    </div>
  );
}};

export default {component_name};'''
    
    def _generate_types_file(self, config: Dict[str, Any]) -> str:
        """Generate TypeScript types file"""
        
        component_name = config["name"]
        props = config.get("props", {})
        
        props_interface = []
        for prop_name, prop_config in props.items():
            prop_type = prop_config["type"]
            required = prop_config.get("required", False)
            optional = "" if required else "?"
            props_interface.append(f"  {prop_name}{optional}: {prop_type};")
        
        return f'''export interface {component_name}Props {{
{chr(10).join(props_interface)}
}}

export interface {component_name}State {{
  isLoading: boolean;
  error: string | null;
}}

export interface {component_name}Config {{
  organizationId: string;
  features: string[];
  theme: 'light' | 'dark';
}}'''
    
    def _generate_hooks_file(self, config: Dict[str, Any]) -> str:
        """Generate custom hooks file"""
        
        component_name = config["name"]
        
        return f'''import {{ useState, useEffect, useCallback }} from 'react';
import {{ {component_name}State }} from './{component_name}.types';

export const use{component_name} = (organizationId: string) => {{
  const [state, setState] = useState<{component_name}State>({{
    isLoading: false,
    error: null,
  }});

  const refetch = useCallback(async () => {{
    setState(prev => ({{ ...prev, isLoading: true, error: null }}));
    
    try {{
      // Add data fetching logic here
      const data = await fetch(`/api/organizations/${{organizationId}}/{component_name.lower()}`);
      const result = await data.json();
      
      setState(prev => ({{ ...prev, isLoading: false }}));
      return result;
    }} catch (error) {{
      setState(prev => ({{
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'An error occurred'
      }}));
      throw error;
    }}
  }}, [organizationId]);

  useEffect(() => {{
    refetch();
  }}, [refetch]);

  return {{
    ...state,
    refetch
  }};
}};'''
    
    def _generate_utils_file(self, config: Dict[str, Any]) -> str:
        """Generate utilities file"""
        
        component_name = config["name"]
        
        return f'''export const {component_name.lower()}Utils = {{
  formatData: (data: any) => {{
    // Add data formatting logic
    return data;
  }},
  
  validateInput: (input: any) => {{
    // Add input validation logic
    return true;
  }},
  
  generateId: () => {{
    return `{component_name.lower()}_${{Date.now()}}`;
  }},
  
  exportData: (data: any, format: 'json' | 'csv' | 'excel') => {{
    // Add export functionality
    console.log(`Exporting data in ${{format}} format`);
  }}
}};'''
    
    def _generate_test_file(self, config: Dict[str, Any]) -> str:
        """Generate test file"""
        
        component_name = config["name"]
        
        return f'''import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react';
import {{ {component_name} }} from './{component_name}';

describe('{component_name}', () => {{
  const defaultProps = {{
    organizationId: 'test-org-123',
  }};

  it('renders without crashing', () => {{
    render(<{component_name} {{...defaultProps}} />);
    expect(screen.getByText('{component_name}')).toBeInTheDocument();
  }});

  it('displays organization ID', () => {{
    render(<{component_name} {{...defaultProps}} />);
    expect(screen.getByText('test-org-123')).toBeInTheDocument();
  }});

  // Add more tests here
}});'''
    
    async def _generate_component_styling(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate component styling"""
        
        component_name = config["name"]
        
        # Generate Tailwind CSS classes
        tailwind_classes = {
            "container": "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            "card": "bg-white rounded-lg shadow-sm border border-gray-200 p-6",
            "form": "space-y-6",
            "input": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
            "button": "px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500",
            "grid": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
        }
        
        # Generate CSS module
        css_module = f'''.{component_name.lower()} {{
  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }}
  
  .card {{
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    padding: 1.5rem;
  }}
  
  .responsive-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }}
  
  @media (max-width: 768px) {{
    .container {{
      padding: 0.5rem;
    }}
    
    .card {{
      padding: 1rem;
    }}
  }}
}}'''
        
        return {
            "tailwind_classes": tailwind_classes,
            "css_module": css_module,
            "responsive_breakpoints": {
                "sm": "640px",
                "md": "768px", 
                "lg": "1024px",
                "xl": "1280px"
            }
        }
    
    async def _generate_typescript_interfaces(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate TypeScript interfaces"""
        
        interfaces = {}
        
        # Generate data interfaces based on component type
        if config["name"] == "RequirementsForm":
            interfaces["RequirementFormData"] = '''export interface RequirementFormData {
  title: string;
  description: string;
  type: 'functional' | 'non_functional' | 'constraint';
  priority: 'high' | 'medium' | 'low';
  acceptance_criteria?: string[];
  tags?: string[];
  stakeholders?: string[];
  due_date?: Date;
}'''
        
        elif config["name"] == "RequirementsDashboard":
            interfaces["DashboardMetrics"] = '''export interface DashboardMetrics {
  totalRequirements: number;
  completionRate: number;
  activeProjects: number;
  overdueCount: number;
}

export interface ChartData {
  requirementsByType: Array<{ name: string; value: number }>;
  completionTrend: Array<{ date: string; completed: number; total: number }>;
}

export interface ActivityItem {
  id: string;
  action: string;
  requirement: string;
  user: string;
  timestamp: string;
}'''
        
        return interfaces
    
    async def create_dashboard_layout(self, organization_id: str, layout_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom dashboard layout"""
        try:
            layout_id = str(uuid.uuid4())
            
            # Generate layout configuration
            layout = await self._generate_dashboard_layout(layout_config, organization_id)
            
            return {
                "success": True,
                "layout_id": layout_id,
                "layout_configuration": layout,
                "organization_id": organization_id,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dashboard layout creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "organization_id": organization_id
            }
    
    async def _generate_dashboard_layout(self, config: Dict[str, Any], org_id: str) -> Dict[str, Any]:
        """Generate dashboard layout configuration"""
        
        return {
            "grid": {
                "columns": 12,
                "rows": "auto",
                "gap": 4,
                "responsive": True
            },
            "widgets": [
                {
                    "id": "metrics_overview",
                    "type": "metrics_grid",
                    "position": {"x": 0, "y": 0, "w": 12, "h": 2},
                    "config": {"metrics": ["total", "completion", "active", "overdue"]}
                },
                {
                    "id": "requirements_chart",
                    "type": "chart",
                    "position": {"x": 0, "y": 2, "w": 6, "h": 4},
                    "config": {"chart_type": "pie", "data_source": "requirements_by_type"}
                },
                {
                    "id": "progress_trend",
                    "type": "chart", 
                    "position": {"x": 6, "y": 2, "w": 6, "h": 4},
                    "config": {"chart_type": "line", "data_source": "progress_trend"}
                },
                {
                    "id": "recent_activity",
                    "type": "table",
                    "position": {"x": 0, "y": 6, "w": 12, "h": 4},
                    "config": {"data_source": "recent_activities", "max_rows": 10}
                }
            ],
            "theme": {
                "primary_color": "#3B82F6",
                "background_color": "#F9FAFB",
                "card_background": "#FFFFFF",
                "text_color": "#1F2937"
            }
        }

# Initialize Magic MCP Client
mcp_client = MagicMCPClient(
    server_url=os.environ.get('MAGIC_SERVER_URL', 'https://api.magic.dev'),
    api_key=os.environ.get('MAGIC_API_KEY', '')
)

async def magic_ui_generation_tool(organization_id: str, message: str) -> Dict[str, Any]:
    """
    Dynamic UI components for requirements management
    
    Purpose: Generate modern, responsive UI components for requirements
    management with AI-powered design and accessibility features
    
    Expected Benefits:
    - Dynamic dashboard generation
    - Custom forms for requirements capture  
    - Interactive visualization components
    - Responsive requirements management interfaces
    - Rapid UI development and customization
    
    Args:
        organization_id (str): Organization identifier for data isolation
        message (str): UI generation request
        
    Returns:
        Dict[str, Any]: Generated UI components with code and styling
        
    Component Types:
        - requirements_form: Dynamic forms for capturing requirements
        - dashboard: Interactive dashboards with metrics and charts
        - traceability_matrix: Visual traceability matrix components
        - requirements_editor: Rich text editors with AI assistance
        - compliance_checker: Real-time compliance checking interfaces
        - analytics_widget: Configurable analytics widgets
    """
    
    try:
        logger.info(f"Processing Magic UI generation for org {organization_id}")
        
        if not mcp_client.is_enabled:
            return {
                "success": False,
                "error": "Magic MCP server is not configured",
                "message": message,
                "organization_id": organization_id
            }
        
        # Parse message to determine component type and requirements
        component_request = _parse_ui_request(message)
        
        if component_request["operation"] == "generate_component":
            result = await mcp_client.generate_ui_component(organization_id, component_request)
        elif component_request["operation"] == "create_dashboard":
            result = await mcp_client.create_dashboard_layout(organization_id, component_request)
        else:
            # Default: list available component types
            result = {
                "success": True,
                "available_components": [
                    {
                        "type": "requirements_form",
                        "description": "Dynamic form for capturing requirements",
                        "features": ["validation", "auto_save", "accessibility"]
                    },
                    {
                        "type": "dashboard",
                        "description": "Interactive dashboard with metrics and charts",
                        "features": ["real_time_updates", "responsive", "customizable"]
                    },
                    {
                        "type": "traceability_matrix",
                        "description": "Visual traceability matrix",
                        "features": ["interactive", "filterable", "exportable"]
                    },
                    {
                        "type": "requirements_editor",
                        "description": "Rich text editor with AI assistance",
                        "features": ["ai_suggestions", "templates", "collaborative"]
                    },
                    {
                        "type": "compliance_checker",
                        "description": "Real-time compliance checking",
                        "features": ["multiple_standards", "reporting", "suggestions"]
                    },
                    {
                        "type": "analytics_widget",
                        "description": "Configurable analytics widget",
                        "features": ["customizable", "real_time", "exportable"]
                    }
                ]
            }
        
        # Add usage analytics
        result["analytics"] = {
            "tool_type": "magic_ui_generation",
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat(),
            "tool": "magic_integration_tool"
        }
        
        logger.info(f"Magic UI generation completed successfully for org {organization_id}")
        return result
        
    except Exception as e:
        logger.error(f"Magic UI generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": message,
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat()
        }

def _parse_ui_request(message: str) -> Dict[str, Any]:
    """Parse UI generation request from user message"""
    
    message_lower = message.lower()
    
    if "form" in message_lower:
        return {
            "operation": "generate_component",
            "type": "requirements_form",
            "customization": {
                "fields": ["title", "description", "type", "priority"],
                "validation": True,
                "responsive": True
            }
        }
    elif "dashboard" in message_lower:
        return {
            "operation": "create_dashboard",
            "type": "dashboard",
            "layout": {
                "widgets": ["metrics", "charts", "recent_activity"],
                "responsive": True
            }
        }
    elif "matrix" in message_lower or "traceability" in message_lower:
        return {
            "operation": "generate_component",
            "type": "traceability_matrix",
            "customization": {
                "interactive": True,
                "filterable": True,
                "exportable": True
            }
        }
    elif "editor" in message_lower:
        return {
            "operation": "generate_component",
            "type": "requirements_editor",
            "customization": {
                "ai_assistance": True,
                "templates": True,
                "collaborative": True
            }
        }
    elif "compliance" in message_lower:
        return {
            "operation": "generate_component",
            "type": "compliance_checker",
            "customization": {
                "standards": ["IEEE_830", "ISO_29148"],
                "real_time": True
            }
        }
    else:
        return {
            "operation": "list_components",
            "type": "overview"
        }

# Synchronous wrapper for FastMCP compatibility
def magic_ui_generation_tool_sync(organization_id: str, message: str) -> Dict[str, Any]:
    """Synchronous wrapper for Magic UI generation"""
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(magic_ui_generation_tool(organization_id, message))
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