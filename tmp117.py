import smbus

ADDRESS = 0x48
CONFIG_REG = 0x01
TEMPERATURE_REG = 0x00


class TMP117:

    def __init__(self, address: int = 0x48, busnum: int = 1):
        self.address = address
        self.bus = smbus.SMBus(busnum)
        self.read_temperature()

    def extract_config(self, num: int, location: int, length: int) -> bytes:
        data = self.bus.read_i2c_block_data(self.address, CONFIG_REG, 2)
        if (num == 3):
            #Full register dump
            return data
        else:
            mask = 2**length - 1
            return (data[num] >> location) & mask

    def bytes_to_temp(self, data: bytes) -> float:
        # Adjustment for extended mode
        ext = self.extract_config(1, 4, 1)
        #ext = data[1] & 0x01
        res = int((data[0] << (4+ext)) + (data[1] >> (4-ext)))

        if (data[0] | 0x7F is 0xFF):
            # Perform 2's complement operation (x = x-2^bits)
            res = res - 4096*(2**ext)
        # Outputs temperature in degC
        return res*0.0625

    def read_temperature(self) -> float:
        data = self.bus.read_i2c_block_data(self.address, TEMPERATURE_REG, 2)
        return self.bytes_to_temp(data)
