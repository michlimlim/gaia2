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

    def backprop_and_get_new_weights(self):
        weights_before_epoch = {}
        weights_after_epoch = {}
        epoch_loss = 0

        # Store a copy of weights before epoch
        for idx, params in self.parameter_pointers.items():
            weights_before_epoch[idx] = params.clone()

        # Train through minibatches
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
            # Update weights on this minibatch's gradient
            self.optimizer.step()
            # Accumulate epoch loss across minibatches
            epoch_loss += float(loss.data)

        epoch_loss /= len(self.train_loader.dataset)
        print(f"Epoch {self.curr_epoch} | loss: {epoch_loss:.4f}")

        # Restore current neural net's weights to weights before epoch
        for idx, params in self.parameter_pointers.items():
            weights_after_epoch[idx] = params.clone()
            # print(params - weights_after_epoch[idx]) # This is the gradient
            self.parameter_pointers[idx] = weights_before_epoch[idx]

        return weights_after_epoch

    def aggregate_received_updates(self):
        # dict<str, ModelUpdate> Maps host ip addr to its ModelUpdate object
        host_to_model_update = {}

        for host_id in self.pending_work_queues.other_hosts + [self.pending_work_queues.my_host]:
            # This should be a ModelUpdate object
            try:
                # The dequeue function ensures model_update isn't None
                model_update_dict = self.pending_work_queues.dequeue(host_id)
                print('AGG FROM ', host_id)
                model_update = ModelUpdate.from_dict(model_update_dict, host_id)
                # Discard an unfair incoming model update
                if not self.fairness_state.check_fairness_before_aggregation(model_update):
                    continue
                host_to_model_update[host_id] = model_update
            except EmptyQueueError:
                # print('empty for now', host_id)
                continue

        if len(host_to_model_update) == 0:
            if self.fairness_state.check_fairness_before_backprop(self.ip_addr):
                return
            else:
                # print('Nothing to aggregate, and we cannot backprop')
                # print(self.fairness_state.device_ip_addr_to_epoch_dict)
                # print(self.fairness_state.max_epoch_num, self.fairness_state.min_epoch_num, self.fairness_state.k)
                with self.condition:
                    # print("ML THREAD SLEEPING")
                    self.condition.wait()
                # print("ML THREAD WOKE UP")
                return

        weights_for_each_update = self.fairness_state.calculate_weights_for_each_host(host_to_model_update)
        self.fairness_state.update_internal_state_after_aggregation(self.ip_addr, host_to_model_update)
        # Update weights by overwriting self.parameter_pointers
        for idx, _ in self.parameter_pointers.items():
            self.parameter_pointers[idx] = sum([
                host_to_model_update[host].updates[idx] * weights_for_each_update[host]
                for host in host_to_model_update.keys()
            ])

    def train(self):
        while self.curr_epoch < self.n_epochs:
            # print("START CURRENT EPOCH:", self.curr_epoch)
            # Check if we can backprop
            if self.fairness_state.check_fairness_before_backprop(self.ip_addr):
                epoch_weights = self.backprop_and_get_new_weights()
                self.curr_epoch += 1
                # Update internal fairness state
                self.fairness_state.update_internal_state_after_backprop(self.ip_addr)
                model_update = ModelUpdate(
                    updates=epoch_weights,
                    update_metadata=self.fairness_state.export_copy_of_internal_state_for_sending())
                # TODO(ml): Set the synchronization clock cycle in command line
                if self.pending_work_queues.is_leader() and self.curr_epoch > 1 and self.curr_epoch % 2 == 0:
                    print("Initiating Synchronization")
                    self.local_synchronize(model_update.to_json())
                else:     
                    # Enqueue local update to send to other hosts' queues
                    self.sender_queues.enqueue(model_update.to_json())
                # Enqueue local update to my own receiving queue
                self.pending_work_queues.enqueue(model_update, self.ip_addr)
            # If can't backprop, try to aggregate
            self.aggregate_received_updates()

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
    
    def local_synchronize(self, update):
        # :brief Synchronize all devices in the cluster with an update.
        # We will clear all queues in self and other devices first
        # Then we will send our updates 
        # :param update [Object] a model update that needs to be processed
        # Stop all enqueues from non-leader and clear all queues
        self.pending_work_queues.clear_all()
        # Get all devices to clear their queuess
        self.sender_queues.enqueue({"CLEAR" : True, "epoch": self.curr_epoch})
        # Then enqueue the model
        self.sender_queues.enqueue(update)
