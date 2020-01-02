import asyncio
import json

import aiodocker


SUPPORTED_EVENT_TYPES = ("service",)
SUPPORTED_EVENT_ACTIONS = ("create", "update")


_rules = []


def _merge_patches(root: dict, update_patch: dict) -> dict:
    for key, value in update_patch.items():
        root_value = root.get(key, None)

        if isinstance(root_value, dict):
            updated_value = _merge_patches(root_value, value)
        else:
            updated_value = value

        root[key] = updated_value

    return root


def register_rule(resource_type: str, condition: callable, callback: callable):
    _rules.append((resource_type, condition, callback))


async def consume_event(docker, event: dict):
    event_type = event["Type"]
    event_action = event["Action"]
    resource_id = event["Actor"]["ID"]

    if (event_type not in SUPPORTED_EVENT_TYPES) or (
        event_action not in SUPPORTED_EVENT_ACTIONS
    ):
        return

    api_name = f"{event_type}s"
    api = getattr(docker, api_name)
    resource = await api.inspect(resource_id)
    resource_rules = [
        (condition, callback)
        for (resource_type, condition, callback) in _rules
        if resource_type == event_type
    ]
    eligible_rules = [
        callback
        for (condition, callback) in resource_rules
        if condition(event, resource)
    ]
    patches = [await callback(resource) for callback in eligible_rules]
    update_patch = {}

    for patch in patches:
        update_patch = _merge_patches(update_patch, patch)

    data = json.dumps(update_patch)
    params = {
        "version": resource["Version"]["Index"],
    }

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
