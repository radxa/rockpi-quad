#!/usr/bin/env python3
import os.path
import time
import traceback
import threading

import gpiod

import misc

GPIOD_V2 = hasattr(gpiod, 'LineSettings')


class Pwm:
    def __init__(self, chip, fun):
        self.period_value = None
        try:
            int(chip)
            chip = f'pwmchip{chip}'
        except ValueError:
            pass
        self.filepath = f"/sys/class/pwm/{chip}/pwm{fun}/"
        try:
            with open(f"/sys/class/pwm/{chip}/export", 'w') as f:
                f.write(fun)
        except OSError:
            print("Warning: init pwm error")
            traceback.print_exc()

    def period(self, ns: int):
        self.period_value = ns
        with open(os.path.join(self.filepath, 'period'), 'w') as f:
            f.write(str(ns))

    def period_us(self, us: int):
        self.period(us * 1000)

    def enable(self, t: bool):
        if (polarity := os.environ.get('POLARITY')) is not None:
            with open(os.path.join(self.filepath, 'polarity'), 'w') as f:
                f.write(polarity)

        with open(os.path.join(self.filepath, 'enable'), 'w') as f:
            f.write(f"{int(t)}")

    def write(self, duty: float):
        assert self.period_value, "The Period is not set."
        with open(os.path.join(self.filepath, 'duty_cycle'), 'w') as f:
            f.write(f"{int(self.period_value * duty)}")


class Gpio:

    def tr(self):
        while True:
            self.set_value(1)
            time.sleep(self.value[0])
            self.set_value(0)
            time.sleep(self.value[1])

    def __init__(self, period_s):
        self.line_offset = int(os.environ['FAN_LINE'])
        if GPIOD_V2:
            self.chip = gpiod.Chip(misc.gpiochip_path(os.environ['FAN_CHIP']))
            settings = gpiod.LineSettings(direction=gpiod.line.Direction.OUTPUT)
            self.request = self.chip.request_lines(
                config={self.line_offset: settings},
                consumer='fan',
                output_values={self.line_offset: gpiod.line.Value.INACTIVE},
            )
        else:
            self.chip = gpiod.Chip(os.environ['FAN_CHIP'])
            self.line = self.chip.get_line(self.line_offset)
            self.line.request(consumer='fan', type=gpiod.LINE_REQ_DIR_OUT)
        self.value = [period_s / 2, period_s / 2]
        self.period_s = period_s
        self.thread = threading.Thread(target=self.tr, daemon=True)
        self.thread.start()

    def set_value(self, value):
        if GPIOD_V2:
            active = gpiod.line.Value.ACTIVE if value else gpiod.line.Value.INACTIVE
            self.request.set_value(self.line_offset, active)
        else:
            self.line.set_value(value)

    def write(self, duty):
        self.value[1] = duty * self.period_s
        self.value[0] = self.period_s - self.value[1]


def read_temp():
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        t = int(f.read().strip()) / 1000.0
    return t


def get_dc(cache={}):
    if misc.conf['run'].value == 0:
        return 0.999

    if time.time() - cache.get('time', 0) > 60:
        cache['time'] = time.time()
        cache['dc'] = misc.fan_temp2dc(read_temp())

    return cache['dc']


def change_dc(dc, cache={}):
    if dc != cache.get('dc'):
        cache['dc'] = dc
        for pin in pins:
            pin.write(dc)


def running():
    global pins

    if os.environ['HARDWARE_PWM'] == '1':
        chip = os.environ['PWMCHIP']
        pins = [Pwm(chip, fun) for fun in os.environ.get('PWM_FUN', '0').split(',')]
        for pin in pins:
            pin.period_us(40)
            pin.enable(True)
    else:
        pins = [Gpio(0.025)]
    while True:
        change_dc(get_dc())
        time.sleep(1)


if __name__ == '__main__':
    running()
