# MCP CodeGen

MCP CodeGen is a powerful code generation tool designed to create Model Context Protocol (MCP) server implementations from YAML specifications. This tool automates the process of creating structured MCP tools and server code, making it easier to maintain and scale MCP-based applications.

## Overview

MCP CodeGen takes a YAML configuration file (`mcp_cfg.yaml`) that defines MCP tools and their specifications, and generates:

- Individual tool implementation files
- MCP server configuration
- Required project structure
- Complete documentation and type hints

## Features

- **Automated Code Generation**: Generate complete MCP tool implementations from YAML specifications
- **Type Safety**: Full type hints and validation for all tool parameters
- **Documentation**: Auto-generated docstrings and parameter documentation
- **Flexible Transport Modes**: Support for SSE, stdio, and streamable-http transport modes
- **Scalable Architecture**: Easy to add new tools and maintain existing ones

## Project Structure

```
project_root/
├── tools/                  # Directory containing tool implementations
│   ├── __init__.py
│   ├── pull_projects_tool.py
│   ├── pull_documents_tool.py
│   ├── pull_members_tool.py
│   ├── mail_to_tool.py
│   ├── calculate_sum_tool.py
│   └── calculate_bmi_tool.py
├── mcp_server.py          # MCP server configuration
├── requirements.txt       # Project dependencies
├── mcp_cfg.yaml          # Tool configuration file
└── README.md             # This file
```

## YAML Specification Format

The YAML configuration follows this structure:

```yaml
mcp_server:
  mcp_transport_mode: "sse"  # Can be stdio, sse, or streamable-http
  mcp_tools:
    - tool_name: <tool_name>
      tool_description: <tool_description>
      tool_args:
        - arg_variable: <argument_variable_name>
          arg_type: <data_type>
          arg_description: <argument_description>
```

## Current Tools

This project includes the following MCP tools:

### 1. pull_projects
Retrieves project information and data from repositories.

**Parameters:**
- `project_id` (string): Unique identifier of the project to pull
- `include_files` (boolean): Whether to include project file listings
- `branch` (string): Branch name to pull from (default: main)

### 2. pull_documents
Pulls and retrieves document contents from various sources.

**Parameters:**
- `document_path` (string): Path or URL to the document to retrieve
- `format` (string): Expected document format (pdf, docx, txt, etc.)
- `extract_metadata` (boolean): Whether to extract document metadata

### 3. pull_members
Retrieves member information from projects or organizations.

**Parameters:**
- `entity_id` (string): ID of the project or organization to get members from
- `entity_type` (string): Type of entity (project or organization)
- `include_roles` (boolean): Whether to include member roles and permissions
- `include_details` (boolean): Whether to include detailed member information

### 4. mail_to
Sends email messages to specified recipients.

**Parameters:**
- `recipient` (string): Email address of the recipient
- `subject` (string): Subject line of the email
- `body` (string): Email message body content
- `attachment_path` (string): Optional path to file attachment

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the MCP Server

1. Start the MCP server:
```bash
python mcp_server.py
```

2. The server will be available on the configured transport mode (SSE by default).

### Adding New Tools

1. Edit `mcp_cfg.yaml` to add your new tool specification
2. Run the code generator to create the tool implementation:
```bash
mcp-proj-build
```
3. Implement the tool logic in the generated file
4. Restart the MCP server

### Example Tool Implementation

Generated tool files follow this pattern:

```python
def pull_projects(project_id: str, include_files: bool, branch: str) -> Any:
    """
    Pull project information and data from repositories

    Parameters
    ----------
    project_id (str): Unique identifier of the project to pull
    include_files (bool): Whether to include project file listings
    branch (str): Branch name to pull from (default: main)

    Returns
    -------
    Any
        Result of the tool.
    """
    # TODO: implement tool logic
    raise NotImplementedError  # Replace with your custom logic
```

## Configuration

### Transport Modes

The MCP server supports three transport modes:

- **SSE** (Server-Sent Events): Real-time communication with event streaming
- **stdio**: Standard input/output communication
- **streamable-http**: HTTP-based streaming communication

Configure the transport mode in `mcp_cfg.yaml`:

```yaml
mcp_server:
  mcp_transport_mode: "sse"  # Change to your preferred mode
```

### Tool Arguments

Supported argument types:

- `string`: Text values
- `number`: Numeric values (int/float)
- `boolean`: True/false values
- `array`: List of values
- `object`: Complex data structures

## Development

### Adding Custom Logic

1. Open the generated tool file in `tools/`
2. Replace the `raise NotImplementedError` with your custom implementation
3. Add proper error handling and validation
4. Test your implementation

### Testing

Run tests to ensure your tools work correctly:

```bash
python -m pytest tests/
```

## Requirements

- Python 3.9+
- pyyaml
- MCP (Model Context Protocol)
- Additional dependencies listed in `requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tool specifications to `mcp_cfg.yaml`
4. Generate the tool implementation
5. Implement the tool logic
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the existing issues
2. Create a new issue with detailed information
3. Include your `mcp_cfg.yaml` configuration if relevant

## Changelog

### Version 1.0.0
- Initial release with core MCP tools
- Support for SSE transport mode
- Automated code generation from YAML specifications
- Six pre-configured tools: pull_projects, pull_documents, pull_members, mail_to, calculate_sum, calculate_bmi