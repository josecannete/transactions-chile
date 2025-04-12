"""
Pytest configuration file.
"""


# Add any shared fixtures or configuration here
def pytest_configure(config):
    """Custom pytest configuration."""
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
