# General python libraries
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

# Code-specific imports
from pendingwork import PendingWork
from data_partition import build_dataset_loader
from neural_net import Net

# Create a function that creates nodes that hold partitioned training data
def initialize_current_node(curr_node, pending_work_queues, dataset='MNIST', dataset_dir='./data'):
    train_loader, test_loader = build_dataset_loader(curr_node, pending_work_queues.num_devices, dataset, dataset_dir, 100)
    return Solver(train_loader, test_loader, pending_work_queues, dataset, 10, 0.005)

class Solver(object):
    def __init__(self, train_loader, test_loader, pending_work_queues, dataset='MNIST', n_epochs=25, lr=0.005):
        self.n_epochs = n_epochs
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.image_dim = {'MNIST': 28*28, 'CIFAR10': 3*32*32}[dataset]
        self.net = Net(image_dim=self.image_dim)
        self.loss_fn = nn.CrossEntropyLoss()
        self.pending_work_queues = pending_work_queues
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
                
                # Enqueue local gradients for my own queue and other hosts' queues
                for host_id in self.pending_work_queues.other_hosts + [self.pending_work_queues.my_host]:
                    self.pending_work_queues.enqueue(local_gradients, host_id)

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
    pending_work_queues = PendingWork()
    pending_work_queues.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    # TODO (Weitai): to change the device id to be the raw addresses of the flask apps
    node = initialize_current_node(0, pending_work_queues, 'MNIST', './data')
    node.train_and_enqueue_local_gradients()
    node.evaluate()
