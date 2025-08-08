# Atoms Database Schema Documentation

**Database**: Supabase PostgreSQL Database  
**URL**: https://ydogoylwenufckscqijp.supabase.co  
**Analysis Date**: 2025-01-08  
**Total Tables**: 34  

## Executive Summary

This comprehensive requirements management and project collaboration system serves as a sophisticated platform for managing complex product development workflows. The database architecture supports multi-tenant organizations, project hierarchies, requirements traceability, testing frameworks, and compliance auditing.

### Core System Capabilities

- **Multi-Tenant Architecture**: Complete organization-based isolation with billing integration
- **Requirements Management**: Rich metadata, version control, and AI-enhanced processing
- **Project Collaboration**: Document hierarchies, assignments, and traceability matrices
- **Testing Framework**: Complete test lifecycle from planning to execution
- **Compliance & Audit**: SOC2-ready audit trails with risk assessment
- **OAuth Integration**: Standard OAuth 2.0 with PKCE support for API access
- **Billing Integration**: Stripe-powered subscription management with usage tracking

## Database Architecture Overview

### Entity Relationship Hierarchy

```
Organizations (Multi-tenant Root)
├── Members (Role-based Access)
├── Projects
│   ├── Members (Project-level Permissions)
│   ├── Documents
│   │   ├── Properties (Custom Metadata)
│   │   ├── Blocks (Content Structure)
│   │   │   ├── Columns (Table Configuration)
│   │   │   └── Requirements (Core Business Logic)
│   │   │       ├── Assignments (Task Management)
│   │   │       ├── Trace Links (Relationship Mapping)
│   │   │       ├── Requirement Tests (QA Integration)
│   │   │       └── Diagram Links (Visual Mapping)
│   │   ├── Test Requirements (QA Definitions)
│   │   └── Test Matrix Views (Analysis Views)
│   ├── Excalidraw Diagrams (Collaborative Drawing)
│   └── React Flow Diagrams (Structured Flows)
├── External Documents (Integration)
├── Usage Logs (Billing Tracking)
└── Audit Logs (Compliance)
```

### Data Flow Patterns

1. **User Onboarding**: `profiles` → `organization_invitations` → `organization_members` → `project_members`
2. **Content Creation**: `projects` → `documents` → `blocks` → `requirements`
3. **Quality Assurance**: `test_req` → `requirement_tests` → execution tracking
4. **Collaboration**: `assignments` → `trace_links` → `diagram_element_links`
5. **Compliance**: All operations → `audit_logs` → SOC2 controls

## Detailed Schema Analysis

### 1. User & Organization Management

#### profiles (User Accounts)
**Purpose**: Core user account management with preferences and multi-organization support

**Key Fields**:
- `id` (UUID, PK) - User identifier
- `email` (TEXT, REQUIRED) - Primary login credential
- `full_name` (TEXT) - Display name
- `personal_organization_id` (UUID) - Individual workspace
- `current_organization_id` (UUID) - Active workspace context
- `job_title` (TEXT) - Professional role
- `preferences` (JSONB) - User settings and configuration
- `status` (user_status ENUM) - Account state management
- `is_approved` (BOOLEAN, REQUIRED) - Account approval workflow

**Business Logic**: Soft delete pattern, approval workflow, multi-organization context switching

#### organizations (Workspaces)
**Purpose**: Multi-tenant workspace containers with billing and resource management

**Key Fields**:
- `id` (UUID, PK) - Organization identifier
- `name` (TEXT, REQUIRED) - Organization name
- `slug` (TEXT, REQUIRED) - URL-safe identifier
- `type` (organization_type ENUM, REQUIRED) - Organization classification
- `billing_plan` (billing_plan ENUM, REQUIRED) - Subscription tier
- `billing_cycle` (pricing_plan_interval ENUM, REQUIRED) - Payment frequency
- `max_members` (INTEGER, REQUIRED) - Capacity constraint
- `max_monthly_requests` (BIGINT, REQUIRED) - Usage limitation
- `settings` (JSONB) - Organization configuration
- `member_count` (INTEGER) - Current membership count
- `storage_used` (BIGINT) - Resource consumption tracking
- `owner_id` (UUID) - Primary administrator

