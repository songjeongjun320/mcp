# Supabase Database Schema Analysis

**Database:** ydogoylwenufckscqijp.supabase.co  
**Analysis Date:** 2025-01-08  
**Total Tables:** 34  

## Executive Summary

This Supabase database appears to be a comprehensive requirements management and project collaboration system. The schema includes:

- **User Management**: Organizations, profiles, members, invitations, roles
- **Project Management**: Projects, documents, blocks, requirements
- **Testing & Quality Assurance**: Test requirements, execution tracking, matrices
- **Collaboration**: Diagrams (Excalidraw & React Flow), assignments, trace links
- **Billing & Compliance**: Stripe integration, usage tracking, audit logs
- **OAuth Authentication**: Complete OAuth 2.0 implementation

## Database Architecture

### Core Entity Relationships

```
Organizations (1) → (N) Projects → (N) Documents → (N) Blocks → (N) Requirements
                                                             → (N) Columns
                                                             
Organizations (1) → (N) Members
Projects (1) → (N) Members
Documents (1) → (N) Properties

Requirements (1) → (N) Requirement Tests ← (1) Test Requirements
Requirements (1) → (N) Assignments
Requirements (1) → (N) Trace Links
Requirements (1) → (N) Diagram Element Links
```

### Data Flow Analysis

1. **User Onboarding**: Profiles → Organization Creation/Invitation → Project Access
2. **Content Creation**: Projects → Documents → Blocks → Requirements
3. **Testing Workflow**: Requirements → Test Requirements → Requirement Tests (Execution)
4. **Collaboration**: Requirements → Assignments → Trace Links → Diagrams
5. **Audit Trail**: All changes → Audit Logs → Compliance tracking

## Detailed Table Analysis

### 1. User & Organization Management

#### `profiles` (User Accounts)
**Purpose**: Core user account information and preferences
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `email` (TEXT, required) - User identifier
  - `full_name` (TEXT) - Display name
  - `avatar_url` (TEXT) - Profile image
  - `personal_organization_id` (UUID) - Personal workspace
  - `current_organization_id` (UUID) - Active workspace
  - `job_title` (TEXT) - Professional role
  - `preferences` (JSONB) - User settings
  - `status` (user_status ENUM) - Account state
  - `is_approved` (BOOLEAN, required) - Account approval status
- **Audit Fields**: created_at, updated_at, is_deleted, deleted_at, deleted_by
- **Business Logic**: Soft delete pattern, approval workflow

#### `organizations` (Workspaces)
**Purpose**: Multi-tenant workspace management with billing
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `name` (TEXT, required) - Organization name
  - `slug` (TEXT, required) - URL identifier
  - `type` (organization_type ENUM, required) - Organization category
  - `billing_plan` (billing_plan ENUM, required) - Subscription tier
  - `billing_cycle` (pricing_plan_interval ENUM, required) - Payment frequency
  - `max_members` (INTEGER, required) - Capacity limit
  - `max_monthly_requests` (BIGINT, required) - Usage limit
  - `settings` (JSONB) - Configuration
  - `metadata` (JSONB) - Additional data
  - `member_count` (INTEGER) - Current members
  - `storage_used` (BIGINT) - Storage consumption
  - `owner_id` (UUID) - Primary owner
- **Audit Fields**: Standard soft delete pattern
- **Business Logic**: Resource limiting, multi-tenancy

#### `organization_members` (Membership)
**Purpose**: Organization membership and role management
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `organization_id` → organizations.id
  - `user_id` → profiles.id
- **Core Fields**:
  - `role` (user_role_type ENUM, required) - Permission level
  - `status` (user_status ENUM) - Member state
  - `permissions` (JSONB) - Custom permissions
  - `last_active_at` (TIMESTAMP) - Activity tracking
- **Audit Fields**: Standard soft delete pattern

