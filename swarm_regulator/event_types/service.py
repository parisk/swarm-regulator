SUPPORTED_ACTIONS = ("create", "update")


def extract_update_payload(resource: dict) -> dict:
    return resource["Spec"]


def extract_update_params(resource: dict) -> dict:
    return {"version": resource["Version"]["Index"]}