**Business Logic**: Resource limits enforcement, billing integration, multi-tenancy isolation

#### organization_members (Membership Management)
**Purpose**: Organization membership with role-based access control

**Key Relationships**:
- `organization_id` → organizations.id
- `user_id` → profiles.id

**Key Fields**:
- `role` (user_role_type ENUM, REQUIRED) - Permission level
- `status` (user_status ENUM) - Member state
- `permissions` (JSONB) - Custom permission overrides
- `last_active_at` (TIMESTAMP) - Activity tracking

#### organization_invitations (Invitation System)
**Purpose**: Pending organization invitations with token-based security

**Key Fields**:
- `email` (TEXT, REQUIRED) - Invitee identifier
- `role` (user_role_type ENUM, REQUIRED) - Intended permission level
- `token` (UUID, REQUIRED) - Security token
- `status` (invitation_status ENUM, REQUIRED) - Invitation state
- `expires_at` (TIMESTAMP, REQUIRED) - Security expiration

### 2. Project & Document Management

#### projects (Project Containers)
**Purpose**: Project-level organization for requirements and documentation

**Key Relationships**:
- `organization_id` → organizations.id

**Key Fields**:
- `name` (TEXT, REQUIRED) - Project identifier
- `slug` (TEXT, REQUIRED) - URL-safe identifier
- `description` (TEXT) - Project overview
- `visibility` (visibility ENUM, REQUIRED) - Access control level
- `status` (project_status ENUM, REQUIRED) - Project lifecycle state
- `settings` (JSONB) - Project configuration
- `tags` (TEXT[]) - Categorization system
- `star_count` (INTEGER) - Popularity metric
- `version` (INTEGER) - Version tracking

#### documents (Document Structure)
**Purpose**: Document containers within projects for content organization

**Key Relationships**:
- `project_id` → projects.id

**Key Fields**:
- `name` (TEXT, REQUIRED) - Document identifier
- `slug` (TEXT, REQUIRED) - URL-safe identifier
- `description` (TEXT) - Document overview
- `tags` (TEXT[]) - Categorization
- `version` (BIGINT, REQUIRED) - Version control

#### blocks (Content Blocks)
**Purpose**: Structured content blocks within documents

**Key Relationships**:
- `document_id` → documents.id
- `org_id` → organizations.id

**Key Fields**:
- `type` (TEXT, REQUIRED) - Block type classification
- `name` (TEXT, REQUIRED) - Block identifier
- `position` (INTEGER, REQUIRED) - Display ordering
- `content` (JSONB) - Block content data
- `version` (BIGINT, REQUIRED) - Version tracking

### 3. Requirements Management Core

#### requirements (Central Requirements Repository)
**Purpose**: Core requirements with rich metadata and AI enhancement capabilities

**Key Relationships**:
- `document_id` → documents.id
- `block_id` → blocks.id

**Key Fields**:
- `external_id` (TEXT) - External system integration
- `name` (TEXT, REQUIRED) - Requirement title
- `description` (TEXT) - Detailed specification
- `status` (requirement_status ENUM, REQUIRED) - Lifecycle state
- `format` (requirement_format ENUM, REQUIRED) - Format classification
- `priority` (requirement_priority ENUM, REQUIRED) - Priority level
- `level` (requirement_level ENUM, REQUIRED) - Requirement hierarchy level
- `position` (DOUBLE PRECISION, REQUIRED) - Ordering system
- `tags` (TEXT[]) - Categorization
- `original_requirement` (TEXT) - Source specification
- `enchanced_requirement` (TEXT) - AI-processed specification
- `ai_analysis` (JSONB) - AI processing results
- `properties` (JSONB) - Custom metadata
- `version` (BIGINT, REQUIRED) - Version control

**Business Logic**: AI enhancement pipeline, version tracking, flexible metadata

#### properties (Custom Property Definitions)
**Purpose**: Configurable metadata fields for requirements customization

