# src/session5/integration_testing.py
"""
Comprehensive testing framework for PydanticAI agents including unit tests,
integration tests, mocking, and test data generation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic, Type, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import time
import uuid
import random
import string
import pytest
from unittest.mock import Mock, AsyncMock, patch
import functools
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestType(str, Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SMOKE = "smoke"

class AssertionType(str, Enum):
    """Types of assertions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"
    IS_NONE = "is_none"
    IS_NOT_NONE = "is_not_none"

# Test result models

class TestResult(BaseModel):
    """Result of a test execution."""
    test_id: str = Field(..., description="Unique test identifier")
    test_name: str = Field(..., description="Test name")
    test_type: TestType = Field(..., description="Type of test")
    status: TestStatus = Field(..., description="Test status")
    duration_ms: float = Field(..., description="Test duration in milliseconds")
    message: Optional[str] = Field(None, description="Status message")
    error_details: Optional[str] = Field(None, description="Error details if failed")
    assertions_passed: int = Field(default=0, description="Number of passed assertions")
    assertions_failed: int = Field(default=0, description="Number of failed assertions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now)

class TestSuite(BaseModel):
    """A collection of related tests."""
    suite_name: str = Field(..., description="Test suite name")
    tests: List[TestResult] = Field(default_factory=list, description="Test results")
    setup_duration_ms: float = Field(default=0, description="Setup duration")
    teardown_duration_ms: float = Field(default=0, description="Teardown duration")
    created_at: datetime = Field(default_factory=datetime.now)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test suite summary."""
        status_counts = defaultdict(int)
        total_duration = 0
        total_assertions_passed = 0
        total_assertions_failed = 0
        
        for test in self.tests:
            status_counts[test.status.value] += 1
            total_duration += test.duration_ms
            total_assertions_passed += test.assertions_passed
            total_assertions_failed += test.assertions_failed
        
        return {
            "suite_name": self.suite_name,
            "total_tests": len(self.tests),
            "status_counts": dict(status_counts),
            "total_duration_ms": total_duration + self.setup_duration_ms + self.teardown_duration_ms,
            "total_assertions_passed": total_assertions_passed,
            "total_assertions_failed": total_assertions_failed,
            "success_rate": status_counts["passed"] / len(self.tests) if self.tests else 0
        }

# Test data generation

class TestDataGenerator:
    """Generates realistic test data for various scenarios."""
    
    @staticmethod
    def generate_string(length: int = 10, chars: str = string.ascii_letters + string.digits) -> str:
        """Generate random string."""
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_email() -> str:
        """Generate random email."""
        username = TestDataGenerator.generate_string(8)
        domain = random.choice(['example.com', 'test.org', 'demo.net'])
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_phone() -> str:
        """Generate random phone number."""
        return f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    @staticmethod
    def generate_date(start_date: datetime = None, end_date: datetime = None) -> datetime:
        """Generate random date between start and end."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        return start_date + timedelta(days=random_days)
    
    @staticmethod
    def generate_user_profile() -> Dict[str, Any]:
        """Generate realistic user profile data."""
        return {
            "user_id": str(uuid.uuid4()),
            "username": TestDataGenerator.generate_string(12),
            "email": TestDataGenerator.generate_email(),
            "phone": TestDataGenerator.generate_phone(),
            "first_name": random.choice(['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana']),
            "last_name": random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']),
            "age": random.randint(18, 80),
            "created_at": TestDataGenerator.generate_date(),
            "is_active": random.choice([True, False]),
            "preferences": {
                "theme": random.choice(['light', 'dark']),
                "notifications": random.choice([True, False]),
                "language": random.choice(['en', 'es', 'fr', 'de'])
            }
        }
    
    @staticmethod
    def generate_test_data(data_type: str, count: int = 1) -> Union[Any, List[Any]]:
        """Generate test data of specified type."""
        generators = {
            "string": lambda: TestDataGenerator.generate_string(),
            "email": TestDataGenerator.generate_email,
            "phone": TestDataGenerator.generate_phone,
            "date": TestDataGenerator.generate_date,
            "user_profile": TestDataGenerator.generate_user_profile,
            "integer": lambda: random.randint(1, 1000),
            "float": lambda: round(random.uniform(0, 1000), 2),
            "boolean": lambda: random.choice([True, False]),
            "uuid": lambda: str(uuid.uuid4())
        }
        
        generator = generators.get(data_type, lambda: None)
        
        if count == 1:
            return generator()
        else:
            return [generator() for _ in range(count)]

# Assertion framework

class AssertionError(Exception):
    """Custom assertion error."""
    pass

class TestAssertions:
    """Comprehensive assertion framework."""
    
    def __init__(self):
        self.passed_assertions = 0
        self.failed_assertions = 0
    
    def assert_equals(self, actual: Any, expected: Any, message: str = None):
        """Assert that two values are equal."""
        if actual == expected:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected {expected}, but got {actual}"
            raise AssertionError(msg)
    
    def assert_not_equals(self, actual: Any, expected: Any, message: str = None):
        """Assert that two values are not equal."""
        if actual != expected:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected {actual} to not equal {expected}"
            raise AssertionError(msg)
    
    def assert_contains(self, container: Any, item: Any, message: str = None):
        """Assert that container contains item."""
        if item in container:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected {container} to contain {item}"
            raise AssertionError(msg)
    
    def assert_greater_than(self, actual: float, threshold: float, message: str = None):
        """Assert that actual is greater than threshold."""
        if actual > threshold:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected {actual} to be greater than {threshold}"
            raise AssertionError(msg)
    
    def assert_less_than(self, actual: float, threshold: float, message: str = None):
        """Assert that actual is less than threshold."""
        if actual < threshold:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected {actual} to be less than {threshold}"
            raise AssertionError(msg)
    
    def assert_true(self, condition: bool, message: str = None):
        """Assert that condition is true."""
        if condition:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected condition to be True"
            raise AssertionError(msg)
    
    def assert_false(self, condition: bool, message: str = None):
        """Assert that condition is false."""
        if not condition:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected condition to be False"
            raise AssertionError(msg)
    
    def assert_none(self, value: Any, message: str = None):
        """Assert that value is None."""
        if value is None:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected None, but got {value}"
            raise AssertionError(msg)
    
    def assert_not_none(self, value: Any, message: str = None):
        """Assert that value is not None."""
        if value is not None:
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected value to not be None"
            raise AssertionError(msg)
    
    def assert_type(self, value: Any, expected_type: Type, message: str = None):
        """Assert that value is of expected type."""
        if isinstance(value, expected_type):
            self.passed_assertions += 1
        else:
            self.failed_assertions += 1
            msg = message or f"Expected {expected_type}, but got {type(value)}"
            raise AssertionError(msg)
    
    def assert_raises(self, exception_type: Type[Exception], func: Callable, *args, **kwargs):
        """Assert that function raises specific exception."""
        try:
            func(*args, **kwargs)
            self.failed_assertions += 1
            raise AssertionError(f"Expected {exception_type} to be raised")
        except exception_type:
            self.passed_assertions += 1
        except Exception as e:
            self.failed_assertions += 1
            raise AssertionError(f"Expected {exception_type}, but got {type(e)}")

# Mock utilities

class MockGenerator:
    """Utilities for creating mocks and stubs."""
    
    @staticmethod
    def create_async_mock(return_value: Any = None, side_effect: Any = None) -> AsyncMock:
        """Create async mock with specified behavior."""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock
    
    @staticmethod
    def create_sync_mock(return_value: Any = None, side_effect: Any = None) -> Mock:
        """Create sync mock with specified behavior."""
        mock = Mock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock
    
    @staticmethod
    def create_service_mock(service_responses: Dict[str, Any]) -> Mock:
        """Create mock for service with predefined responses."""
        mock = Mock()
        for method_name, response in service_responses.items():
            if asyncio.iscoroutinefunction(response) or isinstance(response, AsyncMock):
                setattr(mock, method_name, MockGenerator.create_async_mock(return_value=response))
            else:
                setattr(mock, method_name, MockGenerator.create_sync_mock(return_value=response))
        return mock

# Test runner

class TestRunner:
    """Executes tests and manages test lifecycle."""
    
    def __init__(self):
        self.test_suites: List[TestSuite] = []
        self.logger = logging.getLogger(__name__ + ".TestRunner")
    
    async def run_test_function(self, test_func: Callable, test_name: str, 
                              test_type: TestType = TestType.UNIT) -> TestResult:
        """Run a single test function."""
        test_id = str(uuid.uuid4())
        start_time = time.time()
        assertions = TestAssertions()
        
        try:
            # Execute test function
            if asyncio.iscoroutinefunction(test_func):
                await test_func(assertions)
            else:
                test_func(assertions)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if assertions.failed_assertions == 0:
                status = TestStatus.PASSED
                message = "All assertions passed"
            else:
                status = TestStatus.FAILED
                message = f"{assertions.failed_assertions} assertion(s) failed"
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=test_type,
                status=status,
                duration_ms=duration_ms,
                message=message,
                assertions_passed=assertions.passed_assertions,
                assertions_failed=assertions.failed_assertions
            )
        
        except AssertionError as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=test_type,
                status=TestStatus.FAILED,
                duration_ms=duration_ms,
                message="Assertion failed",
                error_details=str(e),
                assertions_passed=assertions.passed_assertions,
                assertions_failed=assertions.failed_assertions + 1
            )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=test_type,
                status=TestStatus.ERROR,
                duration_ms=duration_ms,
                message="Test error",
                error_details=str(e),
                assertions_passed=assertions.passed_assertions,
                assertions_failed=assertions.failed_assertions
            )
    
    async def run_test_suite(self, suite_name: str, test_functions: List[Tuple[Callable, str]], 
                           setup_func: Optional[Callable] = None,
                           teardown_func: Optional[Callable] = None) -> TestSuite:
        """Run a test suite with setup and teardown."""
        suite = TestSuite(suite_name=suite_name)
        
        # Run setup
        setup_start = time.time()
        try:
            if setup_func:
                if asyncio.iscoroutinefunction(setup_func):
                    await setup_func()
                else:
                    setup_func()
        except Exception as e:
            self.logger.error(f"Setup failed for suite {suite_name}: {str(e)}")
        
        suite.setup_duration_ms = (time.time() - setup_start) * 1000
        
        # Run tests
        for test_func, test_name in test_functions:
            try:
                result = await self.run_test_function(test_func, test_name)
                suite.tests.append(result)
                
                status_symbol = "✓" if result.status == TestStatus.PASSED else "✗"
                self.logger.info(f"{status_symbol} {test_name} ({result.duration_ms:.1f}ms)")
                
            except Exception as e:
                self.logger.error(f"Failed to run test {test_name}: {str(e)}")
        
        # Run teardown
        teardown_start = time.time()
        try:
            if teardown_func:
                if asyncio.iscoroutinefunction(teardown_func):
                    await teardown_func()
                else:
                    teardown_func()
        except Exception as e:
            self.logger.error(f"Teardown failed for suite {suite_name}: {str(e)}")
        
        suite.teardown_duration_ms = (time.time() - teardown_start) * 1000
        
        self.test_suites.append(suite)
        return suite
    
    def get_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = sum(len(suite.tests) for suite in self.test_suites)
        total_passed = sum(
            len([t for t in suite.tests if t.status == TestStatus.PASSED])
            for suite in self.test_suites
        )
        total_failed = sum(
            len([t for t in suite.tests if t.status == TestStatus.FAILED])
            for suite in self.test_suites
        )
        total_errors = sum(
            len([t for t in suite.tests if t.status == TestStatus.ERROR])
            for suite in self.test_suites
        )
        
        return {
            "total_suites": len(self.test_suites),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "success_rate": total_passed / total_tests if total_tests > 0 else 0,
            "suites": [suite.get_summary() for suite in self.test_suites]
        }

