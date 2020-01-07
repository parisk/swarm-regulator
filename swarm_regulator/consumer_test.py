import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from . import consumer
from .event_types import service


@pytest.fixture
def service_payload():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    fixtures_dir = os.path.join(current_dir, "fixtures")
    fixture_file = os.path.join(fixtures_dir, "service.json")

    with open(fixture_file) as fixture:
        return json.loads(fixture.read())


def test_register_rule():
    mocked_rules_list = []
    resource_type = 'something'
    condition = lambda x: False
    callback = lambda x: True

    with patch("swarm_regulator.consumer._rules", mocked_rules_list):
        consumer.register_rule(resource_type, condition, callback)

    assert mocked_rules_list == [(resource_type, condition, callback)]


@pytest.mark.asyncio
async def test_consume_event_service(service_payload):
    mocked_query_json = AsyncMock()
    mocked_service_inspect = AsyncMock(return_value=service_payload)
    mocked_services_api = MagicMock()
    mocked_services_api.inspect = mocked_service_inspect
    mocked_docker = MagicMock()
    mocked_docker._query_json = mocked_query_json
    mocked_docker.services = mocked_services_api
    dummy_event = {
        "Type": "service",
        "Action": "create",
        "Actor": {
            "ID": service_payload["ID"],
        },
    }

    def dummy_condition(service_spec):
        """Check if service name starts with `dummy-`."""
        return not service_spec["Name"].startswith("dummy-")

    async def dummy_callback(service_spec):
        """Prepend service name with `dummy-`."""
        service_spec["Name"] = f"dummy-{service_spec['Name']}"
        return service_spec

    consumer.register_rule("service", dummy_condition, dummy_callback)

    await consumer.consume_event(mocked_docker, dummy_event)

    update_payload = service.extract_update_payload(service_payload)
    data = await dummy_callback(update_payload)
    params = service.extract_update_params(service_payload)
    mocked_query_json.assert_awaited_once_with(
        f"services/{service_payload['ID']}/update",
        method="POST",
        data=json.dumps(data),
        params=params,
    )
