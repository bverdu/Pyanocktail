# -*- coding: utf-8 -*-
#!/usr/bin/python2
'''
Created on 11 oct. 2013

@author: Bertrand Verdu - bertrand.verdu@gmail.com

I2c service - Raspberry_Pi specific - in charge of i2c communication
Courtesy Adafruit project
'''
from __future__ import division
import time
import math
import smbus
import sys

MCP23017_IODIRA = 0x00
MCP23017_IODIRB = 0x01
MCP23017_GPIOA = 0x12
MCP23017_GPIOB = 0x13
MCP23017_GPPUA = 0x0C
MCP23017_GPPUB = 0x0D
MCP23017_OLATA = 0x14
MCP23017_OLATB = 0x15
MCP23008_GPIOA = 0x09
MCP23008_GPPUA = 0x06
MCP23008_OLATA = 0x0A


class Internal_functions(object):

    @staticmethod
    def sampleGen(duration):
        '''
        simple generator for variable speed tests
        divide the total time by 4, send first 30% of speed, then 60%, then 100%, then 50%
        '''
        yield 0.3, duration / 4
        yield 0.6, duration / 4
        yield 1, duration / 4
        yield 0.5, duration / 4


def switchcontrol(control, on=0, debug=False):
    '''
    Pianocktail fonction to open or close given pump
   control is a list containing:
                         type (gpio,pwm,fake_gpio,fake_pwm),
                          i2c bus address, 
                          channel number, 
                          speed ratio.
    '''
    init_gpio = []
    init_pwm = []
    gpio_ctrl = []
    pwm_ctrl = []
    if debug:
        print(str(control) + ' on=' + str(on))
        print('switchcontrol type %s requested for pump %s' %
              (control[0], control[2]))
    try:
        if control[0] == 'pwm':
            try:
                idx = init_pwm.index(control[1])
            except ValueError:
                pwm_ctrl.append(Rpi_PWM(address=control[1], debug=debug))
                init_pwm.append(control[1])
                idx = len(init_pwm) - 1
                pwm_ctrl[idx].setPWMFreq(60)
            if on == 1:
                pwm_ctrl[idx].setPWM(control[2], int(control[3] * 1024.0), 0)
            else:
                pwm_ctrl[idx].setPWM(control[2], 0, 0)

        if control[0] == 'gpio':
            try:
                idx = init_gpio.index(control[1])
            except ValueError:
                gpio_ctrl.append(Rpi_MCP230XX(
                    address=control[1], num_gpios=16))
                init_gpio.append(control[1])
                idx = len(init_gpio) - 1
            if on == 1:
                gpio_ctrl[idx].config(control[2], gpio_ctrl[idx].OUTPUT)
                gpio_ctrl[idx].output(control[2], 1)
            else:
                gpio_ctrl[idx].config(control[2], gpio_ctrl[idx].OUTPUT)
                gpio_ctrl[idx].output(control[2], 0)
    except Exception as err:
        print(str(err))
        raise


def playRecipe(ingredients_list, qty=1, debug=False):
    '''
    Pianocktail fonction to serve given list of ingredients
    Each ingredient is a sub-list containing:
                         type (gpio,pwm,fake_gpio,fake_pwm),
                          i2c bus address, 
                          channel number, 
                          duration,
                          speed,
                          variable speed function.
    '''
    init_gpio = []
    init_pwm = []
    gpio_ctrl = []
    pwm_ctrl = []
