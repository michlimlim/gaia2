import random
import torch
import torch.utils.data as data
from torchvision import datasets, transforms

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
def partition_dataset(dataset, curr_node, no_of_nodes=2):
    bsz = 128 / float(no_of_nodes) # Btw we divide the batch size by the number of nodes in order to maintain the overall batch size of 128. Fairer comparison.
    partition_sizes = [1.0 / no_of_nodes for _ in range(no_of_nodes)]
    partition = DataPartitioner(dataset, partition_sizes)
    return torch.utils.data.DataLoader(
        partition.use(curr_node),
        batch_size=int(bsz),
        shuffle=True)

def build_dataset_loader(curr_node, no_of_nodes = 2, dataset='MNIST', dataset_dir='./data', batch_size=100):
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
    
    train_dataset = dataset_(root=dataset_dir, train=True, transform=transform, download=True)
    train_loader = partition_dataset(train_dataset, curr_node, no_of_nodes)
    test_dataset = dataset_(root=dataset_dir, train=False, transform=transform, download=True)
    test_loader = data.DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader
