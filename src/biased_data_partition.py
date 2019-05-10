import numpy as np
import warnings
from torchvision import datasets
from torch.utils.data.dataset import Dataset
from PIL import Image

class CustomizedTrainMNIST(Dataset):
    # This was derived from counting the MNIST dataset.
    # Limiting factor is that there are only 5421 examples of digit 5
    # in the MNIST train dataset
    MAX_NUM_EXAMPLES_PER_CLASS = 5400
    def __init__(self, *args, **kwargs):
        # Don't override method if TEST dataset. Only override if TRAIN.
        if 'train' in kwargs and kwargs['train'] is False:
            super().__init__(*args, **kwargs)
        if 'label_to_num_examples' in kwargs:
            label_to_num_examples = kwargs.pop('label_to_num_examples')
        if 'transform' in kwargs:
            self.transform = kwargs['transform']
        else:
            self.transform = None
        if 'target_transform' in kwargs:
            self.target_transform = kwargs['target_transform']
        else:
            self.target_transform = None
        self._mnist_dataset = datasets.MNIST(*args, **kwargs)
        (self.data, self.targets) = self._trim_train_data(label_to_num_examples)

    # :param label_to_num_examples [dict<int, int>] Maps data label to number of examples desired
    # :brief Creates a dataset with num_examples of each label, subject to MAX_NUM_EXAMPLES_PER_CLASS
    def _trim_train_data(self, label_to_num_examples):
        label_indexes = {}
        for i in range(self._mnist_dataset.__len__()):
            example = self._mnist_dataset.__getitem__(i)
            label = example[1]
            if label in label_to_num_examples:
                if label not in label_indexes:
                    label_indexes[label] = [i]
                else:
                    label_indexes[label].append(i)
        index_set = []
        for label, num_examples in label_to_num_examples.items():
            num_examples = min(num_examples, CustomizedTrainMNIST.MAX_NUM_EXAMPLES_PER_CLASS)
            index_set.extend(label_indexes[label][:num_examples])
        new_dataset = [self._mnist_dataset.data[i] for i in index_set]
        new_targets = [self._mnist_dataset.targets[i] for i in index_set]
        return new_dataset, new_targets

    def __getitem__(self, index):
        img = self.data[index]
        target = int(self.targets[index])
        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.fromarray(img.numpy(), mode='L')
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return (img, target)

    def __len__(self):
        return len(self.data)
