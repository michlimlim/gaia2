import random
import torch
import torch.utils.data as data
from torchvision import datasets, transforms
from src.biased_data_partition import CustomizedTrainMNIST

# Helper functions
""" Dataset partitioning helper from https://seba-1511.github.io/tutorials/intermediate/dist_tuto.html"""
class Partition(object):
    def __init__(self, data, index):
        self.data = data
        self.index = index

    def __len__(self):
        return len(self.index)

    def __getitem__(self, index):
        data_idx = self.index[index]
        return self.data[data_idx]

class DataPartitioner(object):
    def __init__(self, data, sizes=[0.7, 0.2, 0.1], seed=1234):
        self.data = data
        self.partitions = []
        random.seed(seed)
        data_len = len(data)
        indexes = [x for x in range(0, data_len)]
        random.shuffle(indexes)

        for frac in sizes:
            part_len = int(frac * data_len)
            self.partitions.append(indexes[0:part_len])
            indexes = indexes[part_len:]

    def use(self, partition):
        return Partition(self.data, self.partitions[partition])

""" Partitioning MNIST adapted from https://seba-1511.github.io/tutorials/intermediate/dist_tuto.html"""
def partition_dataset(dataset, curr_node: int, no_of_nodes: int):
    partition_sizes = [1.0 / no_of_nodes for _ in range(no_of_nodes)]
    partition = DataPartitioner(dataset, partition_sizes)
    return torch.utils.data.DataLoader(
        partition.use(curr_node),
        batch_size=100,
        shuffle=True)

def build_dataset_loader(curr_node_ip_addr, other_nodes_ip_addrs, dataset='MNIST', dataset_dir='./data', batch_size=100, biased=False):
    dataset_ = {
        'MNIST': datasets.MNIST,
        'CIFAR10': datasets.CIFAR10
    }[dataset]
    transform = {
        'MNIST': transforms.ToTensor(),
        'CIFAR10': transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
    }[dataset]

    sorted_node_ip_addrs = sorted([curr_node_ip_addr] + other_nodes_ip_addrs)
    no_of_nodes = len(sorted_node_ip_addrs)
    self_idx = sorted_node_ip_addrs.index(curr_node_ip_addr)

    if biased:
        d = {
            0: 5400,
            1: 5400,
            2: 5400,
            3: 5400,
            4: 5400,
            5: 5400,
            6: 5400,
            7: 5400,
            8: 5400,
            9: 5400,
        }
        # list_of_dicts = partition_dict(no_of_nodes)
        list_of_dicts = [
            {
                0: 5400,
                1: 5400,
                2: 5400,
                3: 5400,
                4: 5400,
            },
            {
                2: 5400,
                3: 5400,
                4: 5400,
                5: 5400,
                6: 5400,
            },
            {
                5: 5400,
                6: 5400,
                7: 5400,
                8: 5400,
                9: 5400
            },
                
            ]
        case_1_a = CustomizedTrainMNIST('../data', label_to_num_examples=list_of_dicts[self_idx], train=True, download=True,
        transform=transforms.ToTensor())
        train_loader = torch.utils.data.DataLoader(case_1_a, batch_size=batch_size, shuffle=True)
    else:
        sorted_node_ip_addrs = sorted([curr_node_ip_addr] + other_nodes_ip_addrs)
        no_of_nodes = len(sorted_node_ip_addrs)
        train_dataset = dataset_(root=dataset_dir, train=True, transform=transform, download=True)
        # Equal partition of the data
        partition_sizes = [1.0 / no_of_nodes] * no_of_nodes
        partition = DataPartitioner(train_dataset, partition_sizes)
        train_loader = torch.utils.data.DataLoader(
            partition.use(self_idx),
            batch_size=batch_size,
            shuffle=True
        )

    test_dataset = dataset_(root=dataset_dir, train=False, transform=transform, download=True)
    test_loader = data.DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader

def partition_dict(no_of_nodes):
    d = {
            0: 5400,
            1: 5400,
            2: 5400,
            3: 5400,
            4: 5400,
            5: 5400,
            6: 5400,
            7: 5400,
            8: 5400,
            9: 5400,
    }
    if no_of_nodes > 10:
        return []
    else:
        partitioned_dicts = []
        partition_size = 10 // no_of_nodes
        j = 0
        for i in range(no_of_nodes - 1):
            partitioned_dicts.append(dict(list(d.items())[j:j+partition_size]))
            j += partition_size
        partitioned_dicts.append(dict(list(d.items())[j:10]))
        return partitioned_dicts



