#!/usr/bin/python
"""
written by Mikhail Doronin
licensed as GPLv3
"""

from datetime import time
from datetime import datetime
from math import modf
from numbers import Number
from time import sleep
from functools import reduce

import pyvisa as visa

from instruments.instrument import Instrument

import logging
log = logging.getLogger(__name__)

class PX100(Instrument):

    # Reading values
    ISON = 0x10
    VOLTAGE = 0x11
    CURRENT = 0x12
    TIME = 0x13
    CAP_AH = 0x14
    CAP_WH = 0x15
    TEMP = 0x16
    LIM_CURR = 0x17
    LIM_VOLT = 0x18
    TIMER = 0x19

    # Command values
    OUTPUT = 0x01
    SETCURR = 0x02
    SETVCUT = 0x03
    SETTMR = 0x04
    RESETCNT = 0x05
    # Unknown beyond this point, no response from device

    ENABLED = 0x0100
    DISABLED = 0x0000

    MUL = {
        ISON: 1,
        VOLTAGE: 1000.,
        CURRENT: 1000.,
        CAP_AH: 1000.,
        CAP_WH: 1000.,
        TEMP: 1,
        LIM_CURR: 100.,
        LIM_VOLT: 100.,
    }

    KEY_CMDS = {
        'is_on': ISON,
        'voltage': VOLTAGE,
        'current': CURRENT,
        'time': TIME,
        'cap_ah': CAP_AH,
        'cap_wh': CAP_WH,
        'temp': TEMP,
        'set_current': LIM_CURR,
        'set_voltage': LIM_VOLT,
        'set_timer': TIMER,
    }

    FREQ_VALS = [
        'is_on',
        'voltage',
        'current',
        'time',
        'cap_ah',
    ]

    AUX_VALS = [
        'cap_wh',
        'temp',
        'set_current',
        'set_voltage',
        'set_timer',
    ]

    COMMANDS = {
        Instrument.COMMAND_ENABLE: OUTPUT,
        Instrument.COMMAND_SET_VOLTAGE: SETVCUT,
        Instrument.COMMAND_SET_CURRENT: SETCURR,
        Instrument.COMMAND_SET_TIMER: SETTMR,
        Instrument.COMMAND_RESET: RESETCNT,
    }

    VERIFY_CMD = {
        Instrument.COMMAND_ENABLE: 'is_on',
        Instrument.COMMAND_SET_VOLTAGE: 'set_voltage',
        Instrument.COMMAND_SET_CURRENT: 'set_current',
        Instrument.COMMAND_SET_TIMER: 'set_timer',
        Instrument.COMMAND_RESET: 'cap_ah',
    }

    RESET_WH = 'RESET_WH'
    RESET_AH = 'RESET_AH'
    RESET_DURATION = 'RESET_DURATION'
    RESET_ALL = 'RESET_ALL'
    BACKLIGHT_TIME = 'BACKLIGHT_TIME'
    SET_PRICE = 'SET_PRICE'
    SETUP_OR_LEFT_BUTTON = 'SETUP_OR_LEFT_BUTTON'
    ENTER_BUTTON = 'ENTER_BUTTON'
    PLUS_BUTTON = 'PLUS_BUTTON'
    MINUS_BUTTON = 'MINUS_BUTTON'

    STANDARD_COMMANDS = {
        RESET_WH: 0x01,
        RESET_AH: 0x02,
        RESET_DURATION: 0x03,
        'NO-OP': 0x04,
        RESET_ALL: 0x05,
        'NO-OP': 0x11,
        'NO-OP': 0x12,
        BACKLIGHT_TIME: 0x21,
        SET_PRICE: 0x22,
        SETUP_OR_LEFT_BUTTON: 0x31,
        ENTER_BUTTON: 0x32,
        PLUS_BUTTON: 0x33,
        MINUS_BUTTON: 0x34,

    }

    # Max wattage to avoid cutoff of 185W on a 180W DL24P
    MAX_WATTS = 170.0

    def __init__(self, device):
        log.debug(f"DEVICE: {device}")
        self.device = device
        self.name = "PX100" # TODO remove hard coding and switch on different profiles of device
        self.aux_index = 0
        self.data = {
            'is_on': 0.,
            'voltage': 0.,
            'current': 0.,
            'time': time(0),
            'cap_ah': 0.,
            'cap_wh': 0.,
            'temp': 0,
            'set_current': 0.,
            'set_voltage': 0.,
            'set_timer': time(0),
        }

    def probe(self):
        log.debug("probe")
        if not isinstance(self.device, visa.resources.SerialInstrument):
            return False

        self.port = self.device.resource_name.split('::')[0].replace('ASRL', '')
        self.__setup_device()
        self.__clear_device()

        return self.__is_number(self.getVal(PX100.VOLTAGE))

    def readAll(self, read_all_aux=False):
        log.debug("readAll")
        self.__clear_device()
        self.update_vals(PX100.FREQ_VALS)

        if read_all_aux:
            self.update_vals(PX100.AUX_VALS)
        else:
            self.update_val(PX100.AUX_VALS[self.__next_aux()])

        self.data["ts"] = datetime.now()
        self.data["watts"] = self.data["current"] * self.data["voltage"]
        self.data["voltage_cutoff"] = self.data["set_voltage"]
        return self.data

    def update_vals(self, keys):
        for key in keys:
            self.update_val(key)

    def update_val(self, key):
        value = self.getVal(PX100.KEY_CMDS[key])
        if (value is not False):
            self.data[key] = value

    def command(self, command, value):
        log.info(f"COMMAND: {command}, VALUE: {value}")
        if command not in (PX100.COMMANDS.keys()):
            return False

        for _i in range(0, 3):
            self.setVal(PX100.COMMANDS[command], value)
            sleep(0.5)
            self.update_val(PX100.VERIFY_CMD[command])
            if self.data[PX100.VERIFY_CMD[command]] == value:
                break
            log.debug("retry " + command)
            log.debug(self.data[PX100.VERIFY_CMD[command]])
            log.debug(value)
            sleep(0.7)

        if (command == Instrument.COMMAND_RESET):
            self.update_vals(PX100.AUX_VALS)

    def getVal(self, command):
        ret = self.writeFunction(command, [0, 0])
        if (not ret or len(ret) == 0):
            log.debug("no answer")
            return False
        elif (len(ret) == 1 and ret[0] == 0x6F):
            log.debug("setval")
            return False
        elif (len(ret) < 7 or ret[0] != 0xCA or ret[1] != 0xCB
              or ret[5] != 0xCE or ret[6] != 0xCF):
            log.debug("Receive error")
            return False

        try:
            mult = PX100.MUL[command]
        except:
            mult = 1000.

        if (command == PX100.TIME or command == PX100.TIMER):
            hh = ret[2]
            mm = ret[3]
            ss = ret[4]
            return time(hh, mm, ss)  #'{:02d}:{:02d}:{:02d}'.format(hh, mm, ss)
        else:
            return int.from_bytes(ret[2:5], byteorder='big') / mult

    def setVal(self, command, value):
        log.info(f"SET_VALUE COMMAND: {command}, VALUE: {value}")
        if isinstance(value, float):
            f, i = modf(value)
            value = [int(i), round(f * 100)]
        elif isinstance(value, time):
            value = (value.second + value.minute * 60 +
                     value.hour * 3600).to_bytes(2, byteorder='big')
        elif (command == PX100.OUTPUT and value):
            value = [0x01, 0x00]
        else:
            value = value.to_bytes(2, byteorder='big')
        log.info(f"SET_VALUE COMMAND: {command}, VALUE: {value}")
        ret = self.writeFunction(command, value)
        log.info(f"SET_VALUE response: {ret}")
        return ret == 0x6F


    def checksum(self, frame):
        return reduce(lambda x, y: (x & 255) + y, frame[2:]) ^ 68

    def writeFunction(self, command, value):
        if command >= 0x10:
            resp_len = 7
        else:
            resp_len = 1

        # TODO: final frame should be the checksum
        frame = bytearray([0xB1, 0xB2, command, *value, 0xB6])
        try:
            self.device.write_raw(frame)
            return self.device.read_bytes(resp_len)
        except Exception as inst:
            log.debug(type(inst))    # the exception instance
            log.debug(inst.args)     # arguments stored in .args
            log.debug(inst)
            log.debug("error reading bytes")
            return False


    def raw_writer(self, b_array):
        if b_array[2] >= 0x10:
            resp_len = 7
        else:
            resp_len = 4
        self.device.write_raw(b_array)
        return self.device.read_bytes(resp_len)

    def turnOn(self):
        log.debug("turnon")
        self.setVal(PX100.OUTPUT, PX100.ENABLED)

    def turnOff(self):
        self.turnOFF()

    def turnOFF(self):
        log.debug("turnoff")
        self.setVal(PX100.OUTPUT, PX100.DISABLED)

    def close(self):
        sleep(.2)
        self.device.close()

    def __setup_device(self):
        try:
            self.device.timeout = 500
            self.device.baud_rate = 9600
            self.device.data_bits = 8
            self.device.stop_bits = visa.constants.StopBits.one
            self.device.parity = visa.constants.Parity.none
            self.device.flow_control = visa.constants.ControlFlow.none
        except:
            pass

    def __clear_device(self):
        try:
            self.device.read_bytes(self.device.bytes_in_buffer)
        except Exception as inst:
            log.debug(type(inst))    # the exception instance
            log.debug(inst.args)     # arguments stored in .args
            log.debug(inst)
            log.debug("error reading bytes")
            self.device.close
            return False

    def __next_aux(self):
        self.aux_index += 1
        if self.aux_index >= len(PX100.AUX_VALS):
            self.aux_index = 0
        return self.aux_index

    def __is_number(self, value):
        return isinstance(value, Number) and not isinstance(value, bool)

    #####
    # Commands
    #####
    def reset_wh(self):
        return self.execute(self.RESET_WH)

    def reset_ah(self):
        return self.execute(self.RESET_AH)

    def reset_duration(self):
        return self.execute(self.RESET_DURATION)

    def reset_all(self):
        return self.execute(self.RESET_ALL)

    def set_cutoff_voltage(self, value):
        self.setVal(self.COMMANDS[Instrument.COMMAND_SET_VOLTAGE], value)

    def set_constant_current(self, value):
        self.setVal(self.COMMANDS[Instrument.COMMAND_SET_CURRENT], value)

    def set_timer(self, value):
        self.setVal(self.COMMANDS[Instrument.COMMAND_SET_TIMER], value)

    def set_watts(self, value):
        # Check current watts
        # If not enabled, return false
        data = self.get_readings()
        if value > self.MAX_WATTS:
            value = self.MAX_WATTS
        if data['is_on'] != 1:
            return False

        # Call multiple times to narrow in on the value even after voltage sag
        self._watt_setter(value)
        self._watt_setter(value)
        return self._watt_setter(value)

    def _watt_setter(self, desired_watts):
        data = self.get_readings()
        wattage = round(data['watts'])
        volt = data['voltage']

        if wattage == desired_watts:
            return round(data['watts'], 3)
        else:
            desired_amps = round(desired_watts / volt, 3)
            log.info(f"Desired amps: {desired_amps}")
            self.set_constant_current(desired_amps)
            sleep(1)
            new_watts = round(self.get_readings()['watts'], 3)

            return new_watts


    def maintain_constant_power(self, watts):
        cont = True
        # Set watts returns false if no load test running
        while cont:
            cont = self.set_watts(watts)
            sleep(1)

    def get_internal_resistance_milli_ohm(self, max_amps = 2.0):
        # 7.10.2 of ISO 69951-2 2003 Defines internal resistance measurement
        # Source: https://www.accu-select.de/KUNDEN-DOWNLOAD/Akku-Norm%20EN%2069951-2/EN61951-2Y2003_1f.pdf
        # It is most useful when measured multiple times on same pack through its lifetime
        # and indicates when a pack is near EOL
        # Procedure is essentially 2 step DC amp application followed by v measurements
        # - Low voltage for 10s
        # increasing by duration_padding to allow for settings change timing
        # Setting current and reading voltage is repeated to ensure the values are active values because
        # during testing the values were not updating accurately
        DURATION_PADDING = 3
        I1 = max_amps / 10
        I2 = max_amps
        self.enable()
        sleep(3)
        self.set_constant_current(I1)
        self.set_constant_current(I1)
        self.set_constant_current(I1)
        sleep(10 + DURATION_PADDING)
        _ = self.readAll(True)['voltage']
        _ = self.readAll(True)['voltage']
        U1 = self.readAll(True)['voltage']
        self.set_constant_current(I2)
        self.set_constant_current(I2)
        self.set_constant_current(I2)
        # Note should be 3s
        sleep(5 + DURATION_PADDING)
        _ = self.readAll(True)['voltage']
        _ = self.readAll(True)['voltage']
        U2 = self.readAll(True)['voltage']
        self.disable()
        R_DC = round((U1 - U2) / (I2 - I1) * 1000, 2) # for mOhm
        return {R_DC, 'mOhm'}


    def push_setup_or_left_button(self):
        return self.execute(self.SETUP_OR_LEFT_BUTTON)

    def push_enter_on_off_button(self):
        return self.execute(self.ENTER_BUTTON)

    def enable(self):
        self.turnOn()

    def disable(self):
        self.turnOff()

    def enable_load(self):
        return self.turnOn()

    def disable_load(self):
        return self.turnOff()

    def push_plus_button(self):
        return self.execute(self.PLUS_BUTTON)

    def push_minus_button(self):
        return self.execute(self.MINUS_BUTTON)

    def get_readings(self):
        return self.readAll(read_all_aux=True)

    def execute(self, command, *values):
        return self.raw_writer(self.command_frame(self.STANDARD_COMMANDS[command], *values))

    def command_frame(self, command_int, *values):
        padded_values = [0x00, 0x00, 0x00, 0x00]
        for i, v in enumerate(values):
            padded_values[i] = v
        frame = [0xff, 0x55, 0x11, 0x02, command_int, *padded_values]
        frame.append(self.checksum(frame))
        return bytearray(frame)