#### `organization_invitations` (Invitations)
**Purpose**: Pending organization invitations
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `organization_id` → organizations.id
- **Core Fields**:
  - `email` (TEXT, required) - Invitee email
  - `role` (user_role_type ENUM, required) - Intended role
  - `token` (UUID, required) - Invitation token
  - `status` (invitation_status ENUM, required) - Invitation state
  - `expires_at` (TIMESTAMP, required) - Expiration time
  - `metadata` (JSONB) - Additional data
- **Audit Fields**: Standard pattern

### 2. Project & Document Management

#### `projects` (Projects)
**Purpose**: Project containers for requirements and documents
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `organization_id` → organizations.id
- **Core Fields**:
  - `name` (TEXT, required) - Project name
  - `slug` (TEXT, required) - URL identifier
  - `description` (TEXT) - Project description
  - `visibility` (visibility ENUM, required) - Access control
  - `status` (project_status ENUM, required) - Project state
  - `settings` (JSONB) - Project configuration
  - `tags` (TEXT[]) - Categorization
  - `metadata` (JSONB) - Additional data
  - `star_count` (INTEGER) - Popularity metric
  - `version` (INTEGER) - Version tracking
- **Ownership**: created_by, updated_by, owned_by
- **Audit Fields**: Standard soft delete pattern

#### `project_members` (Project Access)
**Purpose**: Project-level access control
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `project_id` → projects.id
  - `org_id` → organizations.id
- **Core Fields**:
  - `user_id` (UUID, required) - Member identifier
  - `role` (project_role ENUM, required) - Project permissions
  - `status` (user_status ENUM) - Member state
  - `permissions` (JSONB) - Custom permissions
  - `last_accessed_at` (TIMESTAMP) - Activity tracking
- **Audit Fields**: Standard soft delete pattern

#### `project_invitations` (Project Invitations)
**Purpose**: Pending project invitations
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `project_id` → projects.id
- **Core Fields**:
  - `email` (TEXT, required) - Invitee email
  - `role` (project_role ENUM, required) - Intended role
  - `token` (UUID, required) - Invitation token
  - `status` (invitation_status ENUM, required) - State
  - `expires_at` (TIMESTAMP, required) - Expiration
- **Audit Fields**: Standard pattern

#### `documents` (Document Containers)
**Purpose**: Document structure within projects
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `project_id` → projects.id
- **Core Fields**:
  - `name` (TEXT, required) - Document name
  - `slug` (TEXT, required) - URL identifier
  - `description` (TEXT) - Document description
  - `tags` (TEXT[]) - Categorization
  - `version` (BIGINT, required) - Version control
- **Audit Fields**: Standard soft delete pattern

#### `blocks` (Document Blocks)
**Purpose**: Structured content blocks within documents
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `document_id` → documents.id
  - `org_id` → organizations.id
- **Core Fields**:
  - `type` (TEXT, required) - Block type
  - `name` (TEXT, required) - Block identifier
  - `position` (INTEGER, required) - Display order
  - `content` (JSONB) - Block content
  - `version` (BIGINT, required) - Version tracking
- **Audit Fields**: Standard soft delete pattern

### 3. Requirements Management

#### `requirements` (Core Requirements)
**Purpose**: Central requirements repository with rich metadata
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `document_id` → documents.id
  - `block_id` → blocks.id
- **Core Fields**:
  - `external_id` (TEXT) - External system reference
  - `name` (TEXT, required) - Requirement title
  - `description` (TEXT) - Detailed description
  - `status` (requirement_status ENUM, required) - Current state
  - `format` (requirement_format ENUM, required) - Format type
  - `priority` (requirement_priority ENUM, required) - Priority level
  - `level` (requirement_level ENUM, required) - Requirement level
  - `type` (TEXT) - Requirement type
  - `position` (DOUBLE PRECISION, required) - Display order
  - `tags` (TEXT[]) - Categorization
  - `original_requirement` (TEXT) - Source text
  - `enchanced_requirement` (TEXT) - Processed text
  - `ai_analysis` (JSONB) - AI processing results
  - `properties` (JSONB) - Custom properties
  - `version` (BIGINT, required) - Version tracking
