def load_stat():
    loadavg = {}
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    loadavg['lavg_1']=con[0]
    loadavg['lavg_5']=con[1]
    loadavg['lavg_15']=con[2]
    loadavg['nr']=con[3]
    loadavg['last_pid']=con[4]
    return loadavg

def uptime_stat():
    uptime = {}
    f = open("/proc/uptime")
    con = f.read().split()
    f.close()
    all_sec = float(con[0])
    MINUTE,HOUR,DAY = 60,3600,86400
    uptime['day'] = int(all_sec / DAY )
    uptime['hour'] = int((all_sec % DAY) / HOUR)
    uptime['minute'] = int((all_sec % HOUR) / MINUTE)
    uptime['second'] = int(all_sec % MINUTE)
    uptime['Free rate'] = float(con[1]) / float(con[0])
    return uptime

def memory_stat():
    mem = {}
    f = open("/proc/meminfo")
    lines = f.readlines()
    f.close()
    for line in lines:
        if len(line) < 2: continue
        name = line.split(':')[0]
        var = line.split(':')[1].split()[0]
        mem[name] = round(float(var) / 1024.0, 2)
    mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
    return mem

def is_ip(address):
    import socket
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            if not isinstance(address, str):
                address = address.decode('utf8')
            inet_pton(family, address)
            return family
        except (TypeError, ValueError, OSError, IOError):
            pass
    return False

def inet_pton(family, addr):
    import socket
    addr = to_str(addr)
    if family == socket.AF_INET:
        return socket.inet_aton(addr)
    elif family == socket.AF_INET6:
        if '.' in addr:  # a v4 addr
            v4addr = addr[addr.rindex(':') + 1:]
            v4addr = socket.inet_aton(v4addr)
            v4addr = ['%02X' % ord(x) for x in v4addr]
            v4addr.insert(2, ':')
            newaddr = addr[:addr.rindex(':') + 1] + ''.join(v4addr)
            return inet_pton(family, newaddr)
        dbyts = [0] * 8  # 8 groups
        grps = addr.split(':')
        for i, v in enumerate(grps):
            if v:
                dbyts[i] = int(v, 16)
            else:
                for j, w in enumerate(grps[::-1]):
                    if w:
                        dbyts[7 - j] = int(w, 16)
                    else:
                        break
                break
        return b''.join((chr(i // 256) + chr(i % 256)) for i in dbyts)
    else:
        raise RuntimeError("What family?")

def to_str(s):
    if bytes != str:
        if isinstance(s, bytes):
            return s.decode('utf-8')
    return s
