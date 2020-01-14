# Swarm Regulator

Regulate your Docker Swarm cluster, according to YOUR rules. Use `async` Python functions to enforce rules like service placement and resource management on your Docker Swarm.

## Concepts

### Consumer

Each regulator is based on top of a single consumer. The consumer responds to Docker events and instruments all components of the regulator.

### Conditions

A regulator needs to know when to apply its rules. This is what conditions are for. Conditions help us know when should a rule be applied on a Docker Swarm entity. In brief, a condition is a Python function (or callable) that accepts a Docker Swarm entity as a single argument and returns `True` when the rule should run, and `False` when it shouldn't.

**🙌 Heads up**: In order to avoid infinite loops, a confition that initially returns `True`, should return `False`, when it gets the regulated entity as an argument. If this is not the case, the rule is being ignored.

### Rules

Rules simply do the job. Rules are **`async`** Python functions that accept a Docker Swarm entity as an argument and return it modified, so it complies with the business logic we intend to enforce on our Docker Swarm cluster.

## Requirements

- Python 3.8+
- Docker Swarm Mode cluster

## Install

### pipenv

```
pipenv install swarm-regulator
```

### poetry

```
poetry add swarm-regulator
```

### pip

```
pip install swarm-regulator
```

## Run

1. Create a Python file (e.g. `regulator.py`)
2. Import the `consumer` from the `swarm_regulator` package
3. Register your rules that will run according to given conditions
4. Run your regulator

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
