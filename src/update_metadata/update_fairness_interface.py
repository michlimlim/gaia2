from src.util import ExtraFatal
from src.update_metadata.model_update import ModelUpdate

class UpdateMetadata(object):
    pass

class UpdateReceiverState(object):
    # :param my_device_ip_addr [str] Device ip address of the host calling this fn
    def check_fairness_before_backprop(self, my_device_ip_addr: str):
        raise ExtraFatal("Must implement this method")

    def check_fairness_before_aggregation(self, model_update: ModelUpdate):
        raise ExtraFatal("Must implement this method")

    # :param ip_addr [str]
    # :param model_update [ModelUpdate]
    def update_internal_state_after_backprop(self, device_ip_addr: str):
        raise ExtraFatal("Must implement this method")

    # :param ip_addr [str]
    # :param model_update [ModelUpdate]
    def update_internal_state_before_aggregation(self, device_ip_addr: str, model_update: ModelUpdate):
        raise ExtraFatal("Must implement this method")

    # :brief call this fn after each aggregation attempt
    # :return array<float> weight for each incoming update
    def calculate_weights_for_each_update(self):
        raise ExtraFatal("Must implement this method")

    # :brief call this fn when you want to send a model update
    # :return [UpdateMetadata]
    def export_copy_of_internal_state_for_sending(self) -> UpdateMetadata:
        raise ExtraFatal("Must implement this method")

    def export_copy_of_internal_state(self) -> UpdateMetadata:
        raise ExtraFatal("Must implement this method")