- **Audit Fields**: Standard soft delete pattern

#### `properties` (Custom Properties)
**Purpose**: Configurable metadata fields for requirements
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `org_id` → organizations.id
  - `project_id` → projects.id
  - `document_id` → documents.id
- **Core Fields**:
  - `name` (TEXT, required) - Property name
  - `property_type` (TEXT, required) - Data type
  - `options` (JSONB) - Configuration options
  - `scope` (TEXT) - Application scope
  - `is_base` (BOOLEAN) - System property flag
- **Audit Fields**: created_at, updated_at, created_by, updated_by

#### `columns` (Table Columns)
**Purpose**: Custom column configuration for requirements tables
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `block_id` → blocks.id
  - `property_id` → properties.id
- **Core Fields**:
  - `position` (DOUBLE PRECISION, required) - Column order
  - `width` (INTEGER) - Column width
  - `is_hidden` (BOOLEAN) - Visibility flag
  - `is_pinned` (BOOLEAN) - Pin flag
  - `default_value` (TEXT) - Default value
- **Audit Fields**: Standard pattern

### 4. Testing & Quality Assurance

#### `test_req` (Test Requirements)
**Purpose**: Test case definitions and specifications
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `project_id` → projects.id
- **Core Fields**:
  - `test_id` (TEXT) - External test identifier
  - `title` (TEXT, required) - Test case title
  - `description` (TEXT) - Detailed description
  - `test_type` (test_type ENUM, required) - Test category
  - `priority` (test_priority ENUM, required) - Priority level
  - `status` (test_status ENUM, required) - Current state
  - `method` (test_method ENUM, required) - Test approach
  - `result` (TEXT) - Test result
  - `expected_results` (TEXT) - Expected outcomes
  - `preconditions` (TEXT) - Setup requirements
  - `test_steps` (JSONB) - Step-by-step instructions
  - `estimated_duration` (INTERVAL) - Time estimate
  - `category` (TEXT[]) - Test categories
  - `test_environment` (TEXT) - Environment requirements
  - `attachments` (JSONB) - File attachments
  - `version` (TEXT) - Version information
  - `is_active` (BOOLEAN) - Active status
- **Audit Fields**: created_at, updated_at, created_by, updated_by

#### `requirement_tests` (Test Execution)
**Purpose**: Links requirements to test executions with results
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `requirement_id` → requirements.id
  - `test_id` → test_req.id
- **Core Fields**:
  - `execution_status` (execution_status ENUM, required) - Test result
  - `result_notes` (TEXT) - Execution notes
  - `executed_at` (TIMESTAMP) - Execution time
  - `executed_by` (UUID) - Executor
  - `execution_environment` (TEXT) - Test environment
  - `execution_version` (TEXT) - Version tested
  - `defects` (JSONB) - Found issues
  - `evidence_artifacts` (JSONB) - Supporting evidence
  - `external_test_id` (TEXT) - External system reference
  - `external_req_id` (TEXT) - External requirement reference
- **Audit Fields**: created_at, updated_at

#### `test_matrix_views` (Test Views)
**Purpose**: Configurable test matrix views for project analysis
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `project_id` → projects.id
- **Core Fields**:
  - `name` (TEXT, required) - View name
  - `configuration` (JSONB, required) - View settings
  - `is_active` (BOOLEAN) - Active status
  - `is_default` (BOOLEAN) - Default view flag
- **Audit Fields**: created_at, updated_at, created_by, updated_by

### 5. Collaboration & Traceability

