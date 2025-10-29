"""
Installation and Setup Verification Script
Run this to verify all dependencies are installed correctly
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """
    Test if a module can be imported
    
    Args:
        module_name: Name of the module to import
        package_name: Display name (if different from module_name)
    """
    package_name = package_name or module_name
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name:<30} installed")
        return True
    except ImportError:
        print(f"✗ {package_name:<30} NOT installed")
        return False


def test_python_version():
    """
    Check Python version
    """
    version = sys.version_info
    print(f"\nPython Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("✓ Python version is compatible (3.7+)")
        return True
    else:
        print("✗ Python version is too old. Please use Python 3.7 or higher")
        return False


def test_project_modules():
    """
    Check if project modules can be imported
    """
    modules = [
        'config',
        'crawler',
        'pagerank',
        'indexer',
        'ranker',
        'evaluator',
        'web_interface',
    ]
    
    print("\nProject Modules:")
    all_ok = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}.py found and importable")
        except ImportError as e:
            print(f"✗ {module}.py has import errors: {e}")
            all_ok = False
        except Exception as e:
            print(f"⚠ {module}.py has issues: {e}")
            all_ok = False
    
    return all_ok


def test_directories():
    """
    Check if required directories exist
    """
    import os
    
    directories = ['data', 'index', 'results']
    
    print("\nRequired Directories:")
    all_ok = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"✓ {directory}/ exists")
        else:
            print(f"⚠ {directory}/ does not exist (will be created on first run)")
    
    return True


def main():
    """
    Run all tests
    """
    print("="*80)
    print("PageRank Search Engine - Installation Verification")
    print("="*80)
    
    # Test Python version
    python_ok = test_python_version()
    
    # Test required packages
    print("\nRequired Packages:")
    packages = [
        ('wikipediaapi', 'wikipedia-api'),
        ('numpy', 'numpy'),
        ('flask', 'Flask'),
    ]
    
    packages_ok = all(test_import(module, name) for module, name in packages)
    
    # Test optional packages
    print("\nOptional Packages:")
    optional = [
        ('pytest', 'pytest (for testing)'),
        ('black', 'black (for code formatting)'),
    ]
    
    for module, name in optional:
        test_import(module, name)
    
    # Test project modules
    modules_ok = test_project_modules()
    
    # Test directories
    dirs_ok = test_directories()
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    if python_ok and packages_ok and modules_ok:
        print("✓ All required components are installed and working!")
        print("\nYou can now run the pipeline:")
        print("  $ python run_pipeline.py")
        print("\nOr run individual components:")
        print("  $ python crawler.py")
        print("  $ python pagerank.py")
        print("  $ python indexer.py")
        print("  $ python ranker.py")
        print("  $ python web_interface.py")
    else:
        print("✗ Some components are missing or have errors")
        print("\nTo fix missing packages, run:")
        print("  $ pip install -r requirements.txt")
        
        if not modules_ok:
            print("\nSome project modules have errors. Please check:")
            print("  - All .py files are in the same directory")
            print("  - No syntax errors in the code")
    
    print("="*80)


if __name__ == "__main__":
    main()