#     ingredients_list=[]
#     if prelist != None:
#         ingredients_list = prelist
#     ingredients_list = ingredients_list + ing_list
#     if postlist != None:
#         ingredients_list = ingredients_list + postlist
    for ingredient in ingredients_list:
        if ingredient[0] == 'gpio':
            try:
                idx = init_gpio.index(ingredient[1])
            except ValueError:
                gpio_ctrl.append(Rpi_MCP230XX(
                    address=ingredient[1], num_gpios=16))
                init_gpio.append(ingredient[1])
                idx = len(init_gpio) - 1
            gpio_ctrl[idx].config(ingredient[2], gpio_ctrl[idx].OUTPUT)
            gpio_ctrl[idx].output(ingredient[2], 1)
            time.sleep(ingredient[3] * float(qty))
            gpio_ctrl[idx].output(ingredient[2], 0)

        elif ingredient[0] == 'pwm':
            try:
                idx = init_pwm.index(ingredient[1])
            except ValueError:
                pwm_ctrl.append(Rpi_PWM(address=ingredient[1], debug=debug))
                init_pwm.append(ingredient[1])
                idx = len(init_pwm) - 1
                pwm_ctrl[idx].setPWMFreq(60)
            if ingredient[5] not in ('None', ''):
                try:
                    fct = getattr(Internal_functions, ingredient[5])
                    res = fct(ingredient[3])
                    for ratio, duration in res:
                        pwm_ctrl[idx].setPWM(ingredient[2], int(
                            ratio * ingredient[4] * 1024.0), 0)
                        time.sleep(duration * float(qty))
                except Exception as e:
                    print(str(e))
                    pwm_ctrl[idx].setPWM(
                        ingredient[2], int(ingredient[4] * 1024.0), 0)
                    time.sleep(ingredient[3] * float(qty))
            else:
                pwm_ctrl[idx].setPWM(
                    ingredient[2], int(ingredient[4] * 1024.0), 0)
                time.sleep(ingredient[3] * float(qty))
            pwm_ctrl[idx].setPWM(ingredient[2], 0, 0)

        elif ingredient[0] == 'stepper':
            '''
            stepper command
            '''
            try:
                idx = init_gpio.index(ingredient[1])
            except ValueError:
                gpio_ctrl.append(Rpi_MCP230XX(
                    address=ingredient[1], num_gpios=16))
                init_gpio.append(ingredient[1])
                idx = len(init_gpio) - 1
            addresses = ingredient[2]
            stepper = Stepper(addresses, gpio_ctrl[idx])
            if ingredient[3] < 0:
                stepper.backward(-int(ingredient[3] * 1000.0))
            else:
                stepper.forward(int(ingredient[3] * 1000.0))
            for address in addresses:
                gpio_ctrl[idx].output(address, 0)

        elif ingredient[0] == 'motor':
            '''
            continuous motor
            '''
            try:
                idx = init_gpio.index(ingredient[1][1])
            except ValueError:
                gpio_ctrl.append(Rpi_MCP230XX(
                    address=ingredient[1][1], num_gpios=16))
                init_gpio.append(ingredient[1][1])
                idx = len(init_gpio) - 1
            addresses = ingredient[2]
            motor = Motor(addresses[1:], gpio_ctrl[idx])
            speed = abs(ingredient[4])
            try:
                idx = init_pwm.index(ingredient[1][0])
            except ValueError:
                pwm_ctrl.append(Rpi_PWM(address=ingredient[1][0], debug=debug))
                init_pwm.append(ingredient[1][0])
                idx = len(init_pwm) - 1
                pwm_ctrl[idx].setPWMFreq(60)
            if ingredient[5] not in ('None', ''):
                try:
                    fct = getattr(Internal_functions, ingredient[5])
                    res = fct(float(abs(ingredient[3])))
                    for ratio, duration in res:
                        print("duration = %f" % duration)
                        pwm_ctrl[idx].setPWM(addresses[0], int(
                            ratio * ingredient[4] * 1024.0), 0)
                        if ingredient[3] < 0:
                            motor.backward()
                        else:
                            motor.forward()
                        time.sleep(duration)
                except Exception as e:
                    print(str(e))
                    pwm_ctrl[idx].setPWM(
                        addresses[0], int(ingredient[4] * 1024.0), 0)
                    if float(ingredient[3]) < 0:
                        motor.backward()
                    else:
                        motor.forward()
                    time.sleep(float(abs(ingredient[3])))
            else:
                pwm_ctrl[idx].setPWM(addresses[0], int(speed * 1024.0), 0)
                if ingredient[3] < 0:
                    motor.backward()
                else:
                    motor.forward()
                time.sleep(float(abs(ingredient[3])))
            motor.stop()


class Rpi_Exception(Exception):
    '''
    Custom exception
    '''

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class Fake_bus(object):

    def __init__(self):
        print("Fake bus initialized")

    def __getattr__(self, attr):
        #         print('getattr: %s' % attr)
        return lambda *args: print(" - ".join([str(arg) for arg in args]))


