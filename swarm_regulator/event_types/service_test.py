import json
import os

import pytest

from . import service

@pytest.fixture
def service_payload():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.join(current_dir, os.path.pardir)
    fixtures_dir = os.path.join(parent_dir, "fixtures")
    fixture_file = os.path.join(fixtures_dir, "service.json")

    with open(fixture_file) as fixture:
        return json.loads(fixture.read())


def test_spec_as_update_payload(service_payload):
    update_payload = service.extract_update_payload(service_payload)
    assert update_payload == service_payload["Spec"]


def test_version_in_update_params(service_payload):
    update_params = service.extract_update_params(service_payload)
    assert update_params["version"] == service_payload["Version"]["Index"]