**Key Relationships**:
- `org_id` → organizations.id
- `project_id` → projects.id
- `document_id` → documents.id

**Key Fields**:
- `name` (TEXT, REQUIRED) - Property identifier
- `property_type` (TEXT, REQUIRED) - Data type specification
- `options` (JSONB) - Configuration options
- `scope` (TEXT) - Application scope
- `is_base` (BOOLEAN) - System property indicator

#### columns (Table Column Configuration)
**Purpose**: Custom column configuration for requirements tables

**Key Relationships**:
- `block_id` → blocks.id
- `property_id` → properties.id

**Key Fields**:
- `position` (DOUBLE PRECISION, REQUIRED) - Column ordering
- `width` (INTEGER) - Display width
- `is_hidden` (BOOLEAN) - Visibility control
- `is_pinned` (BOOLEAN) - Pin status
- `default_value` (TEXT) - Default value

### 4. Testing & Quality Assurance

#### test_req (Test Requirements)
**Purpose**: Test case definitions and specifications

**Key Relationships**:
- `project_id` → projects.id

**Key Fields**:
- `test_id` (TEXT) - External test identifier
- `title` (TEXT, REQUIRED) - Test case title
- `description` (TEXT) - Detailed test specification
- `test_type` (test_type ENUM, REQUIRED) - Test classification
- `priority` (test_priority ENUM, REQUIRED) - Priority level
- `status` (test_status ENUM, REQUIRED) - Test status
- `method` (test_method ENUM, REQUIRED) - Test approach
- `result` (TEXT) - Test execution result
- `expected_results` (TEXT) - Expected outcomes
- `preconditions` (TEXT) - Setup requirements
- `test_steps` (JSONB) - Step-by-step instructions
- `estimated_duration` (INTERVAL) - Time estimation
- `category` (TEXT[]) - Test categorization
- `test_environment` (TEXT) - Environment specification
- `attachments` (JSONB) - Supporting files
- `is_active` (BOOLEAN) - Active status

#### requirement_tests (Test Execution Tracking)
**Purpose**: Links requirements to test executions with detailed results

**Key Relationships**:
- `requirement_id` → requirements.id
- `test_id` → test_req.id

**Key Fields**:
- `execution_status` (execution_status ENUM, REQUIRED) - Test result
- `result_notes` (TEXT) - Execution notes
- `executed_at` (TIMESTAMP) - Execution timestamp
- `executed_by` (UUID) - Executor identifier
- `execution_environment` (TEXT) - Test environment
- `execution_version` (TEXT) - Version tested
- `defects` (JSONB) - Identified issues
- `evidence_artifacts` (JSONB) - Supporting evidence
- `external_test_id` (TEXT) - External system reference
- `external_req_id` (TEXT) - External requirement reference

#### test_matrix_views (Test Analysis Views)
**Purpose**: Configurable test matrix views for analysis

**Key Relationships**:
- `project_id` → projects.id

**Key Fields**:
- `name` (TEXT, REQUIRED) - View identifier
- `configuration` (JSONB, REQUIRED) - View settings
- `is_active` (BOOLEAN) - Active status
- `is_default` (BOOLEAN) - Default view indicator

### 5. Collaboration & Traceability

#### assignments (Task Assignment System)
**Purpose**: Assignment tracking for requirements and other entities

**Key Fields**:
- `entity_id` (UUID, REQUIRED) - Assigned entity
- `entity_type` (entity_type ENUM, REQUIRED) - Entity classification
- `assignee_id` (UUID, REQUIRED) - Assigned user
- `role` (assignment_role ENUM, REQUIRED) - Assignment role
- `status` (requirement_status ENUM, REQUIRED) - Assignment status
- `comment` (TEXT) - Assignment notes
- `due_date` (TIMESTAMP) - Due date
- `completed_at` (TIMESTAMP) - Completion timestamp
- `version` (BIGINT, REQUIRED) - Version tracking

#### trace_links (Traceability Matrix)
**Purpose**: Relationships between entities for traceability analysis