#### `assignments` (Task Assignments)
**Purpose**: Assignment tracking for requirements and other entities
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `entity_id` (UUID, required) - Assigned entity
  - `entity_type` (entity_type ENUM, required) - Entity type
  - `assignee_id` (UUID, required) - Assigned user
  - `role` (assignment_role ENUM, required) - Assignment role
  - `status` (requirement_status ENUM, required) - Assignment status
  - `comment` (TEXT) - Assignment notes
  - `due_date` (TIMESTAMP) - Due date
  - `completed_at` (TIMESTAMP) - Completion time
  - `version` (BIGINT, required) - Version tracking
- **Audit Fields**: Standard soft delete pattern

#### `trace_links` (Traceability Links)
**Purpose**: Relationships between different entities for traceability
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `source_id` (UUID, required) - Source entity
  - `target_id` (UUID, required) - Target entity
  - `source_type` (entity_type ENUM, required) - Source type
  - `target_type` (entity_type ENUM, required) - Target type
  - `link_type` (trace_link_type ENUM, required) - Relationship type
  - `description` (TEXT) - Link description
  - `version` (BIGINT, required) - Version tracking
- **Audit Fields**: Standard soft delete pattern

### 6. Diagram & Visualization

#### `excalidraw_diagrams` (Excalidraw Diagrams)
**Purpose**: Collaborative drawing diagrams
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `name` (TEXT) - Diagram name
  - `diagram_data` (JSONB) - Excalidraw data
  - `thumbnail_url` (TEXT) - Preview image
  - `organization_id` (UUID) - Organization context
  - `project_id` (UUID) - Project context
- **Audit Fields**: created_at, updated_at, created_by, updated_by

#### `diagram_element_links` (Element Links)
**Purpose**: Links diagram elements to requirements
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `diagram_id` → excalidraw_diagrams.id
  - `requirement_id` → requirements.id
- **Core Fields**:
  - `element_id` (TEXT, required) - Excalidraw element ID
  - `link_type` (VARCHAR) - Link type (manual/auto-detected)
  - `metadata` (JSONB) - Additional link data
- **Audit Fields**: created_at, updated_at, created_by

#### `diagram_element_links_with_details` (Enhanced Element Links)
**Purpose**: View combining diagram links with requirement details
- **Primary Key**: `id` (UUID)
- **Combined Fields**: Includes all fields from diagram_element_links plus:
  - `diagram_name` (TEXT) - Diagram name
  - `project_id` (UUID) - Project context
  - `organization_id` (UUID) - Organization context
  - `requirement_name` (TEXT) - Requirement name
  - `requirement_description` (TEXT) - Requirement description
  - `requirement_external_id` (TEXT) - External ID
  - `requirement_priority` (requirement_priority) - Priority
  - `requirement_status` (requirement_status) - Status
  - `created_by_email` (VARCHAR) - Creator email

#### `react_flow_diagrams` (React Flow Diagrams)
**Purpose**: Structured flow diagrams with nodes and edges
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `project_id` → projects.id
- **Core Fields**:
  - `name` (VARCHAR, required) - Diagram name
  - `description` (TEXT) - Diagram description
  - `nodes` (JSONB, required) - Flow nodes
  - `edges` (JSONB, required) - Flow connections
  - `viewport` (JSONB) - View configuration
  - `diagram_type` (VARCHAR) - Diagram type
  - `layout_algorithm` (VARCHAR) - Layout method
  - `theme` (VARCHAR) - Visual theme
  - `settings` (JSONB) - Configuration
  - `metadata` (JSONB) - Additional data
- **Audit Fields**: created_at, updated_at, created_by, updated_by

### 7. External Integration

#### `external_documents` (External Documents)
**Purpose**: Links to external document sources
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `organization_id` (UUID, required) - Organization context
  - `name` (TEXT, required) - Document name
  - `url` (TEXT) - External URL
  - `type` (TEXT) - Document type
  - `size` (BIGINT) - File size
  - `gumloop_name` (TEXT) - Gumloop integration
- **Ownership**: owned_by, created_by, updated_by
- **Audit Fields**: Standard soft delete pattern

