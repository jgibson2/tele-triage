import yaml
from models import ResponseModel, Actions
import sys

def response_model_from_yaml_file(filename):
    with open(filename, 'r') as f:
        text = f.read()
        return response_model_from_yaml(text)

def response_model_from_yaml_text(text):
    schema = yaml.safe_load(text)
    return response_model_from_yaml(schema)

def response_model_from_yaml(yml):
    resp = ResponseModel()
    for obj in yml:
        if 'send' in obj:
            resp.send(obj['send']['message'])
        if 'receive' in obj:
            resp.receive(obj['receive']['key'], getattr(sys.modules['builtins'], obj['receive']['expect_type']), getattr(Actions, obj['receive']['on_failure']))
        if 'conditional' in obj:
            resp.conditional(lambda message: eval(obj['conditional']['condition']),
                             response_model_from_yaml(obj['conditional']['response_if_true']),
                             response_model_from_yaml(obj['conditional']['response_if_false']))
    return resp