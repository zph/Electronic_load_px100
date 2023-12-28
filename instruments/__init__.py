#!/usr/bin/python

import pyvisa as visa

from instruments import px100

import logging

log = logging.getLogger(__name__)

class Instruments:
    def __init__(self):
        self.rm = visa.ResourceManager('@py')
        self.instruments = []
        self.discover()

    def list(self):
        return self.instruments

    def instr(self):
        if self.instruments:
            return self.instruments[0]

    def discover(self):
        log.debug("Detecting instruments...")
        for i in self.rm.list_resources():
            log.debug(i)
            try:
                inst = self.rm.open_resource(i)
            except:
                log.debug("err opening instrument")
                continue

            if not isinstance(inst, visa.resources.Resource):
                continue

            try:
                driver = px100.PX100(inst)  #Todo: loop over drivers if multiple
                if driver.probe():
                    self.instruments.append(driver)
                    log.debug("found " + driver.name)
                else:
                    log.debug("ko")
            except Exception as inst:
                log.debug(type(inst))  # the exception instance
                log.debug(inst.args)  # arguments stored in .args
                log.debug(inst)
                log.debug("err")
                try:
                    inst.close()
                except Exception as inst:
                    log.debug(type(inst))  # the exception instance
                    log.debug(inst.args)  # arguments stored in .args
                    log.debug(inst)
                    log.debug("no close")

        else:
            if len(self.instruments) == 0:
                log.debug("No instruments found")
