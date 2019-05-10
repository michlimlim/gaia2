# General python libraries
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from threading import Condition

# Code-specific imports
from src.update_metadata.model_update import ModelUpdate
from src.update_metadata.device_fairness import DeviceFairnessUpdateMetadata, DeviceFairnessReceiverState
from src.pendingwork import PendingWork
from src.data_partition import build_dataset_loader
from src.neural_net import Net
from src.sender import Sender
from src.util import EmptyQueueError, ExtraFatal

# Create a function that creates nodes that hold partitioned training data
def initialize_current_node(pending_work_queues, dataset='MNIST', dataset_dir='./data'):
    curr_node_ip_addr = pending_work_queues.my_host
    other_nodes_ip_addrs = pending_work_queues.other_hosts
    train_loader, test_loader = build_dataset_loader(curr_node_ip_addr, other_nodes_ip_addrs, dataset, dataset_dir, 100)
    sender_queues = Sender(1000)
    return Solver(train_loader, test_loader, pending_work_queues, sender_queues, dataset, 10, 0.005)

class Solver(object):
    def __init__(self, train_loader, test_loader, pending_work_queues, sender_queues, dataset='MNIST', n_epochs=25, lr=0.005, k=2):
        self.n_epochs = n_epochs
        self.curr_epoch = 0
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.image_dim = {'MNIST': 28*28, 'CIFAR10': 3*32*32}[dataset]
        self.net = Net(image_dim=self.image_dim)
        self.parameter_pointers = self.get_nn_module_parameter_pointers(self.net)
        self.loss_fn = nn.CrossEntropyLoss()
        self.sender_queues = sender_queues
        self.sender_queues.setup(pending_work_queues.my_host, pending_work_queues.other_hosts)
        self.sender_queues.run()
        self.pending_work_queues = pending_work_queues
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)
        self.ip_addr = pending_work_queues.my_host
        device_ip_addr_to_epoch_dict = {}
        for ip_addr in pending_work_queues.other_hosts + [pending_work_queues.my_host]:
            device_ip_addr_to_epoch_dict[ip_addr] = 0
        self.fairness_state = DeviceFairnessReceiverState(
            k,
            device_ip_addr_to_epoch_dict)
        if torch.cuda.is_available():
            self.net = self.net.cuda()
        self.condition = Condition()

    # :brief nn.module.parameters() yields a generator of nn.Parameter, but unfortunately
    #   we can't use it to later the original, so we need to remember pointers for each
    #   nn.Parameter in the neural net
    # :param nn_module [nn.module] module to extract nn.Parameter pointers from
    def get_nn_module_parameter_pointers(self, nn_module):
        return { str(idx): params for idx, params in enumerate(self.net.parameters()) }

    def minibatch_backprop_and_update_weights(self, minibatch_idx, images, labels):
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

        # Get gradients for this minibatch
        minibatch_updates = { idx: params.clone() for idx, params in self.parameter_pointers.items() }

        # Update internal state after performing one minibatch backprop
        self.fairness_state.update_internal_state_after_backprop(self.ip_addr)

        # Wrap these minibatch gadients into a ModelUpdate and send
        model_update = ModelUpdate(
            updates=minibatch_updates,
            update_metadata=self.fairness_state.device_ip_addr_to_epoch_dict)
        
        # Enqueue local update to send to other hosts' queues
        self.sender_queues.enqueue(model_update.to_json())

        # Calculate loss for this minibatch, averaged across no. of examples in this minibatch
        minibatch_loss = float(loss.data) / len(images)
        
        print(f"Minibatch {minibatch_idx} | loss: {minibatch_loss:.4f}")
        return
    
    def aggregate_received_updates(self):
        metadata_list = []
        weight_list = []

        # The list of host_id's represented in all models
        # (Cannot assume that this is the same/other_hosts all the time because metadata
        # could come from nodes outside the cluster)
        host_id_list = []
        
        models = []

        for host_id in self.pending_work_queues.other_hosts:
            # This should be a ModelUpdate object
            try:
                host_weight_list, host_metadata_list, id_list = self.pending_work_queues.empty_model_and_metadata_from(host_id)
                print('AGG FROM: ', host_id)
                weight_list.extend(host_weight_list)
                metadata_list.extend(host_metadata_list)
                host_id_list.extend(id_list)

            except EmptyQueueError:
                print('EMPTY Q:', host_id)
                continue

        # Return if empty
        if len(metadata_list) == 0:
            return
        
        # Remove duplicate host id's
        host_id_list = set(host_id_list)

        metadata_list.append(self.fairness_state.device_ip_addr_to_epoch_dict)
        weight_list.append(self.parameter_pointers)
        alphas = self.fairness_state.get_alphas(metadata_list, host_id_list)

        # Sanity check
        if (len(alphas) != len(weight_list)) or (len(weight_list) != len(metadata_list)):
            print(len(alphas), 'alphas')
            print(len(weight_list), 'weigts')
            print(len(metadata_list), 'metadata')
            raise ValueError("Something very wrong with our alphas")

        self.fairness_state.update_internal_state_after_aggregation(
            alphas, 
            metadata_list,
            host_id_list)
        # Update weights by overwriting self.parameter_pointers
        for idx, _ in self.parameter_pointers.items():
            self.parameter_pointers[idx] = sum([
                alpha * weight[idx] for alpha, weight in zip(alphas, weight_list)])
        return

    def train(self):
        minibatches = list(self.train_loader)
        i = 0
        while i < len(minibatches): 
            while self.pending_work_queues.total_no_of_updates > 0:
                # Aggregate
                self.aggregate_received_updates()

            # Check if we can backprop
            images, labels = minibatches[i]
            self.minibatch_backprop_and_update_weights(i, images, labels)
            i += 1
            

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

