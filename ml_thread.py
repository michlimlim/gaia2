# General python libraries
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

# Code-specific imports
# from somewhere import enqueue
# from somewhere import PendingWork
from data_partition import build_dataset_loader
from neural_net import Net

class LocalState(object):
    def __init__(self, config_dict):
        self.device_id = config_dict['device_id']

# Create a function that creates nodes that hold partitioned training data
def initialize_current_node(curr_node, no_of_nodes = 2, dataset='MNIST', dataset_dir='./data'):
    train_loader, test_loader = build_dataset_loader(curr_node, no_of_nodes, dataset, dataset_dir, 100)
    return Solver(train_loader, test_loader, dataset, 2, 0.005)

class Solver(object):
    def __init__(self, train_loader, test_loader, dataset='MNIST', n_epochs=25, lr=0.005):
        self.n_epochs = n_epochs
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.image_dim = {'MNIST': 28*28, 'CIFAR10': 3*32*32}[dataset]
        self.net = Net(image_dim=self.image_dim)
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)
        if torch.cuda.is_available():
            self.net = self.net.cuda()  

    def train_and_enqueue_local_gradients(self):
        self.net.train()
        for epoch_i in range(self.n_epochs):
            local_gradients = {}
            epoch_i += 1
            epoch_loss = 0
            for images, labels in self.train_loader:
                images = Variable(images).view(-1, self.image_dim)
                labels = Variable(labels)
                if torch.cuda.is_available():
                    images = images.cuda()
                    labels = labels.cuda()

                logits = self.net(images)
                loss = self.loss_fn(logits, labels)
                self.optimizer.zero_grad()
                loss.backward()
                # Since everybody has the same net structure, the only thing
                # we need to identify which gradients belongs to which parameter
                # is the sequence number.
                for idx, p in enumerate(self.net.parameters()):
                    # obtain gradient for each param here.
                    # then we send the gradient!
                    local_gradients[idx] = p.grad

                # Enqueue local gradients for each device id which is not myself
                for device_id in range(PendingWork.num_devices):
                    PendingWork.enqueue(local_gradients, device_id)
                # In the usual case, we call the step() function on the optimizer,
                # which will adjust the weights for
                # each part of the net from the gradient.
                # But this is commented out now because the aggregator function
                # will perform the aggregation!
                # self.optimizer.step()
                epoch_loss += float(loss.data)

            epoch_loss /= len(self.train_loader.dataset)
            print(f"Epoch {epoch_i} | loss: {epoch_loss:.4f}")
            
    def evaluate(self):
        total = 0
        correct = 0
        self.net.eval()
        for images, labels in self.test_loader:
            images = Variable(images).view(-1, self.image_dim)
            if torch.cuda.is_available():
                images = images.cuda()
            logits = self.net(images)
            _, predicted = torch.max(logits.data, 1)
            total += labels.size(0)
            correct += (predicted.cpu() == labels).sum()
        print(f'Accuracy: {100 * correct / total:.2f}%')


if __name__=="__main__":
    with open('config.json') as f:
        local_state = LocalState(json.loads(f.read()))

    node = initialize_current_node(local_state.device_id, PendingWork.num_devices, 'MNIST', './data')
    node.train()
    node.evaluate()
