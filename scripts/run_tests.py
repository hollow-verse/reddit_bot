#!/usr/bin/env python
"""Script to run all tests with verbose output."""
import unittest
import sys
import os
import logging
from importlib import import_module
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def discover_tests():
    """Discover all test files in the tests directory."""
    test_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests')))
    test_files = []
    
    for path in test_dir.glob('**/*test_*.py'):
        # Convert path to module name
        module_path = str(path.relative_to(test_dir.parent)).replace('/', '.').replace('\\', '.').replace('.py', '')
        test_files.append(module_path)
    
    return test_files

def run_test_file(module_name):
    """Run tests from a single file."""
    try:
        module = import_module(module_name)
        logger.info(f"Running tests from: {module_name}")
        
        # Find and collect test cases from the module
        test_cases = []
        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, type) and issubclass(item, unittest.TestCase) and item is not unittest.TestCase:
                test_cases.append(item)
        
        # Run the test cases
        for test_case in test_cases:
            logger.info(f"Running test case: {test_case.__name__}")
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(unittest.makeSuite(test_case))
            
            # Log test results
            if result.wasSuccessful():
                logger.info(f"✓ Test case {test_case.__name__} passed successfully")
            else:
                logger.error(f"✗ Test case {test_case.__name__} failed: {len(result.failures)} failures, {len(result.errors)} errors")
                # Print failures and errors
                for failure in result.failures:
                    logger.error(f"  Failure: {failure[0]}")
                    logger.error(f"    {failure[1]}")
                for error in result.errors:
                    logger.error(f"  Error: {error[0]}")
                    logger.error(f"    {error[1]}")
        
        return True
    except Exception as e:
        logger.error(f"Error running tests from {module_name}: {str(e)}")
        return False

def main():
    """Main function to run all tests."""
    logger.info("Starting test runner")
    
    # Discover test files
    test_files = discover_tests()
    logger.info(f"Found {len(test_files)} test files")
    
    # Run each test file
    success_count = 0
    failure_count = 0
    
    for test_file in test_files:
        if run_test_file(test_file):
            success_count += 1
        else:
            failure_count += 1
    
    # Log summary
    logger.info(f"Test run complete: {success_count} test files passed, {failure_count} test files failed")
    
    # Exit with appropriate status code
    if failure_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 