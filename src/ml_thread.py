# General python libraries
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

# Code-specific imports
from src.model_update import ModelUpdate
from src.update_metadata.device_fairness import DeviceFairnessUpdateMetadata, DeviceFairnessReceiverState
from src.pendingwork import PendingWork
from src.data_partition import build_dataset_loader
from src.neural_net import Net
from src.util import EmptyQueueError

# Create a function that creates nodes that hold partitioned training data
def initialize_current_node(pending_work_queues, dataset='MNIST', dataset_dir='./data'):
    curr_node_ip_addr = pending_work_queues.my_host
    other_nodes_ip_addrs = pending_work_queues.other_hosts
    train_loader, test_loader = build_dataset_loader(curr_node_ip_addr, other_nodes_ip_addrs, dataset, dataset_dir, 100)
    return Solver(train_loader, test_loader, pending_work_queues, dataset, 10, 0.005)

class Solver(object):
    def __init__(self, train_loader, test_loader, pending_work_queues, dataset='MNIST', n_epochs=25, lr=0.005, k=3):
        self.n_epochs = n_epochs
        self.curr_epoch = 0
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.image_dim = {'MNIST': 28*28, 'CIFAR10': 3*32*32}[dataset]
        self.net = Net(image_dim=self.image_dim)
        self.parameter_pointers = self.get_nn_module_parameter_pointers(self.net)
        self.loss_fn = nn.CrossEntropyLoss()
        self.pending_work_queues = pending_work_queues
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)
        self.ip_addr = pending_work_queues.my_host
        device_ip_addr_to_epoch_dict = {}
        for ip_addr in pending_work_queues.other_hosts + [pending_work_queues.my_host]:
            device_ip_addr_to_epoch_dict[ip_addr] = 0
        self.fairness_state = DeviceFairnessReceiverState(
            k,
            pending_work_queues.num_devices,
            device_ip_addr_to_epoch_dict)
        if torch.cuda.is_available():
            self.net = self.net.cuda()

    # :brief nn.module.parameters() yields a generator of nn.Parameter, but unfortunately
    #   we can't use it to later the original, so we need to remember pointers for each
    #   nn.Parameter in the neural net
    # :param nn_module [nn.module] module to extract nn.Parameter pointers from
    def get_nn_module_parameter_pointers(self, nn_module):
        return { idx: params for idx, params in enumerate(self.net.parameters()) }

    def backprop_and_get_new_weights(self):
        weights_before_epoch = {}
        weights_after_epoch = {}
        epoch_loss = 0
        minibatches = 0

        # Store a copy of weights before epoch
        for idx, params in self.parameter_pointers.items():
            weights_before_epoch[idx] = params.clone()

        # Train through minibatches
        for images, labels in self.train_loader:
            minibatches += 1
            images = Variable(images).view(-1, self.image_dim)
            labels = Variable(labels)
            if torch.cuda.is_available():
                images = images.cuda()
                labels = labels.cuda()

            logits = self.net(images)
            loss = self.loss_fn(logits, labels)
            self.optimizer.zero_grad()
            loss.backward()
            # Update weights on this minibatch's gradient
            self.optimizer.step()
            # Accumulate epoch loss across minibatches
            epoch_loss += float(loss.data)

        epoch_loss /= len(self.train_loader.dataset)
        print(f"Epoch {self.curr_epoch} | loss: {epoch_loss:.4f}")

        # Restore current neural net's weights to weights before epoch
        for idx, params in self.parameter_pointers.items():
            weights_after_epoch = params.clone()
            # print(params - weights_after_epoch[idx]) # This is the gradient
            self.parameter_pointers[idx] = weights_before_epoch[idx]

        """
        Defunct because we now send weights instead of gradients
        # Calculate diff between curr params and previous params    
        for idx, params in enumerate(self.net.parameters()):
            epoch_gradient_updates[idx] = params - weights_before_epoch[idx]
        """
        return weights_after_epoch

    def aggregate_received_weights(self):
        # TODO: (ml/wt) To simplify calculation, we should just enqueue our own weights into the 
        # aggregation queues. right now i don't think this is implemented
        num_devices_used_during_agg = 0
        aggregate_weights = {}
        for host_id in self.pending_work_queues.other_hosts:
            # This should be a ModelUpdate object
            try:
                model_update = self.pending_work_queues.dequeue(host_id)
                update_metadata = model_update.update_metadata
                for idx, params in model_update.updates:
                    aggregate_weights[idx] += params
                num_devices_used_during_agg += 1
                self.fairness_state.update_device_fairness(
                    host_id,
                    update_metadata.device_ip_addr_to_epoch_dict[host_id])
            except EmptyQueueError:
                continue

        # Update weights by overwriting self.parameter_pointers
        for idx, params in self.parameter_pointers.items():
            self.parameter_pointers[idx] = aggregate_weights[idx] / float(self.pending_work_queues.num_devices)

    def train(self):
        while self.curr_epoch < self.n_epochs:
            print(self.curr_epoch)
            # Check if we can backprop
            if self.fairness_state.check_device_fairness():
                epoch_weights = self.backprop_and_get_new_weights()
                self.curr_epoch += 1
                # Update internal fairness state
                self.fairness_state.update_device_fairness(self.ip_addr, self.curr_epoch)
                model_update = ModelUpdate(
                    updates=epoch_weights,
                    update_metadata=self.fairness_state)
                # Enqueue local gradients for other hosts' queues
                for host_id in self.pending_work_queues.other_hosts:
                    # TODO(ml/wt): send model_update to host_id
                    # The fact that we used an object should probably get 
                    # Python to use a pointer to the object instead of copying the update
                    # deeply over and over again
                    pass
                    
            # If we can't, we can only try to aggregate
            else:
                self.aggregate_received_weights()

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