### 8. Authentication & OAuth

#### `oauth_clients` (OAuth Clients)
**Purpose**: OAuth 2.0 client applications
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `client_id` (VARCHAR, required) - OAuth client ID
  - `client_name` (VARCHAR, required) - Application name
  - `client_secret` (VARCHAR) - Client secret
  - `redirect_uris` (JSONB, required) - Allowed redirects
  - `grant_types` (JSONB, required) - Supported grants
  - `response_types` (JSONB, required) - Response types
  - `scope` (TEXT) - OAuth scopes
  - `is_public` (BOOLEAN) - Public client flag
- **Audit Fields**: created_at, updated_at

#### `oauth_authorization_codes` (Authorization Codes)
**Purpose**: OAuth 2.0 authorization code storage
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `user_id` → profiles.id
- **Core Fields**:
  - `code` (VARCHAR, required) - Authorization code
  - `client_id` (VARCHAR, required) - OAuth client
  - `redirect_uri` (TEXT, required) - Redirect URI
  - `code_challenge` (VARCHAR, required) - PKCE challenge
  - `code_challenge_method` (VARCHAR, required) - PKCE method
  - `scope` (TEXT) - Requested scopes
  - `state` (VARCHAR) - OAuth state
  - `expires_at` (TIMESTAMP, required) - Expiration
- **Audit Fields**: created_at

#### `oauth_access_tokens` (Access Tokens)
**Purpose**: OAuth 2.0 access token management
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `token_hash` (VARCHAR, required) - Token hash
  - `client_id` (VARCHAR, required) - OAuth client
  - `user_id` (UUID) - Token owner
  - `scope` (TEXT) - Token scopes
  - `expires_at` (TIMESTAMP, required) - Expiration
- **Audit Fields**: created_at, last_used_at

#### `oauth_refresh_tokens` (Refresh Tokens)
**Purpose**: OAuth 2.0 refresh token management
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `user_id` → profiles.id
- **Core Fields**:
  - `token` (VARCHAR, required) - Refresh token
  - `client_id` (VARCHAR, required) - OAuth client
  - `scope` (TEXT) - Token scopes
  - `expires_at` (TIMESTAMP, required) - Expiration
- **Audit Fields**: created_at, last_used_at

### 9. Billing & Usage

#### `stripe_customers` (Stripe Integration)
**Purpose**: Stripe billing customer management
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `organization_id` → organizations.id
- **Core Fields**:
  - `stripe_customer_id` (TEXT) - Stripe customer ID
  - `stripe_subscription_id` (TEXT) - Subscription ID
  - `subscription_status` (subscription_status ENUM, required) - Status
  - `price_id` (TEXT) - Stripe price ID
  - `current_period_start` (TIMESTAMP) - Billing period start
  - `current_period_end` (TIMESTAMP) - Billing period end
  - `cancel_at_period_end` (BOOLEAN) - Cancellation flag
  - `payment_method_last4` (TEXT) - Card last 4 digits
  - `payment_method_brand` (TEXT) - Card brand
- **Audit Fields**: created_at, updated_at

#### `billing_cache` (Billing Cache)
**Purpose**: Cached billing status and usage data
- **Primary Key**: `organization_id` (UUID)
- **Foreign Keys**: `organization_id` → organizations.id
- **Core Fields**:
  - `billing_status` (JSONB, required) - Current billing state
  - `current_period_usage` (JSONB, required) - Usage metrics
  - `synced_at` (TIMESTAMP, required) - Last sync time
  - `period_start` (TIMESTAMP, required) - Period start
  - `period_end` (TIMESTAMP, required) - Period end

#### `usage_logs` (Usage Tracking)
**Purpose**: Feature usage tracking for billing
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `organization_id` → organizations.id
- **Core Fields**:
  - `user_id` (UUID, required) - User identifier
  - `feature` (TEXT, required) - Feature name
  - `quantity` (INTEGER, required) - Usage amount
  - `unit_type` (TEXT, required) - Unit measurement
  - `metadata` (JSONB) - Additional usage data
