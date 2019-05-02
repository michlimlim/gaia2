from src.util import ExtraFatal
from src.update_metadata.update_fairness_interface import UpdateMetadata, UpdateReceiverState
from src.update_metadata.model_update import ModelUpdate

class DeviceFairnessUpdateMetadata(UpdateMetadata):
    # :brief Store metadata for an update to guarantee device-based fairness
    # :param device_ip_addr_to_epoch_dict [dict<str, int>] maps device id to
    #   latest epoch seen by that device
    def __init__(self, device_ip_addr_to_epoch_dict):
        self.device_ip_addr_to_epoch_dict = device_ip_addr_to_epoch_dict

class DeviceFairnessReceiverState(UpdateReceiverState):
    # :brief Stores receiver state required to guarantee device-based fairness
    # :param k [int] max diff allowed between latest epoch no. seen by any device
    #   versus earliest epoch no. seen by any device
    # :param num_devices [int] total no. of devices in network
    # :param device_ip_addr_to_epoch_dict [dict<str, int>] maps device id to
    #   latest epoch seen by that device
    def __init__(self, k, num_devices, device_ip_addr_to_epoch_dict):
        self.k = k
        self.num_devices = num_devices
        self.device_ip_addr_to_epoch_dict = device_ip_addr_to_epoch_dict
        (
            self.max_epoch_device_ip_addr,
            self.max_epoch_num
        ) = max(device_ip_addr_to_epoch_dict.items(), key=lambda tup: tup[1])
        (
            self.min_epoch_device_ip_addr,
            self.min_epoch_num
        ) = min(device_ip_addr_to_epoch_dict.items(), key=lambda tup: tup[1])

    def export_copy_of_internal_state_for_sending(self):
        return DeviceFairnessUpdateMetadata(self.device_ip_addr_to_epoch_dict).__dict__

    # :brief Checks if we can backprop. Relies only on internal state.
    def check_fairness_before_backprop(self) -> bool:
        return (self.max_epoch_num - self.min_epoch_num) < self.k

    # :brief For device fairness, it's always safe to aggregate.
    def check_fairness_before_aggregation(self, model_update: ModelUpdate) -> bool:
        return True

    # :brief Update state for latest epoch_num for a given device
    # :param device_ip_addr [str] IP address of given device
    # :param epoch_num [int] latest epoch seen by device from device_ip_addr
    def _update_device_epoch(self, device_ip_addr, epoch_num):
        if epoch_num > self.max_epoch_num:
            self.max_epoch_num = epoch_num
            self.max_epoch_device_ip_addr = device_ip_addr
        if epoch_num < self.min_epoch_num:
            self.min_epoch_num = epoch_num
            self.min_epoch_device_ip_addr = device_ip_addr
        if ((device_ip_addr in self.device_ip_addr_to_epoch_dict)
            and (self.device_ip_addr_to_epoch_dict[device_ip_addr] > epoch_num)):
            raise ExtraFatal(
                "epoch num should be monotonically increasing: incoming epoch {} \
                from {} vs. stored epoch {}".format(
                    epoch_num, 
                    device_ip_addr,
                    self.device_ip_addr_to_epoch_dict[device_ip_addr]
                ))
        self.device_ip_addr_to_epoch_dict[device_ip_addr] = epoch_num
        print(self.device_ip_addr_to_epoch_dict)

    def _update_internal_state_from_model_update(self, device_ip_addr: str, model_update: ModelUpdate):
        if device_ip_addr in model_update.update_metadata.device_ip_addr_to_epoch_dict:
            epoch_num = model_update.update_metadata.device_ip_addr_to_epoch_dict[device_ip_addr]
            print(model_update.update_metadata.device_ip_addr_to_epoch_dict)
            print(epoch_num)
            self._update_device_epoch(device_ip_addr, epoch_num)
            print(self.device_ip_addr_to_epoch_dict)
        else:
            raise ExtraFatal('device_ip_addr not found')

    def update_internal_state_after_backprop(self, device_ip_addr: str):
        epoch_num = self.device_ip_addr_to_epoch_dict[device_ip_addr]
        self._update_device_epoch(device_ip_addr, epoch_num + 1)

    def update_internal_state_after_aggregation(self, device_ip_addr: str, model_update: ModelUpdate):
        self._update_internal_state_from_model_update(device_ip_addr, model_update)

    # brief: Given a dict that maps a host to its ModelUpdate object,
    #   calculate the weight we give to each host's updates.
    # param: host_to_model_update [dict<str, ModelUpdate>] host_ip map to ModelUpdate
    # returns: host_to_weight [dict<str, float>] host_ip map to weight for host's update
    # side_effect: updates internal state to track bias
    def calculate_weights_for_each_host(self, host_to_model_update):
        equal_weight = 1.0 / float(len(host_to_model_update))
        host_to_weight = {}
        # Host-oblivious: Doesn't matter who the update is from
        for sender_host_ip_addr, model_update in host_to_model_update.items():
            host_to_weight[sender_host_ip_addr] = equal_weight
            df_metadata = DeviceFairnessUpdateMetadata(**(model_update.update_metadata))
            for host_ip_addr, epoch_no in df_metadata.device_ip_addr_to_epoch_dict.items():
                if epoch_no > self.device_ip_addr_to_epoch_dict[host_ip_addr]:
                    self._update_device_epoch(host_ip_addr, epoch_no)
        return host_to_weight
