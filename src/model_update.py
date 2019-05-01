import json

class ModelUpdate(object):
    def __init__(self, updates, update_metadata):
        # :brief Store a model update sent by a device from its local data
        # :param updates [dict<int, torch.tensor>] maps the int i-th module of the network to the 
        #     gradient update. Only int needed because all devices have same network arch
        # :param gradient_metadata [dict] user-defined UpdateMetadata object in __dict__ form
        self.updates = updates
        self.update_metadata = update_metadata

    def to_json(self):
        # :brief Converts current object into a json representation
        return json.dumps({
            'updates': self.updates,
            'update_metadata': self.update_metadata.__dict__
        })

    def from_json(json_string):
        # :brief Converts json version of model update into an object form
        return ModelUpdate(**json.loads(json_string))
