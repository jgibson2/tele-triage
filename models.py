import enum
import collections
import logging

Actions = enum.Enum('Actions', ['send', 'receive', 'condition', 'retry', 'stop'])
retry_message = "Sorry, we didn't understand that. Try again?"

class ResponseModel:
    def __init__(self):
        self.actions = collections.deque()

    def send(self, message):
        self.actions.append((Actions.send, message))
        return self

    def receive(self, key, expect_type=str, on_failure=Actions.retry):
        self.actions.append((Actions.receive, key, expect_type, on_failure))
        return self

    def conditional(self, condition, response_model_if_true, response_model_if_false):
        self.actions.append((Actions.condition, condition, response_model_if_true, response_model_if_false))
        return self

    def build(self, uuid, logger=None):
        self.actions.append((Actions.stop,))
        return UserModel(uuid, self.actions, logger) if uuid is not None else None


class UserModel:
    def __init__(self, uuid, actions, logger=None):
        self.uuid = uuid
        self.actions = actions
        self.values = collections.OrderedDict()
        if(logger is None):
            logger = logging.getLogger(str(uuid))
        self.logger = logger

    """
    Returns the response to give, and whether to continue or not
    """
    def get_response(self, message):
        try:
            action = self.actions.popleft()
        except IndexError:
            return Actions.stop
        if action[0] == Actions.receive:
            try:
                val = action[2](message)
                self.values[action[1]] = val
            except:
                self.logger.error(f'Could not parse {message} to {action[2]}!')
                if action[3] == Actions.retry:
                    self.actions.appendleft(action)
                    return (retry_message, True)
            return self.get_response(message) # recurse until we get a send
        elif action[0] == Actions.send:
            do_continue = False
            try:
                do_continue = self.actions[0][0] is not Actions.stop
            except IndexError:
                pass
            return (action[1], do_continue)
        elif action[0] == Actions.condition:
            cond = action[1](message) #unsafe, so use wisely!
            if(cond):
                self.actions.extendleft(action[2].actions)
            else:
                self.actions.extendleft(action[3].actions)
            return self.get_response(message)
        return self.get_response(message)


class UserModelRepository:
    def __init__(self, response_model, logger=None):
        self.users = {}
        self.logger = logger
        self.response_model = response_model

    def get_or_create(self, uuid):
        if uuid not in self.users:
            self.users[uuid] = self.response_model.build(uuid, self.logger)
        return self.users[uuid]

    def delete(self, uuid):
        if uuid in self.users:
            del self.users[uuid]

    def get_response(self, uuid, message):
        return self.get_or_create(uuid).get_response(message)