from src.util import ExtraFatal
from src.update_metadata.update_fairness_interface import UpdateMetadata, UpdateReceiverState
from src.update_metadata.model_update import ModelUpdate
from src.get_weights import get_weights

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
    def __init__(self, k, device_ip_addr_to_epoch_dict):
        self.k = k
        self.device_ip_addr_to_epoch_dict = device_ip_addr_to_epoch_dict
        self.epoch_no_to_num_devices = {}
        for epoch in device_ip_addr_to_epoch_dict.values():
            if epoch not in self.epoch_no_to_num_devices:
                self.epoch_no_to_num_devices[epoch] = 1
            else:
                self.epoch_no_to_num_devices[epoch] += 1
        self.max_epoch_num = max(device_ip_addr_to_epoch_dict.values())
        self.min_epoch_num = min(device_ip_addr_to_epoch_dict.values())

    def export_copy_of_internal_state_for_sending(self):
        return DeviceFairnessUpdateMetadata(self.device_ip_addr_to_epoch_dict).__dict__

    def export_copy_of_internal_state(self):
        return DeviceFairnessUpdateMetadata(self.k, self.device_ip_addr_to_epoch_dict)
    
    @staticmethod
    def fairness_for_one_vec(vector, thresh):
        return (max(vector) - min(vector)) < thresh

    # :param alphas [list[float]]
    # :param vectors [list[list[float]]]
    def fairness_fn(self, alphas, dicts, thresh):
        temp = {}
        for d, alpha in zip(dicts, alphas):
            for key, val in d.items():
                if key not in temp:
                    temp[key] = val * alpha
                else:
                    temp[key] += val * alpha
        return self.fairness_for_one_vec(temp.values(), thresh)

    # :param host_to_model_update [dict<str, ModelUpdate>] dict that maps host_ip to ModelUpdate
    # :returns 
    #    - alphas [array<float>]
    def get_alphas(self, metadata_list, weight_list):
        print("metaadata list", metadata_list)
        return get_weights(metadata_list)

    # :brief Checks if we can backprop. Relies only on internal state.
    def check_fairness_before_backprop(self) -> bool:
        return self.fairness_fn([1], [self.epoch_no_to_num_devices], self.k)

    # :brief For device fairness, it's always safe to aggregate.
    def check_fairness_before_aggregation(self, model_update: ModelUpdate) -> bool:
        return True

    def _update_min(self, device_ip_addr, epoch_num):
        # Decrement previous epoch_no's count
        # Increment new epoch_no's count
        prev_epoch_num = self.device_ip_addr_to_epoch_dict[device_ip_addr]
        self.epoch_no_to_num_devices[prev_epoch_num] -= 1
        if epoch_num not in self.epoch_no_to_num_devices:
            self.epoch_no_to_num_devices[epoch_num] = 1
        else:
            self.epoch_no_to_num_devices[epoch_num] += 1
        # Update min epoch num in current state if necessary
        if (
            (self.min_epoch_num == prev_epoch_num)
            and (self.epoch_no_to_num_devices[prev_epoch_num] == 0)
        ):
            for i in range(self.min_epoch_num + 1, self.max_epoch_num + 1):
                if self.epoch_no_to_num_devices[i] > 0:
                    self.min_epoch_num = i
                    break

    # :brief Update state for latest epoch_num for a given device
    # :param device_ip_addr [str] IP address of given device
    # :param epoch_num [int] latest epoch seen by device from device_ip_addr
    def _update_device_epoch(self, device_ip_addr, epoch_num):
        # Update max epoch number in current state
        if epoch_num > self.max_epoch_num:
            self.max_epoch_num = epoch_num

        # Update min epoch number in current state
        self._update_min(device_ip_addr, epoch_num)

        # Double check monotonocity
        if ((device_ip_addr in self.device_ip_addr_to_epoch_dict)
            and (self.device_ip_addr_to_epoch_dict[device_ip_addr] > epoch_num)):
            raise ExtraFatal(
                "epoch num should be monotonically increasing: incoming epoch {} \
                from {} vs. stored epoch {}".format(
                    epoch_num, 
                    device_ip_addr,
                    self.device_ip_addr_to_epoch_dict[device_ip_addr]
                ))
        # Overwrite newest epoch seen for the given device ip address
        self.device_ip_addr_to_epoch_dict[device_ip_addr] = epoch_num
        print(self.device_ip_addr_to_epoch_dict)

    def _update_internal_state_from_model_update_metadata(self, update_metadata: DeviceFairnessUpdateMetadata):
        for host_ip_addr, epoch_no in update_metadata.device_ip_addr_to_epoch_dict.items():
            if epoch_no > self.device_ip_addr_to_epoch_dict[host_ip_addr]:
                self._update_device_epoch(host_ip_addr, epoch_no)

    # :brief Updates our internal state after we perform backprop.
    #     We do this because we don't want to perform too much wasted work by rushing
    #     ahead and endlessly performing backprop even when we're in an unfair state (our updates dominate)
    def update_internal_state_after_backprop(self, device_ip_addr: str):
        epoch_num = self.device_ip_addr_to_epoch_dict[device_ip_addr]
        self._update_device_epoch(device_ip_addr, epoch_num + 1)

    # :param: host_to_model_update [dict<str, ModelUpdate>] host_ip map to ModelUpdate
    # :param: my_device_ip_addr [str] my own device ip address. this param allows us to treat
    #     our own update differently if we want to
    def update_internal_state_after_aggregation(self, alphas_for_each_update, metadata_list, host_id_list):
        new_metadata = {}
        for idx, _ in enumerate(host_id_list):
            alpha = alphas_for_each_update[idx]
            incoming_metadata = metadata_list[idx]
            print(incoming_metadata, 'incoming')
            for key, val in incoming_metadata.items():
                if key not in new_metadata:
                    new_metadata[key] = alpha * val
                else:
                    new_metadata[key] += alpha * val
        self.device_ip_addr_to_epoch_dict = new_metadata

    # brief: Calculate the weight we give to each host's updates.
    # param: host_to_model_update [dict<str, ModelUpdate>] dict that maps host_ip to ModelUpdate
    # returns: host_to_weight [dict<str, float>] dict that maps host_ip to weight for host's update
    def calculate_weights_for_each_host(self, host_to_model_update):
        equal_weight = 1.0 / float(len(host_to_model_update))
        host_to_weight = {}
        # Host-oblivious: Doesn't matter who the update is from
        for sender_host_ip_addr, _ in host_to_model_update.items():
            host_to_weight[sender_host_ip_addr] = equal_weight
        return host_to_weight
