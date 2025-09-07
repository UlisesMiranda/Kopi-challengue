import pytest


@pytest.fixture(autouse=True)
def set_openai_api_key(monkeypatch):
    """
    Automatically set a dummy OpenAI API key for all tests.

    This fixture runs for every test and uses pytest's `monkeypatch`
    to set a dummy environment variable. This prevents the OpenAI client
    from raising an error during its initialization in a test environment.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "DUMMY_KEY_FOR_TESTING")
