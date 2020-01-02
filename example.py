import re

import swarm_regulator


def _is_edge(constraint):
    return re.match(r"^node\.labels\.edge(=|!)=", constraint)


def always(event, service) -> bool:
    return True


def has_not_edge_constraint(event, service) -> bool:
    constraints = service["Spec"]["TaskTemplate"]["Placement"]
    edge_constraints = [
        constraint for constraint in constraints if _is_edge(constraint)
    ]
    return len(edge_constraints) == 0


async def print_service(service):
    print(service)
    return {"Spec": {"TaskTemplate": {"Init": True,}}}


async def do_not_schedule_on_edge(service):
    return {
        "Spec": {"TaskTemplate": {"Placement": "node.labels.edge!=true"}},
    }


swarm_regulator.register_rule(
    "service", has_not_edge_constraint, do_not_schedule_on_edge,
)
swarm_regulator.register_rule("service", always, print_service)

swarm_regulator.run()
