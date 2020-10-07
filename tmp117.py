from typing import List

import smbus


ADDRESS = 0x48
CONFIG_REG = 0x01
TEMPERATURE_REG = 0x00
# https://github.com/NilsMinor/TMP117-Arduino/blob/fe96c9caa5d876ca75da6f2e85b77a0498ffd7fb/src/TMP117.h#L48
TMP117_RESOLUTION = 0.0078125


class TMP117:

    def __init__(self, address: int = ADDRESS, busnum: int = 1):
        self.address = address
        self.bus = smbus.SMBus(busnum)
        self.read_temperature()

    def bytes_to_temp(self, data: List[bytes]) -> float:
        # https://github.com/NilsMinor/TMP117-Arduino/blob/fe96c9caa5d876ca75da6f2e85b77a0498ffd7fb/src/TMP117.cpp#L331
        return ((data[0] << 8) | data[1]) * TMP117_RESOLUTION

    def read_temperature(self) -> float:
        # read two bytes from address, register
        data = self.bus.read_i2c_block_data(
            i2c_addr=self.address,
            register=TEMPERATURE_REG,
            length=2
        )
        return self.bytes_to_temp(data)
