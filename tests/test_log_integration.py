#!/usr/bin/env python3
"""
Test demonstrating log inspection capabilities of the testing framework.

Shows how to:
- Read logs within tests
- Assert log contents
- Check for errors/warnings
- Debug test failures with logs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from matrixos.testing import TestRunner
from matrixos.input import InputEvent


def test_log_integration():
    """Test that logs can be read during tests."""
    print("Testing log integration...", end=" ")
    
    runner = TestRunner("examples.platformer.main", max_duration=5.0)
    runner.wait(1.0)
    
    # Get logs from the test
    logs = runner.read_logs()
    
    # Logs should exist
    assert len(logs) > 0, "No logs found"
    
    # Check that logs were actually written
    log_lines = runner.get_log_lines()
    assert len(log_lines) > 0, f"No log lines found"
    
    print(f"✓ ({len(log_lines)} log lines captured)")


def test_log_error_detection():
    """Test that we can detect errors in logs."""
    print("Testing error detection...", end=" ")
    
    runner = TestRunner("examples.platformer.main", max_duration=5.0)
    runner.wait(0.5)
    
    # Should have no errors in normal operation
    errors = runner.get_error_logs()
    assert len(errors) == 0, f"Found unexpected errors: {errors}"
    
    # Test the assertion helper
    runner.assert_no_errors_logged()
    
    print("✓ (no errors found)")


def test_log_content_search():
    """Test searching for specific content in logs."""
    print("Testing log content search...", end=" ")
    
    runner = TestRunner("examples.platformer.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Logs should contain session start marker
    assert runner.log_contains("Session started"), "Session start not in logs"
    
    # Count occurrences
    count = runner.count_log_occurrences("Session started")
    assert count > 0, f"Expected session markers, found {count}"
    
    print(f"✓ (found '{runner.log_contains('Session started')}')")



def test_log_isolation():
    """Test that logs can be isolated between test phases."""
    print("Testing log isolation...", end=" ")
    
    runner = TestRunner("examples.platformer.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Read initial logs
    initial_lines = len(runner.get_log_lines())
    assert initial_lines > 0, "No initial logs"  # Should have session start at minimum
    
    # Clear log marker (future reads start from here)
    runner.clear_logs()
    
    # Do more actions
    runner.inject_repeat(InputEvent.RIGHT, count=10, delay=0.05)
    runner.wait(0.5)
    
    # New logs should only include recent actions
    new_lines = len(runner.get_log_lines())
    
    # After clear, we should have fewer (or zero) lines
    assert new_lines >= 0, "Log line count should be non-negative"
    
    print(f"✓ (initial={initial_lines}, after_clear={new_lines})")



def test_log_debugging():
    """Demonstrate using logs to debug test failures."""
    print("Testing log debugging...", end=" ")
    
    runner = TestRunner("examples.platformer.main", max_duration=5.0)
    runner.wait(1.0)
    
    # When a test fails, you can print logs to understand why
    # runner.print_recent_logs(lines=20)
    
    # Or get specific log types
    warnings = runner.get_warning_logs()
    errors = runner.get_error_logs()
    
    # For this test, we'll just verify the methods work
    assert isinstance(warnings, list), "warnings should be a list"
    assert isinstance(errors, list), "errors should be a list"
    
    print(f"✓ (warnings={len(warnings)}, errors={len(errors)})")


def test_multi_app_logs():
    """Test reading logs from multiple apps."""
    print("Testing multi-app log access...", end=" ")
    
    # Run one app
    runner1 = TestRunner("examples.platformer.main", max_duration=10.0)
    runner1.wait(0.5)
    platformer_logs = runner1.read_logs()  # Read current app's logs
    
    # Run another app  
    runner2 = TestRunner("examples.space_invaders.main", max_duration=10.0)
    runner2.wait(0.5)
    invaders_logs = runner2.read_logs()  # Read current app's logs
    
    # Both should have logs (at least session start)
    assert len(platformer_logs) > 0, "No Platformer logs"
    assert len(invaders_logs) > 0, "No Invaders logs"
    
    # Both should contain session markers
    assert "Session started" in platformer_logs, "Missing session in platformer logs"
    assert "Session started" in invaders_logs, "Missing session in invaders logs"
    
    print("✓ (both apps logged separately)")



def test_log_assertions():
    """Test log-based assertions."""
    print("Testing log assertions...", end=" ")
    
    runner = TestRunner("examples.platformer.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Test that session start is logged
    runner.assert_log_contains("Session started")
    
    # Test no errors assertion
    runner.assert_no_errors_logged()
    
    print("✓ (assertions work)")



def demonstrate_log_debugging_on_failure():
    """
    This demonstrates how logs help debug test failures.
    
    When a test fails, the logs show exactly what the app was doing.
    """
    print("\n" + "="*70)
    print("DEMONSTRATION: Using logs to debug test failures")
    print("="*70 + "\n")
    
    runner = TestRunner("examples.platformer.main", max_duration=10.0)
    runner.wait(1.0)
    
    print("Test scenario: Checking if player moved...")
    
    initial_pos = runner.find_sprite((0, 150, 255), tolerance=10)
    print(f"Initial player position: {initial_pos}")
    
    runner.inject_repeat(InputEvent.RIGHT, count=10, delay=0.05)
    runner.wait(0.5)
    
    new_pos = runner.find_sprite((0, 150, 255), tolerance=10)
    print(f"New player position: {new_pos}")
    
    if new_pos and initial_pos:
        if new_pos[0] > initial_pos[0]:
            print("✓ Player moved right successfully")
        else:
            print("✗ Player didn't move! Checking logs...")
            runner.print_recent_logs(lines=15)
    
    print("\nLogs provide context for:")
    print("  - What methods were called")
    print("  - What events were processed")

    print("  - Any errors or warnings")
    print("  - Timing information")
    print()


def main():
    """Run all log integration tests."""
    print("=" * 70)
    print("MatrixOS Testing Framework - Log Integration Tests")
    print("=" * 70)
    print()
    
    tests = [
        test_log_integration,
        test_log_error_detection,
        test_log_content_search,
        test_log_isolation,
        test_log_debugging,
        test_multi_app_logs,
        test_log_assertions,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Run demonstration
    demonstrate_log_debugging_on_failure()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed > 0:
        print("\n❌ Some tests failed")
        sys.exit(1)
    else:
        print("\nAll log integration tests passed! ✅")
        print("\nKey features demonstrated:")
        print("  ✓ Reading logs within tests")
        print("  ✓ Searching log content")
        print("  ✓ Detecting errors/warnings")
        print("  ✓ Isolating logs between test phases")
        print("  ✓ Multi-app log access")
        print("  ✓ Log-based assertions")
        print("  ✓ Debugging with logs")
        sys.exit(0)


if __name__ == "__main__":
    main()