class Rpi_I2C(object):

    @staticmethod
    def getPiRevision():
        '''Gets the version number of the Raspberry Pi board
        Courtesy quick2wire-python-api
        https://github.com/quick2wire/quick2wire-python-api
        '''
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Revision'):
                        return int(line.rstrip()[-1])
        except:
            return 0

    @staticmethod
    def getPiI2CBusNumber():
        # Gets the I2C bus number /dev/i2c#
        if Rpi_I2C.getPiRevision():
            return 1 if Rpi_I2C.getPiRevision() > 1 else 0
        return 0

    def __init__(self, address, busnum=-1, debug=False, fake=False):
        self.address = address
    # By default, the correct I2C bus is auto-detected using /proc/cpuinfo
    # Alternatively, you can hard-code the bus version below:
    # self.bus = smbus.SMBus(0); # Force I2C0 (early 256MB Pi's)
    # self.bus = smbus.SMBus(1); # Force I2C1 (512MB Pi's)
        if not fake:
            self.bus = smbus.SMBus(
                busnum if busnum >= 0 else Rpi_I2C.getPiI2CBusNumber())
        else:
            self.bus = Fake_bus()
        self.debug = debug

    def reverseByteOrder(self, data):
        "Reverses the byte order of an int (16-bit) or long (32-bit) value"
        # Courtesy Vishal Sapre
        byteCount = len(hex(data)[2:].replace('L', '')[::2])
        val = 0
        for i in range(byteCount):
            val = (val << 8) | (data & 0xff)
            data >>= 8
        return val

    def errMsg(self):
        print("Error accessing 0x%02X: Check your I2C address" % self.address)
        return -1

    def write8(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        try:
            self.bus.write_byte_data(self.address, reg, value)
            if self.debug:
                print("I2C: Wrote 0x%02X to register 0x%02X" % (value, reg))
        except IOError:
            return self.errMsg()

    def write16(self, reg, value):
        "Writes a 16-bit value to the specified register/address pair"
        try:
            self.bus.write_word_data(self.address, reg, value)
            if self.debug:
                print("I2C: Wrote 0x%02X to register pair 0x%02X,0x%02X" %
                      (value, reg, reg + 1))
        except IOError:
            return self.errMsg()

    def writeList(self, reg, lst):
        "Writes an array of bytes using I2C format"
        try:
            if self.debug:
                print("I2C: Writing list to register 0x%02X:" % reg)
                print(list)
                self.bus.write_i2c_block_data(self.address, reg, lst)
        except IOError:
            return self.errMsg()

    def readList(self, reg, length):
        "Read a list of bytes from the I2C device"
        try:
            results = self.bus.read_i2c_block_data(self.address, reg, length)
            if self.debug:
                print("I2C: Device 0x%02X returned the following from reg 0x%02X" %
                      (self.address, reg))
                print(results)
            return results
        except IOError:
            return self.errMsg()

    def readU8(self, reg):
        "Read an unsigned byte from the I2C device"
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if self.debug:
                print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" %
                      (self.address, result & 0xFF, reg))
            return result
        except IOError:
            return self.errMsg()

    def readS8(self, reg):
        "Reads a signed byte from the I2C device"
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if result > 127:
                result -= 256
            if self.debug:
                print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" %
                      (self.address, result & 0xFF, reg))
            return result
        except IOError:
            return self.errMsg()

    def readU16(self, reg):
        "Reads an unsigned 16-bit value from the I2C device"
        try:
            result = self.bus.read_word_data(self.address, reg)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" %
                      (self.address, result & 0xFFFF, reg))
            return result
        except IOError:
            return self.errMsg()

    def readS16(self, reg):
        "Reads a signed 16-bit value from the I2C device"
        try:
            result = self.bus.read_word_data(self.address, reg)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" %
                      (self.address, result & 0xFFFF, reg))
            return result
        except IOError:
            return self.errMsg()


