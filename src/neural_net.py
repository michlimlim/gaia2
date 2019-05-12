import torch.nn as nn
import numpy as np

class Net(nn.Module):
    def __init__(self, image_dim=28*28):
        super(Net, self).__init__()
        """3-Layer Fully-connected NN"""

        self.net = nn.Sequential(
            nn.Linear(image_dim, 500),
            nn.ReLU(),
            nn.Linear(500, 100),
            nn.ReLU(),
            nn.Linear(100, 10)) 
             
        self.net.apply(weights_init_uniform)     
            
    def forward(self, x):
        return self.net(x)

# From https://stackoverflow.com/questions/49433936/how-to-initialize-weights-in-pytorch        
# takes in a module and applies the specified weight initialization
def weights_init_uniform(m):
    '''Takes in a module and initializes all linear layers with weight
           values taken from a normal distribution.'''

    classname = m.__class__.__name__
    # for every Linear layer in a model
    if classname.find('Linear') != -1:
        y = m.in_features
    # m.weight.data shoud be taken from a normal distribution
        m.weight.data.normal_(0.0,1/np.sqrt(y))
    # m.bias.data should be 0
        m.bias.data.fill_(0)