- **Audit Fields**: created_at

### 10. System Management

#### `user_roles` (User Roles)
**Purpose**: Role assignments across different scopes
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `project_id` → projects.id
  - `org_id` → organizations.id
  - `document_id` → documents.id
- **Core Fields**:
  - `user_id` (UUID, required) - User identifier
  - `admin_role` (user_role_type) - Admin role
  - `project_role` (project_role) - Project role
  - `document_role` (project_role) - Document role
- **Audit Fields**: created_at, updated_at

#### `notifications` (User Notifications)
**Purpose**: In-app notification system
- **Primary Key**: `id` (UUID)
- **Core Fields**:
  - `user_id` (UUID, required) - Recipient
  - `type` (notification_type ENUM, required) - Notification type
  - `title` (TEXT, required) - Notification title
  - `message` (TEXT) - Notification content
  - `unread` (BOOLEAN) - Read status
  - `metadata` (JSONB) - Additional data
  - `read_at` (TIMESTAMP) - Read timestamp
- **Audit Fields**: created_at

#### `audit_logs` (Comprehensive Audit Trail)
**Purpose**: Complete system audit logging for compliance
- **Primary Key**: `id` (UUID)
- **Foreign Keys**:
  - `user_id` → profiles.id
  - `organization_id` → organizations.id
  - `project_id` → projects.id
- **Core Fields**:
  - `entity_id` (UUID, required) - Affected entity
  - `entity_type` (TEXT, required) - Entity type
  - `action` (TEXT, required) - Performed action
  - `actor_id` (UUID) - Action performer
  - `old_data` (JSONB) - Previous state
  - `new_data` (JSONB) - New state
  - `metadata` (JSONB) - Action metadata
  - `event_type` (audit_event_type ENUM) - Event category
  - `severity` (audit_severity ENUM) - Event severity
  - `session_id` (TEXT) - User session
  - `ip_address` (INET) - Client IP
  - `user_agent` (TEXT) - Client agent
  - `resource_type` (resource_type ENUM) - Resource type
  - `resource_id` (UUID) - Resource identifier
  - `description` (TEXT) - Human-readable description
  - `details` (JSONB) - Detailed information
  - `soc2_control` (TEXT) - SOC2 control mapping
  - `compliance_category` (TEXT) - Compliance category
  - `risk_level` (TEXT) - Risk assessment
  - `threat_indicators` (TEXT[]) - Security indicators
  - `source_system` (TEXT) - Source system
  - `correlation_id` (UUID) - Event correlation
- **Audit Fields**: created_at, updated_at, timestamp

### 11. Summary Views

#### `document_summary` (Document Summary)
**Purpose**: Aggregated document statistics
- **Primary Key**: `document_id` (UUID)
- **Foreign Keys**: `project_id` → projects.id
- **Core Fields**:
  - `document_name` (TEXT) - Document name
  - `block_count` (BIGINT) - Number of blocks
  - `requirement_count` (BIGINT) - Number of requirements
- **Audit Fields**: updated_at

## Custom Data Types (ENUMS)

### User & Organization Management
- `user_status`: Account states (active, inactive, suspended, etc.)
- `user_role_type`: Organization roles (owner, admin, member, viewer, etc.)
- `organization_type`: Organization categories
- `billing_plan`: Subscription tiers (free, pro, enterprise, etc.)
- `pricing_plan_interval`: Billing cycles (monthly, yearly, etc.)
- `invitation_status`: Invitation states (pending, accepted, expired, etc.)

### Project Management
- `project_status`: Project states (active, archived, draft, etc.)
- `project_role`: Project-specific roles
- `visibility`: Access levels (public, private, organization, etc.)

