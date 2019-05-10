from unit.unit import TestCalculator
from torchvision import transforms
from torch.utils.data import DataLoader
from src.biased_data_partition import CustomizedTrainMNIST

def test_biased_data_partition(calc):
    def compare_dicts(calc, d, expected_d):
        for key, val in expected_d.items():
            calc.check(d[key] == val)
            del d[key]
        calc.check(len(d) == 0)

    d_1 = {
        0: 1000,
        1: 2000,
        2: 3000,
        3: 4000
    }
    calc.context("test biased data partitioning")
    case_1_a = CustomizedTrainMNIST('../data', label_to_num_examples=d_1, train=True, download=True,
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ]))
    test_1_dataloader = DataLoader(case_1_a, batch_size=1, shuffle=True)
    d = {}
    for _, label in test_1_dataloader:
        label = label.item()
        if label not in d:
            d[label] = 1
        else:
            d[label] += 1
    compare_dicts(calc, d, d_1)
    test_2_dataloader = DataLoader(case_1_a, batch_size=64, shuffle=True)
    d = {}
    for _, labels in test_2_dataloader:
        for label in labels:
            label = label.item()
            if label not in d:
                d[label] = 1
            else:
                d[label] += 1
    compare_dicts(calc, d, d_1)

def add_tests(calc):
    calc.add_test(test_biased_data_partition)

