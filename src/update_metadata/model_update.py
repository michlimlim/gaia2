import json
import torch

class ModelUpdate(object):
    def __init__(self, updates, update_metadata):
        # :brief Store a model update sent by a device from its local data
        # :param updates [dict<int, torch.tensor>] maps the int i-th module of the network to the 
        #     gradient update. Only int needed because all devices have same network arch
        # :param update_metadata [dict] arbitrary dict
        self.updates = updates
        self.update_metadata = update_metadata

    def to_json(self):
        # :brief Converts current object into a json representation
        return json.dumps({
            'updates': {str(k): v.data.numpy().tolist() for k, v in self.updates.items()},
            'update_metadata': self.update_metadata
        })

    @staticmethod
    def from_dict(d):
        # :brief Converts dict version of model update into an object form
        model_update_obj = d
        model_update_obj.updates = {k: torch.Tensor(v) for k,v in model_update_obj.updates.items()}
        return model_update_obj