### Requirements Management
- `requirement_status`: Requirement states (draft, approved, implemented, etc.)
- `requirement_format`: Format types (natural language, formal, etc.)
- `requirement_priority`: Priority levels (low, medium, high, critical, etc.)
- `requirement_level`: Requirement levels (system, component, feature, etc.)
- `entity_type`: Entity categories (requirement, test, document, etc.)
- `assignment_role`: Assignment types (assignee, reviewer, approver, etc.)
- `trace_link_type`: Relationship types (derived_from, satisfies, conflicts_with, etc.)

### Testing & Quality
- `test_type`: Test categories (unit, integration, system, acceptance, etc.)
- `test_priority`: Test priority levels
- `test_status`: Test states (planned, active, passed, failed, etc.)
- `test_method`: Test approaches (manual, automated, etc.)
- `execution_status`: Test execution results

### System & Compliance
- `notification_type`: Notification categories
- `audit_event_type`: Audit event categories
- `audit_severity`: Severity levels (low, medium, high, critical, etc.)
- `resource_type`: Resource categories
- `subscription_status`: Stripe subscription states

## Security & Compliance Features

### Row Level Security (RLS)
- **Multi-tenant Isolation**: Organization-based data segregation
- **Role-based Access**: Fine-grained permissions per entity type
- **Project-level Access**: Document and requirement access control

### Audit Trail
- **Comprehensive Logging**: All entity changes tracked
- **SOC2 Compliance**: Control mapping and compliance categorization
- **Risk Assessment**: Threat indicators and risk level tracking
- **Data Lineage**: Old/new state tracking for all changes

### Data Protection
- **Soft Delete Pattern**: Consistent across all major entities
- **Version Control**: Entity versioning for change tracking
- **Metadata Preservation**: Created/updated by tracking
- **Approval Workflows**: User approval and invitation systems

## Performance Considerations

### Indexing Strategy
- **Primary Keys**: All UUID primary keys automatically indexed
- **Foreign Keys**: Automatic indexing on all foreign key relationships
- **Composite Indexes**: Likely on (organization_id, project_id) combinations
- **Search Optimization**: Text search on names, descriptions, and content

### Data Volume Estimates
- **High Volume Tables**: audit_logs, usage_logs, requirement_tests
- **Medium Volume**: requirements, test_req, assignments, trace_links
- **Low Volume**: organizations, projects, documents, users

### Caching Strategy
- **Billing Cache**: Pre-computed billing status and usage
- **Document Summary**: Aggregated statistics for performance
- **User Sessions**: OAuth token management for API performance

## Integration Points

### External Systems
- **Stripe**: Complete billing integration with webhooks
- **OAuth 2.0**: Standard authentication for API access
- **External Documents**: File system or cloud storage integration
- **Gumloop**: Document processing integration

### API Architecture
- **REST API**: 55 endpoints with full CRUD operations
- **Real-time Updates**: Likely WebSocket or SSE for collaborative features
- **Bulk Operations**: Test execution and requirement import/export
- **Search API**: Full-text search across requirements and documents

## Recommendations

### Performance Optimization
1. **Implement Connection Pooling**: For high-concurrent access
2. **Add Read Replicas**: For reporting and analytics queries
3. **Optimize JSON Queries**: Index JSONB columns for frequent searches
4. **Implement Caching**: Redis for session and frequently accessed data

### Security Enhancements
1. **API Rate Limiting**: Prevent abuse of OAuth endpoints
2. **Data Encryption**: Encrypt sensitive JSONB fields at rest
3. **Backup Strategy**: Automated backups with point-in-time recovery
4. **Monitoring**: Real-time alerting on audit log anomalies

### Scalability Considerations
1. **Partition Large Tables**: audit_logs and usage_logs by date
2. **Archive Old Data**: Implement data retention policies
3. **Optimize Queries**: Add indexes for common query patterns
4. **Load Balancing**: Distribute read traffic across replicas

---

**Analysis completed on 2025-01-08 using Supabase OpenAPI specification introspection**