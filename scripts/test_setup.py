#!/usr/bin/env python3
"""
Test setup script for Google MCP Toolbox integration project.

This script validates the project structure, runs basic tests, and provides
a development environment check.
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_python_version() -> bool:
    """Check if Python version is supported."""
    logger.info("Checking Python version...")
    
    if sys.version_info < (3, 8):
        logger.error(f"Python 3.8+ required, got {sys.version_info}")
        return False
    
    logger.info(f"✓ Python version: {sys.version}")
    return True


def check_project_structure() -> bool:
    """Check if project structure is correct."""
    logger.info("Checking project structure...")
    
    project_root = Path(__file__).parent.parent
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "src/toolbox_integration/__init__.py",
        "src/toolbox_integration/client.py",
        "src/toolbox_integration/auth.py",
        "src/toolbox_integration/utils.py",
        "config/settings.py",
        "examples/basic_usage.py",
        "examples/with_authentication.py",
        "tests/test_client.py",
        "tests/test_auth.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            logger.info(f"✓ {file_path}")
    
    if missing_files:
        logger.error(f"Missing files: {missing_files}")
        return False
    
    logger.info("✓ Project structure is correct")
    return True


def check_imports() -> bool:
    """Check if all imports work correctly."""
    logger.info("Checking imports...")
    
    try:
        # Test basic imports
        import toolbox_integration
        logger.info("✓ Main package import successful")
        
        from toolbox_integration import ToolboxClientWrapper, ToolboxSyncClientWrapper
        logger.info("✓ Client wrapper imports successful")
        
        from toolbox_integration.auth import (
            StaticTokenProvider, 
            EnvironmentTokenProvider,
            CustomTokenProvider,
            create_auth_provider
        )
        logger.info("✓ Auth provider imports successful")
        
        from toolbox_integration.utils import ToolboxConfig, setup_logging
        logger.info("✓ Utils imports successful")
        
        # Test configuration imports
        from config.settings import get_config_summary, validate_config
        logger.info("✓ Configuration imports successful")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Import error: {e}")
        return False


def run_basic_tests() -> bool:
    """Run basic functionality tests."""
    logger.info("Running basic functionality tests...")
    
    try:
        from toolbox_integration import ToolboxClientWrapper
        from toolbox_integration.auth import StaticTokenProvider
        from toolbox_integration.utils import ToolboxConfig
        
        # Test configuration creation
        config = ToolboxConfig(
            default_url="http://test.example.com",
            timeout=10,
            log_level="DEBUG"
        )
        logger.info("✓ Configuration creation successful")
        
        # Test auth provider creation
        auth_provider = StaticTokenProvider("test-token")
        logger.info("✓ Auth provider creation successful")
        
        # Test client wrapper creation (without connection)
        client_wrapper = ToolboxClientWrapper(
            "http://test.example.com",
            auth_provider=auth_provider,
            config=config
        )
        logger.info("✓ Client wrapper creation successful")
        
        # Test token validation
        from toolbox_integration.auth import validate_token_format
        assert validate_token_format("Bearer test-token") is True
        logger.info("✓ Token validation successful")
        
        # Test config validation
        from config.settings import validate_config
        errors = validate_config()
        if errors:
            logger.warning(f"Config validation issues: {errors}")
        else:
            logger.info("✓ Configuration validation successful")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Basic test failed: {e}")
        return False


def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    logger.info("Checking dependencies...")
    
    required_packages = [
        "aiohttp",
        "pytest",
        "pytest-asyncio",
    ]
    
    optional_packages = [
        "google-auth",
        "langchain",
        "langgraph",
        "yaml",
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            logger.info(f"✓ {package} available")
        except ImportError:
            missing_required.append(package)
            logger.error(f"✗ {package} not available")
    
    for package in optional_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            logger.info(f"✓ {package} available (optional)")
        except ImportError:
            missing_optional.append(package)
            logger.warning(f"⚠ {package} not available (optional)")
    
    if missing_required:
        logger.error(f"Missing required packages: {missing_required}")
        logger.info("Install with: pip install -e .")
        return False
    
    if missing_optional:
        logger.info(f"Missing optional packages: {missing_optional}")
        logger.info("Install with: pip install -e '.[dev,auth,langchain]'")
    
    return True


def run_pytest_tests() -> bool:
    """Run pytest tests if available."""
    logger.info("Running pytest tests...")
    
    try:
        import pytest
    except ImportError:
        logger.warning("pytest not available, skipping unit tests")
        return True
    
    try:
        # Change to project root
        project_root = Path(__file__).parent.parent
        os.chdir(project_root)
        
        # Run tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ All tests passed")
            return True
        else:
            logger.error(f"✗ Tests failed with return code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Failed to run tests: {e}")
        return False


def run_example_validation() -> bool:
    """Validate example files syntax."""
    logger.info("Validating example files...")
    
    project_root = Path(__file__).parent.parent
    example_files = [
        "examples/basic_usage.py",
        "examples/with_authentication.py",
    ]
    
    for example_file in example_files:
        example_path = project_root / example_file
        
        try:
            # Check syntax by compiling
            with open(example_path, 'r') as f:
                code = f.read()
            
            compile(code, example_path, 'exec')
            logger.info(f"✓ {example_file} syntax valid")
            
        except SyntaxError as e:
            logger.error(f"✗ {example_file} syntax error: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ {example_file} validation error: {e}")
            return False
    
    return True


def generate_setup_report() -> Dict[str, Any]:
    """Generate a comprehensive setup report."""
    logger.info("Generating setup report...")
    
    report = {
        "python_version": check_python_version(),
        "project_structure": check_project_structure(),
        "imports": check_imports(),
        "dependencies": check_dependencies(),
        "basic_tests": run_basic_tests(),
        "example_validation": run_example_validation(),
        "pytest_tests": run_pytest_tests(),
    }
    
    return report


def print_setup_summary(report: Dict[str, Any]) -> None:
    """Print a summary of the setup validation."""
    print("\n" + "="*60)
    print("GOOGLE MCP TOOLBOX SETUP VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in report.values() if result)
    total = len(report)
    
    print(f"Overall Status: {passed}/{total} checks passed")
    print()
    
    for check, result in report.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check.replace('_', ' ').title():.<40} {status}")
    
    if passed == total:
        print("\n🎉 All checks passed! Your project is ready for development.")
        print("\nNext steps:")
        print("1. Start a toolbox service: (follow MCP Toolbox documentation)")
        print("2. Run examples: python examples/basic_usage.py")
        print("3. Start developing your integration!")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -e '.[dev,auth,langchain]'")
        print("2. Check Python version (3.8+ required)")
        print("3. Verify project structure is complete")
    
    print("="*60)


def main():
    """Main function to run all setup validation checks."""
    logger.info("Starting Google MCP Toolbox setup validation...")
    
    report = generate_setup_report()
    print_setup_summary(report)
    
    # Exit with appropriate code
    if all(report.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main() 