**Key Fields**:
- `source_id` (UUID, REQUIRED) - Source entity
- `target_id` (UUID, REQUIRED) - Target entity
- `source_type` (entity_type ENUM, REQUIRED) - Source classification
- `target_type` (entity_type ENUM, REQUIRED) - Target classification
- `link_type` (trace_link_type ENUM, REQUIRED) - Relationship type
- `description` (TEXT) - Relationship description
- `version` (BIGINT, REQUIRED) - Version tracking

### 6. Diagram & Visualization

#### excalidraw_diagrams (Collaborative Diagrams)
**Purpose**: Freehand collaborative drawing diagrams

**Key Fields**:
- `name` (TEXT) - Diagram identifier
- `diagram_data` (JSONB) - Excalidraw data structure
- `thumbnail_url` (TEXT) - Preview image
- `organization_id` (UUID) - Organization context
- `project_id` (UUID) - Project context

#### diagram_element_links (Diagram Integration)
**Purpose**: Links diagram elements to requirements for visual traceability

**Key Relationships**:
- `diagram_id` → excalidraw_diagrams.id
- `requirement_id` → requirements.id

**Key Fields**:
- `element_id` (TEXT, REQUIRED) - Excalidraw element identifier
- `link_type` (VARCHAR) - Link classification
- `metadata` (JSONB) - Additional link data

#### react_flow_diagrams (Structured Flow Diagrams)
**Purpose**: Node-edge flow diagrams with structured data

**Key Relationships**:
- `project_id` → projects.id

**Key Fields**:
- `name` (VARCHAR, REQUIRED) - Diagram identifier
- `description` (TEXT) - Diagram description
- `nodes` (JSONB, REQUIRED) - Flow nodes
- `edges` (JSONB, REQUIRED) - Flow connections
- `viewport` (JSONB) - View configuration
- `diagram_type` (VARCHAR) - Diagram classification
- `layout_algorithm` (VARCHAR) - Layout method
- `theme` (VARCHAR) - Visual theme
- `settings` (JSONB) - Configuration
- `metadata` (JSONB) - Additional data

### 7. External Integration

#### external_documents (External Document Links)
**Purpose**: Integration with external document sources

**Key Fields**:
- `organization_id` (UUID, REQUIRED) - Organization context
- `name` (TEXT, REQUIRED) - Document identifier
- `url` (TEXT) - External URL
- `type` (TEXT) - Document classification
- `size` (BIGINT) - File size
- `gumloop_name` (TEXT) - Gumloop integration identifier

### 8. OAuth 2.0 Authentication System

#### oauth_clients (OAuth Client Applications)
**Purpose**: OAuth 2.0 client registration and management

**Key Fields**:
- `client_id` (VARCHAR, REQUIRED) - OAuth client identifier
- `client_name` (VARCHAR, REQUIRED) - Application name
- `client_secret` (VARCHAR) - Client authentication secret
- `redirect_uris` (JSONB, REQUIRED) - Allowed redirect URIs
- `grant_types` (JSONB, REQUIRED) - Supported grant types
- `response_types` (JSONB, REQUIRED) - Supported response types
- `scope` (TEXT) - OAuth scopes
- `is_public` (BOOLEAN) - Public client indicator

#### oauth_authorization_codes (PKCE Authorization)
**Purpose**: Authorization code storage with PKCE support

**Key Relationships**:
- `user_id` → profiles.id

**Key Fields**:
- `code` (VARCHAR, REQUIRED) - Authorization code
- `client_id` (VARCHAR, REQUIRED) - OAuth client
- `redirect_uri` (TEXT, REQUIRED) - Redirect URI
- `code_challenge` (VARCHAR, REQUIRED) - PKCE code challenge
- `code_challenge_method` (VARCHAR, REQUIRED) - PKCE method
- `scope` (TEXT) - Requested scopes
- `state` (VARCHAR) - OAuth state parameter
- `expires_at` (TIMESTAMP, REQUIRED) - Code expiration

