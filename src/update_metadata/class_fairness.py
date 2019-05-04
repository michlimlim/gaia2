class ClassFairnessMetadata(object):
    # :brief Store metadata for an update needed to guarantee class-based fairness
    # :param num_classes [int] total no. of classes
    # :param class_id_to_num_examples_dict [dict<int, int>] maps class id to no. of examples in class
    def __init__(self, num_classes, class_id_to_num_examples_dict):
        self.num_classes = num_classes
        self.class_id_to_num_examples_dict = class_id_to_num_examples_dict