class Rpi_MCP230XX(object):
    OUTPUT = 0
    INPUT = 1

    def __init__(self, address, num_gpios):
        self.fake = False

        assert num_gpios >= 0 and num_gpios <= 16, "Number of GPIOs must be between 0 and 16"
        try:
            self.i2c = Rpi_I2C(address=address)
        except:
            self.fake = True
            self.i2c = Rpi_I2C(address=address, fake=True)
        else:
            self.num_gpios = num_gpios
            # set defaults
            if num_gpios <= 8:
                # all inputs on port A
                self.i2c.write8(MCP23017_IODIRA, 0xFF)
                self.direction = self.i2c.readU8(MCP23017_IODIRA)
                self.i2c.write8(MCP23008_GPPUA, 0x00)
            elif num_gpios > 8 and num_gpios <= 16:
                # all inputs on port A
                self.i2c.write8(MCP23017_IODIRA, 0xFF)
                # all inputs on port B
                self.i2c.write8(MCP23017_IODIRB, 0xFF)
                self.direction = self.i2c.readU8(MCP23017_IODIRA)
                self.direction |= self.i2c.readU8(MCP23017_IODIRB) << 8
                self.i2c.write8(MCP23017_GPPUA, 0x00)
                self.i2c.write8(MCP23017_GPPUB, 0x00)
        self.address = address

    def _changebit(self, bitmap, bit, value):
        assert value == 1 or value == 0, "Value is %s must be 1 or 0" % value
        if value == 0:
            return bitmap & ~(1 << bit)
        elif value == 1:
            return bitmap | (1 << bit)

    def _readandchangepin(self, port, pin, value, currvalue=None):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
            pin, self.num_gpios)
        #assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        if not currvalue:
            currvalue = self.i2c.readU8(port)
        newvalue = self._changebit(currvalue, pin, value)
        self.i2c.write8(port, newvalue)
        return newvalue

    def pullup(self, pin, value):
        if self.num_gpios <= 8:
            return self._readandchangepin(MCP23008_GPPUA, pin, value)
        if self.num_gpios <= 16:
            self._readandchangepin(MCP23017_GPPUA, pin, value)
            if (pin < 8):
                return
            else:
                return self._readandchangepin(MCP23017_GPPUB, pin - 8, value) << 8

    # Set pin to either input or output mode
    def config(self, pin, mode):
        if self.fake:
            print("GPIO Controller 0X%02X config mode pin n° %d to %d" %
                  (self.address, pin, mode))
        else:
            if self.num_gpios <= 8:
                self.direction = self._readandchangepin(
                    MCP23017_IODIRA, pin, mode)
            if self.num_gpios <= 16:
                if (pin < 8):
                    self.direction = self._readandchangepin(
                        MCP23017_IODIRA, pin, mode)
                else:
                    self.direction |= self._readandchangepin(
                        MCP23017_IODIRB, pin - 8, mode) << 8
            return self.direction

    def output(self, pin, value):
        if self.fake:
            print("GPIO Controller 0X%02X sent data %d to pin n° %d" %
                  (self.address, value, pin))
        else:
            # assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
            if self.num_gpios <= 8:
                self.outputvalue = self._readandchangepin(
                    MCP23008_GPIOA, pin, value, self.i2c.readU8(MCP23008_OLATA))
            if self.num_gpios <= 16:
                if (pin < 8):
                    self.outputvalue = self._readandchangepin(
                        MCP23017_GPIOA, pin, value, self.i2c.readU8(MCP23017_OLATA))
                else:
                    self.outputvalue = self._readandchangepin(
                        MCP23017_GPIOB, pin - 8, value, self.i2c.readU8(MCP23017_OLATB)) << 8
            return self.outputvalue
#
#
#             self.outputvalue = self._readandchangepin(MCP23017_IODIRA, pin, value, self.outputvalue)
#             return self.outputvalue

    def input(self, pin):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
            pin, self.num_gpios)
        assert self.direction & (
            1 << pin) != 0, "Pin %s not set to input" % pin
        if self.num_gpios <= 8:
            value = self.i2c.readU8(MCP23008_GPIOA)
        elif self.num_gpios > 8 and self.num_gpios <= 16:
            value = self.i2c.readU8(MCP23017_GPIOA)
            value |= self.i2c.readU8(MCP23017_GPIOB) << 8
        return value & (1 << pin)

    def readU8(self):
        result = self.i2c.readU8(MCP23008_OLATA)
        return(result)

    def readS8(self):
        result = self.i2c.readU8(MCP23008_OLATA)
        if (result > 127):
            result -= 256
        return result

    def readU16(self):
        assert self.num_gpios >= 16, "16bits required"
        lo = self.i2c.readU8(MCP23017_OLATA)
        hi = self.i2c.readU8(MCP23017_OLATB)
        return((hi << 8) | lo)

    def readS16(self):
        assert self.num_gpios >= 16, "16bits required"
        lo = self.i2c.readU8(MCP23017_OLATA)
        hi = self.i2c.readU8(MCP23017_OLATB)
        if (hi > 127):
            hi -= 256
        return((hi << 8) | lo)

    def write8(self, value):
        self.i2c.write8(MCP23008_OLATA, value)

    def write16(self, value):
        assert self.num_gpios >= 16, "16bits required"
        self.i2c.write8(MCP23017_OLATA, value & 0xFF)
        self.i2c.write8(MCP23017_OLATB, (value >> 8) & 0xFF)

