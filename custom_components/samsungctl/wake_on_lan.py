# -*- coding: utf-8 -*-
from __future__ import print_function
import ctypes
import socket
import struct
import sys
import platform


PY2 = sys.version_info[0] == 2

if platform.system() == 'Darwin':
    OSX = True
    LINUX = False
    WINDOWS = False
elif platform.system() == 'Windows':
    OSX = False
    LINUX = False
    WINDOWS = True
else:
    OSX = False
    LINUX = True
    WINDOWS = False


def get_mac_address(ip):
    if not PY2 and isinstance(ip, bytes):
        ip = str(ip, 'utf-8')

    if WINDOWS:
        try:
            SendARP = ctypes.windll.Iphlpapi.SendARP
        except AttributeError:
            return None

        try:
            inet_addr = ctypes.windll.wsock32.inet_addr(ip)
            if inet_addr in (0, -1):
                raise ValueError
        except:
            host_ip = socket.gethostbyname(ip)
            inet_addr = ctypes.windll.wsock32.inet_addr(host_ip)

        buf = ctypes.c_buffer(6)
        add_len = ctypes.c_ulong(ctypes.sizeof(buf))
        if SendARP(inet_addr, 0, ctypes.byref(buf), ctypes.byref(add_len)) != 0:
            raise ctypes.WinError()

        # Convert binary data into a string.
        mac_addr = ''
        for int_val in struct.unpack('BBBBBB', buf):
            if int_val > 15:
                replace_str = '0x'
            else:
                replace_str = 'x'
            mac_addr = ''.join(
                [mac_addr, hex(int_val).replace(replace_str, '')]
            )
        mac = ':'.join(
            mac_addr[i:i + 2] for i in range(0, len(mac_addr), 2)
        ).upper()

    else:
        import os
        import re
        import shlex
        from subprocess import check_output

        mac_re_colon = r'([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})'

        def _popen(command, args):
            path = os.environ.get('PATH', os.defpath).split(os.pathsep)
            path.extend(('/sbin', '/usr/sbin'))

            for directory in path:
                executable = os.path.join(directory, command)
                if (
                    os.path.exists(executable) and
                    os.access(executable, os.F_OK | os.X_OK) and
                    not os.path.isdir(executable)
                ):
                    break
            else:
                executable = command

            return _call_proc(executable, args)

        def _call_proc(executable, args):
            cmd = [executable] + shlex.split(args)
            env = dict(os.environ)
            env['LC_ALL'] = 'C'  # Ensure ASCII output so we parse correctly

            if PY2:
                devnull = open(os.devnull, 'wb')
            else:
                import subprocess
                devnull = subprocess.DEVNULL

            output = check_output(cmd, stderr=devnull, env=env)

            if PY2:
                return str(output)
            elif isinstance(output, bytes):
                return str(output, 'utf-8')

        def _uuid_ip():
            from uuid import _arp_getnode

            _gethostbyname = socket.gethostbyname
            try:
                socket.gethostbyname = lambda x: ip
                mac1 = _arp_getnode()
                if mac1 is not None:
                    mac1 = ':'.join(
                        ('%012X' % mac1)[i:i + 2] for i in range(0, 12, 2)
                    )
                    mac2 = _arp_getnode()
                    mac2 = ':'.join(
                        ('%012X' % mac2)[i:i + 2] for i in range(0, 12, 2)
                    )
                    if mac1 == mac2:
                        return mac1
            finally:
                socket.gethostbyname = _gethostbyname

        def _read_arp_file():
            data = _read_file('/proc/net/arp')
            if data is not None and len(data) > 1:
                # Need a space, otherwise a search for 192.168.16.2
                # will match 192.168.16.254 if it comes first!
                match = re.search(re.escape(ip) + r' .+' + mac_re_colon, data)
                if match:
                    return match.groups()[0]

        def _read_file(file_path):
            try:
                with open(file_path) as f:
                    return f.read()
            except OSError:
                return None

        def _neighbor_show():
            res = _popen(
                'ip',
                'neighbor show %s' % ip
            )
            res = res.partition(ip)[2].partition('lladdr')[2]
            return res.strip().split()[0]

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b'', (ip, 55555))
        except socket.error:
            return None

        def _arpreq():
            return __import__('arpreq').arpreq(ip)

        esc = r'\(' + re.escape(ip) + r'\)\s+at\s+'

        def _search(pattern, command, arg):
            def wrapper():
                match = re.search(esc + pattern, _popen(command, arg))
                if match:
                    return match.groups()[0]

            return wrapper

        methods = [
            _read_arp_file,
            _neighbor_show,
            # -a: BSD-style format
            # -n: shows numerical addresses
            _search(mac_re_colon, 'arp', ip),
            _search(mac_re_colon, 'arp', '-an'),
            _search(mac_re_colon, 'arp', '-an %s' % ip)
        ]
        if OSX:
            # Darwin (OSX) oddness
            mac_re_darwin = r'([0-9a-fA-F]{1,2}(?::[0-9a-fA-F]{1,2}){5})'

            methods += [
                _search(mac_re_darwin, 'arp', ip),
                _search(mac_re_darwin, 'arp', '-a'),
                _search(mac_re_darwin, 'arp', '-a %s' % ip)
            ]

        methods += [
            _uuid_ip,
            _arpreq,
        ]

        for m in methods:
            try:
                mac = m()
                if mac:
                    break
            except:
                continue
        else:
            return

        mac = str(mac)
        if not PY2:
            mac = mac.replace("b'", '').replace("'", '')
            mac = mac.replace('\\n', '').replace('\\r', '')

        mac = mac.strip().lower().replace(' ', '').replace('-', ':')

        # Fix cases where there are no colons
        if ':' not in mac and len(mac) == 12:
            mac = ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))

        # Pad single-character octets with a leading zero
        # (e.g Darwin's ARP output)
        elif len(mac) < 17:
            parts = mac.split(':')
            new_mac = []
            for part in parts:
                if len(part) == 1:
                    new_mac.append('0' + part)
                else:
                    new_mac.append(part)
            mac = ':'.join(new_mac)

        # MAC address should ALWAYS be 17 characters before being returned
        if len(mac) != 17:
            mac = None

    return mac


def send_wol(mac_address):
    split_mac = mac_address.split(':')
    hex_mac = list(int(h, 16) for h in split_mac)
    hex_mac = struct.pack('BBBBBB', *hex_mac)

    # create the magic packet from MAC address
    packet = '\xff' * 6 + hex_mac * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(packet, ('255.255.255.255', 9))
    sock.close()


if __name__ == '__main__':
    try:
        entered_ip = raw_input('Enter IP address:')
    except NameError:
        entered_ip = input('Enter IP address:')

    returned_mac = get_mac_address(entered_ip)
    print('Found MAC:', returned_mac)

    if returned_mac is not None:
        try:
            answer = raw_input('Send WOL packet (Y/N)?')
        except NameError:
            answer = input('Send WOL packet (Y/N)?')

        if answer.lower() == 'y':
            send_wol(returned_mac)
