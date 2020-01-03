import asyncio
import copy
import json

import aiodocker

from .event_types import service

EVENT_TYPES = {
    "service": service,
}


_rules = []


def _get_rules_for_event_type(event_type: str) -> list:
    rules = [
        (condition, callback)
        for (resource_type, condition, callback) in _rules
        if resource_type == event_type
    ]
    return rules


def _get_rules_with_matching_conditions(rules, payload):
    rules_with_matching_conditions = [
        (condition, callback) for (condition, callback) in rules if condition(payload)
    ]
    return rules_with_matching_conditions


def _should_accept_regulated_payload(payload, condition):
    """
    We should only accept payloads that do not match the condition of their
    rules to avoid endless updates. Rules should produce payloads that DO NOT
    match their conditions.
    """
    return not condition(payload)


async def _regulate_payload(payload, rules):
    update_payload = payload

    for condition, callback in rules:
        copied_payload = copy.deepcopy(payload)
        regulated_payload = await callback(copied_payload)

        if _should_accept_regulated_payload(regulated_payload, condition):
            update_payload = regulated_payload

    return update_payload


def register_rule(resource_type: str, condition: callable, callback: callable):
    _rules.append((resource_type, condition, callback))


async def consume_event(docker, event: dict):
    event_type = event["Type"]
    event_action = event["Action"]
    resource_id = event["Actor"]["ID"]
    api_name = f"{event_type}s"
    api = getattr(docker, api_name)

    if event_type not in EVENT_TYPES:
        return

    resource_module = EVENT_TYPES[event_type]

    if event_action not in resource_module.SUPPORTED_ACTIONS:
        return

    resource = await api.inspect(resource_id)
    update_payload = resource_module.extract_update_payload(resource)
    resource_rules = _get_rules_for_event_type(event_type)
    rules = _get_rules_with_matching_conditions(resource_rules, update_payload)

    if not len(rules):
        return

    regulated_update_payload = await _regulate_payload(update_payload, rules)
    data = json.dumps(regulated_update_payload)
    params = resource_module.extract_update_params(resource)

    await docker._query_json(
        f"{api_name}/{resource_id}/update", method="POST", data=data, params=params,
    )


async def main():
    docker = aiodocker.Docker()
    subscriber = docker.events.subscribe()

    while event := await subscriber.get():
        await consume_event(docker, event)


def run():
    asyncio.run(main())
