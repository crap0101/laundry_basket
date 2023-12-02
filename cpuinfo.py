#!/usr/bin/env python3
#
# author: Marco Chieppa | crap0101
#

import argparse
import re
import sys
import time

STDERR = sys.stderr

class CpuStat:
    def __init__ (self, user, nice, system, idle):
        self.user, self.nice, self.system, self.idle = user, nice, system, idle
        self.main = False
        self.number = None
    def __str__ (self):
        return '{}({}, {}, {}, {})'.format(
            self.__class__.__name__, self.user, self.nice, self.system, self.idle)
    @property
    def name (self):
        return f'cpu_{"main" if self.main else self.number}'
    @property
    def times (self):
        return (self.user, self.nice, self.system, self.idle)
    @property
    def total_time (self):
        return self.user + self.nice + self.system + self.idle

def get_times():
    try:
        with open('/proc/uptime') as upt:
            line = upt.readline()
            t = line.split()
            # NOTE: idletime: sum of all cores
            uptime, idletime = (float(x.strip()) for x in t)
    except ValueError as e:
            print(f'error reading from {upt.name} | {line} | {e}', file=STDERR)
    return uptime, idletime

def get_info():
    with open('/proc/cpuinfo') as cpuinfo:
        for line in cpuinfo:
            if line.startswith('cpu cores'):
                cores = int(line.split()[3].strip())
                return cores
        else:
            raise Exception(f'error reading {cpuinfo.name}: no core? :-D')

def get_cpu(only_main=False):
    _cpu_s = []
    with open('/proc/stat') as stats:
        for line in stats:
            match = re.match('^cpu(\d+)?\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
            if match:
                groups = match.groups()
                p = CpuStat(*map(float, groups[1:]))
                if groups[0] is None:
                    p.main = True
                else:
                    p.number = int(groups[0])
                _cpu_s.append(p)
    if not _cpu_s:
        raise Exception('error reading {stats.name}: no cpu info? :-(')
    if only_main:
        return list(c for c in _cpu_s if c.main)
    return _cpu_s

def get_parsed():
    p = argparse.ArgumentParser()
    p.add_argument('-e', '--extra',
                   dest='extra_info', action='store_true',
                   help='(mainly for debug: Show some extra informations.')
    p.add_argument('-m', '--only-main',
                   dest='only_main', action='store_true',
                   help='Show the main cpu only.')
    p.add_argument('-s', '--sleep',
                   dest='sleep', type=float, default=0.5,
                   help='''sleep time (in seconds) between checks.
                   Must be a positive float or integer.
                   Default: %(default)s .''')
    p.add_argument('-r', '--repeat',
                   dest='repeat', type=int, default=None,
                   help='''A positive integer representing the maximum number
                   of iterations. Default: run forever.''')
    return p, p.parse_args()


if __name__ == '__main__':
    parser, parsed = get_parsed()
    if parsed.sleep <= 0:
        parser.error('sleep time must be > 0')
    else:
        sleep_time = parsed.sleep
    if parsed.repeat == None:
        repeat = float('+inf')
    elif parsed.repeat <= 0:
        parser.error('iterations number must be > 0')
    else:
        repeat = parsed.repeat
    only_main = parsed.only_main
    
    cores = get_info()
    cpu_s = get_cpu(only_main)
    uptime, idletime = get_times()

    main_c = list(c for c in cpu_s if c.main)[0]
    USER_HZ = main_c.idle / idletime
    main_c_sec = CpuStat(*(v/USER_HZ for v in main_c.times))
    main_c_sec.main = True

    if parsed.extra_info:
        print(f'* uptime: {uptime:.2f} | idletime: {idletime:.2f} '
              f'| uptime (day): {uptime/86400:.2f} | USER_HZ: {USER_HZ:.2f}')
        for c in cpu_s:
            print(f'* {c.name}: {c.user:.2f}, {c.nice:.2f}, '
                  f'{c.system:.2f}, {c.idle:.2f}')
        # in seconds:
        print(f'* cpu_main (seconds): '
              f'{list(f"{i:.2f}" for i in main_c_sec.times)}')
        print("* tot(s) ~ uptime: {:.2f} ~ {:.2f}".format(
            sum(main_c_sec.times) / cores, uptime))
        for c in cpu_s:
            print("* {}: {:.2f}%".format(
                c.name, ((c.total_time - c.idle) * 100) / c.total_time), c)
        print("#"*30)

    try:
        cpu_s = get_cpu(only_main)
        _fmt = f'{{:<{1+max(len(c.name) for c in cpu_s)}}}' + ' {:.2f}%'
        while repeat > 0:
            old_cpu_s = cpu_s[:]
            cpu_s = []
            time.sleep(sleep_time)
            cpu_s = get_cpu(only_main)
            for oc, c in zip(old_cpu_s, cpu_s):
                #change...
                if parsed.extra_info:
                    new = c.total_time - c.idle
                    old = oc.total_time - oc.idle
                    old_p = ((c.total_time - c.idle) * 100) / c.total_time
                    change_p = ((new / old) * 100) - 100
                    print("* change: {}: {:.6f}%".format(c.name, old_p+change_p))
                print(_fmt.format(
                    f'{c.name}:',
                    (((c.total_time - oc.total_time) - (c.idle - oc.idle))
                     * 100)
                    / (c.total_time - oc.total_time)))
            repeat -= 1
            if repeat > 0:
                print('*'*30)
    except KeyboardInterrupt:
        print('>>> exiting...', file=STDERR)
    except ZeroDivisionError as e:
        print(f'{e}\n>{c}\n>{oc}', file=STDERR)