#### oauth_access_tokens (Access Token Management)
**Purpose**: OAuth 2.0 access token lifecycle management

**Key Fields**:
- `token_hash` (VARCHAR, REQUIRED) - Token hash for security
- `client_id` (VARCHAR, REQUIRED) - Associated OAuth client
- `user_id` (UUID) - Token owner
- `scope` (TEXT) - Token permissions
- `expires_at` (TIMESTAMP, REQUIRED) - Token expiration
- `last_used_at` (TIMESTAMP) - Usage tracking

#### oauth_refresh_tokens (Refresh Token Management)
**Purpose**: OAuth 2.0 refresh token management

**Key Relationships**:
- `user_id` → profiles.id

**Key Fields**:
- `token` (VARCHAR, REQUIRED) - Refresh token
- `client_id` (VARCHAR, REQUIRED) - Associated OAuth client
- `scope` (TEXT) - Token permissions
- `expires_at` (TIMESTAMP, REQUIRED) - Token expiration
- `last_used_at` (TIMESTAMP) - Usage tracking

### 9. Billing & Usage Management

#### stripe_customers (Stripe Integration)
**Purpose**: Stripe billing integration and subscription management

**Key Relationships**:
- `organization_id` → organizations.id

**Key Fields**:
- `stripe_customer_id` (TEXT) - Stripe customer identifier
- `stripe_subscription_id` (TEXT) - Subscription identifier
- `subscription_status` (subscription_status ENUM, REQUIRED) - Subscription state
- `price_id` (TEXT) - Stripe price identifier
- `current_period_start` (TIMESTAMP) - Billing period start
- `current_period_end` (TIMESTAMP) - Billing period end
- `cancel_at_period_end` (BOOLEAN) - Cancellation flag
- `payment_method_last4` (TEXT) - Card identification
- `payment_method_brand` (TEXT) - Card brand

#### billing_cache (Performance Cache)
**Purpose**: Cached billing status for performance optimization

**Key Relationships**:
- `organization_id` → organizations.id

**Key Fields**:
- `billing_status` (JSONB, REQUIRED) - Current billing state
- `current_period_usage` (JSONB, REQUIRED) - Usage metrics
- `synced_at` (TIMESTAMP, REQUIRED) - Last synchronization
- `period_start` (TIMESTAMP, REQUIRED) - Period start
- `period_end` (TIMESTAMP, REQUIRED) - Period end

#### usage_logs (Feature Usage Tracking)
**Purpose**: Feature usage tracking for billing and analytics

**Key Relationships**:
- `organization_id` → organizations.id

**Key Fields**:
- `user_id` (UUID, REQUIRED) - User identifier
- `feature` (TEXT, REQUIRED) - Feature identifier
- `quantity` (INTEGER, REQUIRED) - Usage quantity
- `unit_type` (TEXT, REQUIRED) - Unit measurement
- `metadata` (JSONB) - Additional usage data

### 10. System Management & Compliance

#### user_roles (Role Management)
**Purpose**: Hierarchical role assignments across different scopes

**Key Relationships**:
- `project_id` → projects.id
- `org_id` → organizations.id
- `document_id` → documents.id

**Key Fields**:
- `user_id` (UUID, REQUIRED) - User identifier
- `admin_role` (user_role_type) - Administrative role
- `project_role` (project_role) - Project-level role
- `document_role` (project_role) - Document-level role

#### notifications (Notification System)
**Purpose**: In-application notification management

**Key Fields**:
- `user_id` (UUID, REQUIRED) - Notification recipient
- `type` (notification_type ENUM, REQUIRED) - Notification classification
- `title` (TEXT, REQUIRED) - Notification title
- `message` (TEXT) - Notification content
- `unread` (BOOLEAN) - Read status
- `metadata` (JSONB) - Additional notification data
- `read_at` (TIMESTAMP) - Read timestamp

#### audit_logs (Comprehensive Audit Trail)
**Purpose**: Complete system audit logging for SOC2 compliance

**Key Relationships**:
- `user_id` → profiles.id
- `organization_id` → organizations.id
- `project_id` → projects.id

