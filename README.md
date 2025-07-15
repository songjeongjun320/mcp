# Google MCP Toolbox Integration

A comprehensive integration and example project for the Google MCP Toolbox Core SDK, providing easy-to-use tools for building GenAI applications with external functionality integration.

## 🚀 Features

- **Async/Sync Support**: Both asynchronous and synchronous tool invocation
- **Authentication**: Google Cloud authentication and custom auth mechanisms
- **LangGraph Integration**: Seamless integration with LangGraph for agentic workflows
- **Parameter Binding**: Pre-bind parameters for security and consistency
- **Example Projects**: Ready-to-use examples for common use cases

## 📦 Installation

### Basic Installation
```bash
pip install -e .
```

### With Optional Dependencies
```bash
# For development
pip install -e ".[dev]"

# For LangChain integration
pip install -e ".[langchain]"

# For Google Cloud authentication
pip install -e ".[auth]"

# Install all optional dependencies
pip install -e ".[dev,langchain,auth]"
```

## 🏗️ Project Structure

```
google-mcp-toolbox/
├── src/
│   └── toolbox_integration/
│       ├── __init__.py
│       ├── client.py          # ToolboxClient wrapper
│       ├── auth.py            # Authentication utilities
│       └── utils.py           # Utility functions
├── examples/
│   ├── basic_usage.py         # Basic async/sync examples
│   ├── with_authentication.py # Authentication examples
│   ├── langraph_integration.py # LangGraph examples
│   └── parameter_binding.py   # Parameter binding examples
├── tests/
│   ├── test_client.py         # Client tests
│   ├── test_auth.py           # Authentication tests
│   └── test_integration.py    # Integration tests
├── config/
│   └── settings.py            # Configuration settings
├── requirements.txt           # Dependencies
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 🚦 Quick Start

### 1. Basic Usage

```python
import asyncio
from toolbox_integration import ToolboxClientWrapper

async def main():
    async with ToolboxClientWrapper("http://127.0.0.1:5000") as client:
        # Load and use a tool
        weather_tool = await client.load_tool("get_weather")
        result = await weather_tool(location="Seoul")
        print(f"Weather in Seoul: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Synchronous Usage

```python
from toolbox_integration import ToolboxSyncClientWrapper

with ToolboxSyncClientWrapper("http://127.0.0.1:5000") as client:
    weather_tool = client.load_tool("get_weather")
    result = weather_tool(location="Busan")
    print(f"Weather in Busan: {result}")
```

### 3. With Authentication

```python
from toolbox_integration import ToolboxClientWrapper
from toolbox_integration.auth import get_google_id_token

async def main():
    async with ToolboxClientWrapper(
        "https://your-toolbox-service.run.app",
        client_headers={"Authorization": get_google_id_token}
    ) as client:
        tools = await client.load_toolset()
        # Use authenticated tools...

asyncio.run(main())
```

## 📚 Examples

All examples are available in the `examples/` directory:

- **`basic_usage.py`**: Basic async and sync usage patterns
- **`with_authentication.py`**: Google Cloud authentication setup
- **`langraph_integration.py`**: Integration with LangGraph for agentic workflows
- **`parameter_binding.py`**: Binding parameters for security and consistency

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run async tests only
pytest -k "async"
```

## 🔧 Configuration

Configuration is managed through the `config/settings.py` file:

```python
# Default toolbox service URL
DEFAULT_TOOLBOX_URL = "http://127.0.0.1:5000"

# Authentication settings
GOOGLE_CLOUD_PROJECT = "your-project-id"
GOOGLE_CLOUD_REGION = "us-central1"

# Logging configuration
LOG_LEVEL = "INFO"
```

## 🔐 Authentication

### Google Cloud Authentication

For Google Cloud services, ensure you have proper authentication set up:

```bash
# Install Google Cloud SDK
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Custom Authentication

Implement custom authentication by extending the auth module:

```python
from toolbox_integration.auth import AuthProvider

class CustomAuthProvider(AuthProvider):
    async def get_token(self) -> str:
        # Your custom token retrieval logic
        return "your-custom-token"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/google-mcp-toolbox.git
cd google-mcp-toolbox

# Install in development mode
pip install -e ".[dev]"

# Run linting and formatting
black src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/

# Run tests
pytest
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [MCP Toolbox Documentation](https://github.com/toolbox-project/toolbox)
- **Issues**: [GitHub Issues](https://github.com/your-username/google-mcp-toolbox/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/google-mcp-toolbox/discussions)

## 🗺️ Roadmap

- [ ] Add more authentication providers
- [ ] Implement tool caching mechanisms
- [ ] Add monitoring and logging features
- [ ] Create more comprehensive examples
- [ ] Add Docker support
- [ ] Implement tool versioning support 