# RPi.GPIO compatible interface for MCP23017 and MCP23008


class Rpi_GPIO(object):
    OUT = 0
    IN = 1
    BCM = 0
    BOARD = 0

    def __init__(self, busnum, address, num_gpios):
        self.chip = Rpi_MCP230XX(busnum, address, num_gpios)

    def setmode(self, mode):
        # do nothing
        pass

    def setup(self, pin, mode):
        self.chip.config(pin, mode)

    def input(self, pin):
        return self.chip.input(pin)

    def output(self, pin, value):
        self.chip.output(pin, value)

    def pullup(self, pin, value):
        self.chip.pullup(pin, value)


class Rpi_PWM(object):
    i2c = None

    # Registers/etc.
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.debug = debug
        self.fake = False
        try:
            self.i2c = Rpi_I2C(address)
        except FileNotFoundError:
            self.fake = True
            self.i2c = Rpi_I2C(address, fake=True)
        if (self.debug):
            print("Reseting PCA9685 %s" % ",Fake Mode" if self.fake else "")
        if self.i2c.write8(self.__MODE1, 0x00) != None:
            raise Rpi_Exception(
                "Unable to write init sequence for PCA9685 at address 0x%02XX" % address)
        self.address = address

    def setPWMFreq(self, freq):
        if self.fake:
            print("Set PWM controller 0X%02X to frequency %d" %
                  (self.address, freq))
        else:
            "Set the PWM frequency"
            prescaleval = 25000000.0  # 25MHz
            prescaleval /= 4096.0  # 12-bit
            prescaleval /= float(freq)
            prescaleval -= 1.0
            if (self.debug):
                print("Setting PWM frequency to %d Hz" % freq)
                print("Estimated pre-scale: %d" % prescaleval)
            prescale = int(math.floor(prescaleval + 0.5))
            if (self.debug):
                print("Final pre-scale: %d" % prescale)
            oldmode = self.i2c.readU8(self.__MODE1)
            newmode = (oldmode & 0x7F) | 0x10  # sleep
            self.i2c.write8(self.__MODE1, newmode)  # go to sleep
            self.i2c.write8(self.__PRESCALE, prescale)
            self.i2c.write8(self.__MODE1, oldmode)
            time.sleep(0.005)
            self.i2c.write8(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        if self.fake:
            print("Set PWM controller 0X%02X channel n°%d to value %d" %
                  (self.address, channel, on))
        else:
            "Sets a single PWM channel"
            self.i2c.write8(self.__LED0_ON_L + 4 * channel, on & 0xFF)
            self.i2c.write8(self.__LED0_ON_H + 4 * channel, on >> 8)
            self.i2c.write8(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
            self.i2c.write8(self.__LED0_OFF_H + 4 * channel, off >> 8)


class Stepper(object):

    motorA = 2
    motorB = 1
    power = False

    def __init__(self, addresses, bus, fake=False):
        self.fake = fake
        self.addresses = addresses
        self.bus = bus
        for addr in addresses:
            bus.config(addr, bus.OUTPUT)
            bus.output(addr, 0)

    def __del__(self):
        for addr in self.addresses:
            self.bus.output(addr, 0)
        self.power = False

    def _move(self, speed):
        if self.power == False:
            self.bus.output(self.addresses[0], 1)
            self.bus.output(self.addresses[1], 1)
            self.power = True
        if self.motorA == 2:
            self.bus.output(self.addresses[2], 1)
            self.bus.output(self.addresses[3], 0)
        else:
            self.bus.output(self.addresses[2], 0)
            self.bus.output(self.addresses[3], 1)
        if self.motorB == 2:
            self.bus.output(self.addresses[4], 1)
            self.bus.output(self.addresses[5], 0)
        else:
            self.bus.output(self.addresses[4], 0)
            self.bus.output(self.addresses[5], 1)
        time.sleep(speed)

    def backward(self, steps, speed=0.0):
        if self.fake:
            print("Stepper backward for %d steps at %f speed, only one will be simulated for logs sanity..." % (
                steps, speed))
            pol = self.motorA + self.motorB
            if pol == 4:
                self.motorA = 1
            elif pol == 2:
                self.motorA = 2
            elif pol == 3:
                if self.motorA == 1:
                    self.motorB = 1
                else:
                    self.motorB = 2
            self._move(speed)
        else:
            for i in range(steps):
                pol = self.motorA + self.motorB
                if pol == 4:
                    self.motorA = 1
                elif pol == 2:
                    self.motorA = 2
                elif pol == 3:
                    if self.motorA == 1:
                        self.motorB = 1
                    else:
                        self.motorB = 2
                self._move(speed)
    # for addr in self.addresses:
      # self.bus.output(addr, 0)
    # self.power = False

    def forward(self, steps, speed=0.0):
        if self.fake:
            print("Stepper forward for %d steps at %f speed, only one will be simulated for logs sanity..." % (
                steps, speed))
            pol = self.motorA + self.motorB
            if pol == 4:
                self.motorB = 1
            elif pol == 2:
                self.motorB = 2
            elif pol == 3:
                if self.motorA == 1:
                    self.motorA = 2
                else:
                    self.motorA = 1
            self._move(speed)
        else:
            for i in range(steps):
                pol = self.motorA + self.motorB
                if pol == 4:
                    self.motorB = 1
                elif pol == 2:
                    self.motorB = 2
                elif pol == 3:
                    if self.motorA == 1:
                        self.motorA = 2
                    else:
                        self.motorA = 1
                self._move(speed)


class Motor(object):

    power = False

    def __init__(self, addresses, bus):
        self.addresses = addresses
        self.a = addresses[0]
        self.b = addresses[1]
        self.bus = bus

    def __del__(self):
        for addr in self.addresses:
            self.bus.output(addr, 0)
        self.power = False

    def _move(self, sens):
        if self.power == False:
            for addr in self.addresses:
                self.bus.config(addr, self.bus.OUTPUT)

        if sens >= 0:
            self.bus.output(self.a, sens)
            self.bus.output(self.b, 0)
        else:
            self.bus.output(self.a, 0)
            self.bus.output(self.b, 1)

    def backward(self):
        if self.fake:
            print("Motor backward")
        self._move(-1)

    def forward(self):
        if self.fake:
            print("Motor forward")
        self._move(1)

    def stop(self):
        if self.fake:
            print("Motor stop")
        self._move(0)


if __name__ == '__main__':
    print("Fake test first:")
    print("Send Recipe to fake GPIO and PWM controllers")
    recipe = [['fake_gpio', 0x20, 0, 2.1, 0, ''], [
        'fake_pwm', 0x40, 1, 2.3, 1.0, sampleGen]]
    playRecipe(recipe, debug=True)
    print('Fake test finished')
    print('hardware tests:')
    try:
        bus = Rpi_I2C(address=0, debug=True)
    except Exception as err:
        print('no valid i2c controller found')
        print(err.message)
        sys.exit(0)
    try:
        mcp = Rpi_MCP230XX(address=0x20, num_gpios=16)
        print('gpio controller found at 0x%02X' % 0x20)
        hasgpio = True
    except:
        hasgpio = False
        print('no GPIO i2c controller')
    try:
        pwm = Rpi_PWM(debug=True)
        haspwm = True
        print('PWM controller found at 0X%02X' % 0X40)
    except Exception as err:
        haspwm = False
        print('no valid PWM controller found')
        print(str(err))

    if hasgpio:

        # Set pins 0, 1 and 2 to output (you can set pins 0..15 this way)
        mcp.config(0, mcp.OUTPUT)
        mcp.config(1, mcp.OUTPUT)

        print("Starting blinking  on i2c GPIO pin 0 & 1 (CTRL+C to quit)")
        while (True):
            try:
                mcp.output(0, 1)  # Pin 0 High
                time.sleep(0.5)
                mcp.output(1, 1)  # Pin 1 High
                time.sleep(0.5)
                mcp.output(0, 0)  # Pin 0 Low
                time.sleep(0.5)
                mcp.output(1, 0)  # Pin 1 Low
            except KeyboardInterrupt:
                mcp.output(0, 0)
                mcp.output(1, 0)
                break
    if haspwm:
        print("Starting i2c PWM test (CTRL+C to quit)")
        pwm.setPWMFreq(60)
        while (True):
            try:
                pwm.setPWM(0, 0, 0)
                time.sleep(1)
                pwm.setPWM(0, 1000, 0)
                time.sleep(1)
                pwm.setPWM(0, 2000, 0)
                time.sleep(1)
                pwm.setPWM(0, 3000, 0)
                time.sleep(1)
                pwm.setPWM(0, 4096, 0)
                time.sleep(1)
            except KeyboardInterrupt:
                pwm.setPWM(0, 0, 0)
                break
