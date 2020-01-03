import asyncio
import json

import aiodocker


EVENT_TYPES = {
    "service": {
        "get_update_payload": lambda resource: resource["Spec"],
        "get_params": lambda resource: {"version": resource["Version"]["Index"]},
    }
}
SUPPORTED_EVENT_ACTIONS = ("create", "update")


_rules = []


def register_rule(resource_type: str, condition: callable, callback: callable):
    _rules.append((resource_type, condition, callback))


async def consume_event(docker, event: dict):
    event_type = event["Type"]
    event_action = event["Action"]
    resource_id = event["Actor"]["ID"]

    if (event_type not in EVENT_TYPES) or (
        event_action not in SUPPORTED_EVENT_ACTIONS
    ):
        return

    api_name = f"{event_type}s"
    api = getattr(docker, api_name)
    resource = await api.inspect(resource_id)

    update_payload = EVENT_TYPES[event_type]["get_update_payload"](resource)

    resource_rules = [
        (condition, callback)
        for (resource_type, condition, callback) in _rules
        if resource_type == event_type
    ]
    eligible_rules = [
        (condition, callback)
        for (condition, callback) in resource_rules
        if condition(update_payload)
    ]

    if not len(eligible_rules):
        return

    for condition, callback in eligible_rules:
        regulated_payload = await callback(update_payload)

        if not condition(regulated_payload):
            update_payload = regulated_payload

    data = json.dumps(update_payload)
    params = EVENT_TYPES[event_type]["get_params"](resource)

    print(data)
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
