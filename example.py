import re

from swarm_regulator import consumer


def _is_edge(constraint: str):
    return re.match(r"^node\.labels\.edge(=|!)=", constraint)


def has_not_edge_constraint(service_spec) -> bool:
    constraints = service_spec["TaskTemplate"]["Placement"].get("Constraints", [])
    return not any([_is_edge(constraint) for constraint in constraints])


async def do_not_schedule_on_edge(service_spec):
    constraints = service_spec["TaskTemplate"]["Placement"].get("Constraints", []) + [
        "node.labels.edge!=true"
    ]
    service_spec["TaskTemplate"]["Placement"]["Constraints"] = constraints
    return service_spec


consumer.register_rule(
    "service", has_not_edge_constraint, do_not_schedule_on_edge,
)

consumer.run()
