import bme280
import smbus2

bme280_port = 1
bme280_address = 0x76
bme280_bus = smbus2.SMBus(bme280_port)
calibration_params = bme280.load_calibration_params(bme280_bus, bme280_address)


def bme280_temperature() -> float:
    data = bme280.sample(bme280_bus, bme280_address, calibration_params)
    return data.temperature

