import torch.nn as nn

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
            
    def forward(self, x):
        return self.net(x)