**Key Fields**:
- `entity_id` (UUID, REQUIRED) - Affected entity
- `entity_type` (TEXT, REQUIRED) - Entity classification
- `action` (TEXT, REQUIRED) - Performed action
- `actor_id` (UUID) - Action performer
- `old_data` (JSONB) - Previous state
- `new_data` (JSONB) - New state
- `metadata` (JSONB) - Action metadata
- `event_type` (audit_event_type ENUM) - Event classification
- `severity` (audit_severity ENUM) - Event severity
- `session_id` (TEXT) - User session
- `ip_address` (INET) - Client IP address
- `user_agent` (TEXT) - Client user agent
- `resource_type` (resource_type ENUM) - Resource classification
- `resource_id` (UUID) - Resource identifier
- `description` (TEXT) - Human-readable description
- `details` (JSONB) - Detailed information
- `soc2_control` (TEXT) - SOC2 control mapping
- `compliance_category` (TEXT) - Compliance classification
- `risk_level` (TEXT) - Risk assessment
- `threat_indicators` (TEXT[]) - Security indicators
- `source_system` (TEXT) - Source system
- `correlation_id` (UUID) - Event correlation

### 11. Performance Views

#### document_summary (Aggregated Statistics)
**Purpose**: Pre-computed document statistics for performance

**Key Relationships**:
- `project_id` → projects.id

**Key Fields**:
- `document_id` (UUID, PK) - Document identifier
- `document_name` (TEXT) - Document name
- `block_count` (BIGINT) - Number of blocks
- `requirement_count` (BIGINT) - Number of requirements
- `updated_at` (TIMESTAMP) - Last update timestamp

## Custom Data Types (ENUMs)

### User & Organization Management
- **user_status**: Account states (active, inactive, suspended, pending, etc.)
- **user_role_type**: Organization roles (owner, admin, member, viewer, etc.)
- **organization_type**: Organization classifications
- **billing_plan**: Subscription tiers (free, pro, enterprise, etc.)
- **pricing_plan_interval**: Billing cycles (monthly, yearly, etc.)
- **invitation_status**: Invitation states (pending, accepted, expired, cancelled, etc.)

### Project Management
- **project_status**: Project states (active, archived, draft, planning, etc.)
- **project_role**: Project-specific roles (admin, editor, viewer, etc.)
- **visibility**: Access levels (public, private, organization, restricted, etc.)

### Requirements Management
- **requirement_status**: Requirement states (draft, approved, implemented, deprecated, etc.)
- **requirement_format**: Format types (natural_language, formal, structured, etc.)
- **requirement_priority**: Priority levels (low, medium, high, critical, blocker, etc.)
- **requirement_level**: Requirement levels (system, component, feature, user_story, etc.)
- **entity_type**: Entity classifications (requirement, test, document, project, etc.)
- **assignment_role**: Assignment types (assignee, reviewer, approver, observer, etc.)
- **trace_link_type**: Relationship types (derived_from, satisfies, conflicts_with, depends_on, etc.)

### Testing & Quality Assurance
- **test_type**: Test classifications (unit, integration, system, acceptance, performance, etc.)
- **test_priority**: Test priority levels (low, medium, high, critical, etc.)
- **test_status**: Test states (planned, active, passed, failed, blocked, etc.)
- **test_method**: Test approaches (manual, automated, semi_automated, etc.)
- **execution_status**: Test execution results (pass, fail, skip, blocked, etc.)

### System & Compliance
- **notification_type**: Notification classifications (info, warning, error, success, etc.)
- **audit_event_type**: Audit event categories (create, update, delete, login, etc.)
- **audit_severity**: Severity levels (low, medium, high, critical, etc.)
- **resource_type**: Resource classifications (user, organization, project, requirement, etc.)
- **subscription_status**: Stripe subscription states (active, past_due, cancelled, etc.)

## Security & Compliance Architecture

