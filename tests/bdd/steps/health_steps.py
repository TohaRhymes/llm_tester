"""
BDD step definitions for API health check.
"""
from behave import when, then
from tests.utils import SyncASGIClient

client = SyncASGIClient()


@when('I request the health endpoint')
def step_request_health(context):
    """Request the health endpoint."""
    context.response = client.get("/health")


@then('I receive a successful response')
def step_check_successful_response(context):
    """Check that response is successful."""
    assert context.response.status_code == 200


@then('the status is "{expected_status}"')
def step_check_status(context, expected_status):
    """Check that status matches expected value."""
    data = context.response.json()
    assert data["status"] == expected_status


@then('the version information is present')
def step_check_version_present(context):
    """Check that version is present in response."""
    data = context.response.json()
    assert "version" in data
    assert data["version"] is not None
