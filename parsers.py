import yaml
from models import ResponseModel, Actions
import sys


def response_model_from_yaml(filename):
    resp = ResponseModel()
    with open(filename, 'r') as f:
        schema = yaml.safe_load(f)
        for obj in schema:
            if 'send' in obj:
                resp.send(obj['send']['message'])
            if 'receive' in obj:
                resp.receive(obj['receive']['key'], getattr(sys.modules['builtins'], obj['receive']['expect_type']), getattr(Actions, obj['receive']['on_failure']))
    return resp