### Multi-Tenant Security
- **Row Level Security (RLS)**: Organization-based data isolation
- **Hierarchical Access Control**: Organization → Project → Document → Requirement
- **Role-Based Permissions**: Granular permission system across all entities
- **API Authentication**: OAuth 2.0 with PKCE for secure API access

### Compliance Framework
- **SOC2 Ready**: Complete audit trail with control mapping
- **Data Lineage**: Full change tracking with before/after states
- **Risk Assessment**: Threat indicator tracking and risk level classification
- **Retention Policies**: Soft delete patterns with audit preservation

### Data Protection
- **Soft Delete Pattern**: Consistent across all major entities for data recovery
- **Version Control**: Entity versioning for complete change history
- **Approval Workflows**: Structured approval processes for critical operations
- **Session Management**: Secure session tracking with IP and user agent logging

## Performance & Scalability Considerations

### Indexing Strategy
- **Primary Keys**: Automatic UUID indexing
- **Foreign Keys**: Relationship indexing for join performance
- **Composite Indexes**: Multi-column indexes for common query patterns
- **JSONB Indexes**: GIN indexes for flexible metadata queries
- **Text Search**: Full-text search capabilities across content

### Volume Projections
- **High Volume Tables**: 
  - `audit_logs`: 1M+ records (all system changes)
  - `usage_logs`: 100K+ records per month (billing tracking)
  - `requirement_tests`: 50K+ records (test executions)

- **Medium Volume Tables**:
  - `requirements`: 10K+ records (core business entities)
  - `test_req`: 5K+ records (test definitions)
  - `assignments`: 20K+ records (task management)
  - `trace_links`: 15K+ records (traceability matrix)

- **Low Volume Tables**:
  - `organizations`: 100-1K records (tenants)
  - `projects`: 1K-10K records (project containers)
  - `documents`: 5K-50K records (document structure)
  - `profiles`: 1K-100K records (user accounts)

### Caching Strategy
- **Billing Cache**: Pre-computed subscription status and usage metrics
- **Document Summary**: Aggregated statistics for dashboard performance
- **OAuth Tokens**: Session management for API performance
- **Organization Context**: Cached tenant information for multi-tenant queries

## Integration Architecture

### External System Integrations
- **Stripe**: Complete billing lifecycle with webhook processing
- **OAuth 2.0**: Standard authentication for third-party applications
- **External Documents**: File system or cloud storage integration
- **Gumloop**: Document processing and analysis integration
- **AI Services**: Requirement enhancement and analysis

### API Architecture Patterns
- **RESTful Design**: Standard HTTP methods with resource-based URLs
- **Real-time Updates**: WebSocket or Server-Sent Events for collaboration
- **Bulk Operations**: Batch processing for test execution and imports
- **Search API**: Full-text search across requirements and documents
- **Rate Limiting**: API throttling for security and performance

## Recommendations for Optimization

### Performance Enhancements
1. **Connection Pooling**: Implement connection pooling for high-concurrency access
2. **Read Replicas**: Deploy read replicas for reporting and analytics workloads
3. **Query Optimization**: Add specialized indexes for common query patterns
4. **Caching Layer**: Implement Redis for session management and frequent queries
5. **JSONB Optimization**: Create GIN indexes on frequently queried JSONB fields

### Security Improvements
1. **API Rate Limiting**: Implement rate limiting on OAuth endpoints
2. **Data Encryption**: Encrypt sensitive JSONB fields at rest
3. **Backup Strategy**: Automated backups with point-in-time recovery
4. **Monitoring**: Real-time alerting on audit log anomalies
5. **Access Reviews**: Regular access review processes for compliance

### Scalability Planning
1. **Table Partitioning**: Partition large tables (audit_logs, usage_logs) by date
2. **Data Archival**: Implement retention policies for historical data
3. **Load Balancing**: Distribute read traffic across multiple replicas
4. **Microservices**: Consider service decomposition for independent scaling
5. **CDN Integration**: Content delivery for static assets and documentation

---

**Schema Analysis Generated**: 2025-01-08  
**Database Version**: PostgreSQL (Supabase)  
**Analysis Method**: OpenAPI specification introspection with architectural assessment