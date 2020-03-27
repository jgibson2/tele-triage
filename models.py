import queue
import enum
import collections
import logging

Actions = enum.Enum('Actions', ['send', 'receive', 'retry'])

class ResponseModel:
    def __init__(self):
        self.actions = queue.Queue()


    def send(self, message):
        self.actions.put((Actions.send, message))
        return self


    def receive(self, key,  expect_type=str, on_failure=Actions.retry):
        self.actions.put((Actions.receive, key, expect_type, on_failure))
        return self


    def build(self, uuid, logger=None):
        return UserModel(uuid, self.actions, logger)


class UserModel:
    def __init__(self, uuid, actions, logger=None):
        self.uuid = uuid
        self.actions = actions
        self.values = collections.OrderedDict()
        if(logger is None):
            logger = logging.getLogger(str(uuid))
        self.logger = logger


    def act(self, message):
        # TODO: add authentication of uuid in this method?
        if self.actions.empty():
            return None
        action = self.actions.pop()
        if action[0] == Actions.receive:
            try:
                val = action[2](message)
                self.values[action[1]] = val
            except:
                self.logger.error(f'Could not parse {message} to {action[2]}!')
                if action[3] == Actions.retry:
                    self.actions.put(action)
                    return "Sorry, we didn't understand that. Try again?"
            return self.act(message) # recurse until we get a send
        elif action[0] == Actions.send:
            return action[1]
        return None


