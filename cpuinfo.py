
import re
import time

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
"""
       /proc/uptime
              This file contains two numbers (values in seconds): the
              uptime of the system (including time spent in suspend) and
              the amount of time spent in the idle process.

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/deployment_guide/s2-proc-uptime

       /proc/stat
           idle   (4) Time spent in the idle task.  This value
                      should be USER_HZ times the second entry in
                      the /proc/uptime pseudo-file.
>>> #idle = user_hz * idletime
>>> #user_hz=idle/idletime
"""
_debug = 1

def get_times():
    try:
        with open('/proc/uptime') as upt:
            line = upt.readline()
            t = line.split()
            uptime, idletime = (float(x.strip()) for x in t) #idletime: sum of all cores
    except ValueError as e:
            print(f'error reading from {upt.name} | {line} | {e}')
    return uptime, idletime

def get_info():
    with open('/proc/cpuinfo') as cpuinfo:
        for line in cpuinfo:
            if line.startswith('cpu cores'):
                cores = int(line.split()[3].strip())
                return cores
        else:
            raise Exception(f'error reading {cpuinfo.name}: no core? :-D')

def get_cpu():
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
                #_v = line.split()[1:5]
                #user, nice, system, idle = (float(x.strip()) for x in _v)
                #break
    if not _cpu_s:
        raise Exception('error reading {stats.name}: no cpu info? :-(')
    return _cpu_s

if __name__ == '__main__':
    cores = get_info()
    t0 = time.time()
    cpu_s = get_cpu()
    uptime, idletime = get_times()

    main_c = list(c for c in cpu_s if c.main)[0]
    USER_HZ = main_c.idle/idletime
    main_c_sec = CpuStat(*(v/USER_HZ for v in main_c.times)) #(user,nice,system,idle)))
    main_c_sec.main = True

    #_debug = 0
    if _debug:
        print(f'* uptime: {uptime:.2f} | idletime: {idletime:.2f} \
| uptime (day): {uptime/86400:.2f} | USER_HZ: {USER_HZ:.2f}')
        for c in cpu_s:
            print(f'* {c.name}: {c.user:.2f}, {c.nice:.2f}, {c.system:.2f}, {c.idle:.2f}')
        # in seconds:
        print(f'* cpu_main (seconds): {list(f"{i:.2f}" for i in main_c_sec.times)}')
        print("* tot(s) ~ uptime: {:.2f} ~ {:.2f}".format(sum(main_c_sec.times)/cores, uptime))

    for c in cpu_s:
        print("* {}: {:.2f}%".format(c.name, ((c.total_time-c.idle)*100)/c.total_time), c)

    try:
        cpu_s = get_cpu()
        _fmt = f'{{:<{1+max(len(c.name) for c in cpu_s)}}}' + ' {:.2f}%'
        while True:
            print('*'*30)
            old_cpu_s = cpu_s[:]
            cpu_s = []
            time.sleep(0.5)
            cpu_s = get_cpu()
            for oc, c in zip(old_cpu_s, cpu_s):
                assert c.name == oc.name
                assert c.__hash__() != oc.__hash__()
                ###change...
                #new = c.total_time - c.idle
                #old = oc.total_time - oc.idle
                #old_p = ((c.total_time-c.idle)*100)/c.total_time
                #change_p = ((new / old) * 100) - 100
                #print("{}: {:.6f}%".format(c.name, old_p+change_p))
                print(_fmt.format(f'{c.name}:', (((c.total_time - oc.total_time) - (c.idle - oc.idle))*100)/(c.total_time - oc.total_time)))
                #print("{:<3} {:.2f}%".format(f'{c.name}:', (((c.total_time - oc.total_time) - (c.idle - oc.idle))*100)/(c.total_time - oc.total_time)))
                #  +###((c.total_time-c.idle)*100)/c.total_time
                #except ZeroDivisionError as e:print(c.name, "ERRRRRR:", (c.total_time - oc.total_time), (c.idle - oc.idle))
    except KeyboardInterrupt:
        print('exiting...')
    except ZeroDivisionError as e:
        print(f'{e}\n>{c}\n>{oc}')
        
            
    #print("cpu: {:.6f}%".format(((sum(main_c_sec.times)-main_c_sec.idle)*100)/sum(main_c_sec.times)))
    #print("cpu: {:.6f}%".format(((sum(main_c_sec.times)-idletime)*100)/sum(main_c_sec.times))) # test, ok

"""
>>> st
(439199.97, 1920.4, 111925.4, 6254916.91)
>>> #x : uso = 100 : tot => x = (uso * 100) / tot
>>> ((sum(st)-st[-1])*100)/sum(st)
8.123513538414397
"""
