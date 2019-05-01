import json

class ModelUpdate(object):
    def __init__(self, gradients, gradient_metadata):
        # :brief Store a model update sent by a device from its local data
        # :param gradients [dict<int, torch.tensor>] maps the int i-th module of the network to the 
        #     gradient update
        # :param gradient_metadata [dict] user-defined GradientMetadata object in __dict__ form
        self.gradients = gradients
        self.gradient_metadata = gradient_metadata

    def to_json(self):
        # :brief Converts current object into a json representation
        return json.dumps({
            'gradients': self.gradients,
            'gradient_metadata': self.gradient_metadata.__dict__
        })

    def from_json(json_string):
        # :brief Converts json version of model update into an object form
        return ModelUpdate(**json.loads(json_string))
