from src.util import ExtraFatal

class DeviceFairnessGradientMetadata(object):
    # :brief Store metadata for an update to guarantee device-based fairness
    # :param num_devices [int] total no. of devices 
    # :param device_ip_addr_to_epoch_dict [dict<str, int>] maps device id to
    #   latest epoch seen by that device
    def __init__(self, num_devices, device_ip_addr_to_epoch_dict):
        self.num_devices = num_devices
        self.device_ip_addr_to_epoch_dict = device_ip_addr_to_epoch_dict

class DeviceFairnessReceiverState(object):
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

    # :brief Checks if we can calculate gradients
    def check_device_fairness(self) -> bool:
        return (self.max_epoch_num - self.min_epoch_num) < self.k

    # :brief Update state for latest epoch_num for a given device
    # :param device_ip_addr [str] IP address of given device
    # :param epoch_num [int] latest epoch seen by device from device_ip_addr
    def update_device_fairness(self, device_ip_addr, epoch_num):
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