# Example test implementations

class ExampleUserModel(BaseModel):
    """Example user model for testing."""
    user_id: str = Field(..., description="User identifier")
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=13, le=120)

def demo_integration_testing():
    """Demonstrate integration testing framework."""
    print("\n=== Integration Testing Framework Demo ===")
    
    async def run_demo():
        runner = TestRunner()
        
        # Example test functions
        async def test_user_validation_success(assertions: TestAssertions):
            """Test successful user validation."""
            user_data = TestDataGenerator.generate_user_profile()
            user = ExampleUserModel(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=user_data["email"],
                age=user_data["age"]
            )
            
            assertions.assert_not_none(user.user_id, "User ID should not be None")
            assertions.assert_type(user.username, str, "Username should be string")
            assertions.assert_contains(user.email, "@", "Email should contain @")
            assertions.assert_greater_than(user.age, 0, "Age should be positive")
        
        def test_user_validation_failure(assertions: TestAssertions):
            """Test user validation failure."""
            try:
                # Invalid email
                user = ExampleUserModel(
                    user_id="test-123",
                    username="testuser",
                    email="invalid-email",
                    age=25
                )
                assertions.assert_true(False, "Should have raised validation error")
            except Exception as e:
                assertions.assert_contains(str(e), "email", "Error should mention email")
        
        async def test_performance_constraint(assertions: TestAssertions):
            """Test performance constraint."""
            start_time = time.time()
            
            # Simulate some work
            await asyncio.sleep(0.01)
            
            duration = time.time() - start_time
            assertions.assert_less_than(duration, 0.1, "Operation should complete within 100ms")
        
        def test_data_generation(assertions: TestAssertions):
            """Test data generation utilities."""
            email = TestDataGenerator.generate_email()
            assertions.assert_contains(email, "@", "Generated email should contain @")
            
            users = TestDataGenerator.generate_test_data("user_profile", count=5)
            assertions.assert_equals(len(users), 5, "Should generate 5 users")
            
            for user in users:
                assertions.assert_not_none(user["user_id"], "User ID should not be None")
        
        # Mock example
        def test_with_mocking(assertions: TestAssertions):
            """Test using mocks."""
            # Create mock service
            mock_service = MockGenerator.create_service_mock({
                "get_user": {"user_id": "123", "username": "testuser"},
                "save_user": True
            })
            
            # Test with mock
            user_data = mock_service.get_user("123")
            assertions.assert_equals(user_data["username"], "testuser")
            
            result = mock_service.save_user(user_data)
            assertions.assert_true(result, "Save should succeed")
        
        # Setup and teardown functions
        test_data = {}
        
        def setup():
            test_data["initialized"] = True
            print("Test suite setup completed")
        
        def teardown():
            test_data.clear()
            print("Test suite teardown completed")
        
        # Run test suite
        test_functions = [
            (test_user_validation_success, "test_user_validation_success"),
            (test_user_validation_failure, "test_user_validation_failure"),
            (test_performance_constraint, "test_performance_constraint"),
            (test_data_generation, "test_data_generation"),
            (test_with_mocking, "test_with_mocking")
        ]
        
        suite = await runner.run_test_suite(
            "Example Test Suite",
            test_functions,
            setup_func=setup,
            teardown_func=teardown
        )
        
        # Show results
        print(f"\nTest Suite: {suite.suite_name}")
        summary = suite.get_summary()
        print(json.dumps(summary, indent=2))
        
        # Overall report
        print("\nOverall Test Report:")
        report = runner.get_test_report()
        print(json.dumps(report, indent=2))
    
    # Run the async demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    demo_integration_testing()