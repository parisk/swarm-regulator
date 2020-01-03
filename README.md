# Swarm Regulator

Regulate your Docker Swarm cluster, with YOUR rules.

TBD

## Requirements

- Docker Swarm Mode cluster

## Install

TBD

## Run

TBD

## Example

### `regulator.py`
```py
from swarm_regulator import consumer


def _extract_constraints(service_spec):
    return service_spec["TaskTemplate"]["Placement"].get("Constraints", [])


def has_not_constraints(service_spec) -> bool:
    constraints = _extract_constraints(service_spec)
    return not len(constraints)


async def do_not_schedule_on_gpu(service_spec):
    constraints = _extract_constraints(service_spec) + ["node.labels.gpu!=true"]
    service_spec["TaskTemplate"]["Placement"]["Constraints"] = constraints
    return service_spec


consumer.register_rule(
    "service", has_not_constraints, do_not_schedule_on_gpu,
)

consumer.run()
```

### Run

```console
python regulator.py
```
