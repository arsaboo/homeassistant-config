# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import collections
import json
import logging
import os
import socket
import sys

try:
    from .upnp.discover import discover, auto_discover
    from . import __doc__ as doc
    from . import __title__ as title
    from . import __version__ as version
    # noinspection PyCompatibility
    from . import exceptions
    from . import Remote
    from . import key_mappings
    from .config import Config

except ValueError:
    path = os.path.dirname(__file__)
    if not path:
        path = os.path.dirname(sys.argv[0])
    if not path:
        path = os.getcwd()

    sys.path.insert(0, os.path.abspath(os.path.join(path, '..')))
    from samsungctl.upnp.discover import discover, auto_discover
    from samsungctl import __doc__ as doc
    from samsungctl import __title__ as title
    from samsungctl import __version__ as version
    from samsungctl import exceptions
    from samsungctl import Remote
    from samsungctl import key_mappings
    from samsungctl.config import Config


def _read_config():
    config = collections.defaultdict(
        lambda: None,
        dict(
            name="samsungctl",
            description="PC",
            id="",
            method="legacy",
            timeout=0,
        )
    )

    if sys.platform.startswith('win'):
        return config

    directories = []

    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        directories.append(xdg_config)

    directories.append(os.path.join(os.getenv("HOME"), ".config"))
    directories.append("/etc")

    for directory in directories:
        pth = os.path.join(directory, "samsungctl.conf")

        if os.path.isfile(pth):
            config_file = open(pth, 'r')
            break
    else:
        return config

    with config_file:
        try:
            config_json = json.load(config_file)
            config.update(config_json)
        except ValueError as e:
            logging.warning("Could not parse the configuration file.\n  %s", e)

    return config


def keys_help(keys):
    import sys

    key_groups = {}
    max_len = 0

    if not keys or keys == [None]:
        keys = key_mappings.KEYS.values()

    for key in keys:
        if key is None:
            continue

        group = key.group
        key = str(key)
        if group not in key_groups:
            key_groups[group] = []

        if key not in key_groups[group]:
            key_groups[group] += [key]
            max_len = max(max_len, len(key) - 4)

    print('Available keys')
    print('=' * (max_len + 4))
    print()
    print('Note: Key support depends on TV model.')
    print()

    for group in sorted(list(key_groups.keys())):
        print('    ' + group)
        print('    ' + ('-' * max_len))
        print('\n'.join(key_groups[group]))
        print()
    sys.exit(0)


def get_key(key):
    if key in key_mappings.KEYS:
        return key_mappings.KEYS[key]
    else:
        logging.warning("Warning: Key {0} not found.".format(key))


def exit_func(code):
    auto_discover.stop()
    sys.exit(code)


# noinspection PyTypeChecker
def main():
    auto_discover.start()

    epilog = "E.g. %(prog)s --host 192.168.0.10 --name myremote KEY_VOLDOWN"
    parser = argparse.ArgumentParser(
        prog=title,
        description=doc,
        epilog=epilog
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {0}".format(version)
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        help="increase output verbosity"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress non-fatal output"
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="interactive control"
    )
    parser.add_argument(
        "--host",
        help="TV hostname or IP address"
    )
    parser.add_argument(
        "--token",
        default=None,
        help="token for TV's >= 2014"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="TV port number (TCP)"
    )
    parser.add_argument(
        "--method",
        help="Connection method (legacy or websocket)"
    )
    parser.add_argument(
        "--name",
        help="remote control name"
    )
    parser.add_argument(
        "--description",
        metavar="DESC",
        help="remote control description"
    )
    parser.add_argument(
        "--id",
        help="remote control id"
    )
    parser.add_argument(
        "--volume",
        type=int,
        default=None,
        help=(
            "sets the TV volume to the entered value, a value of -1 will "
            "display the volume level"
        )
    )
    parser.add_argument(
        "--brightness",
        type=int,
        default=None,
        help=(
            "sets the TV brightness level to the entered value, "
            "a value of -1 will display the brightness level"
        )
    )
    parser.add_argument(
        "--contrast",
        type=int,
        default=None,
        help=(
            "sets the TV contrast level to the entered value, "
            "a value of -1 will display the contrast level"
        )
    )
    parser.add_argument(
        "--sharpness",
        type=int,
        default=None,
        help=(
            "sets the TV sharpness level to the entered value, "
            "a value of -1 will display the sharpness level"
        )
    )
    parser.add_argument(
        "--mute",
        type=str,
        default=None,
        choices=['off', 'on', 'state'],
        help=(
            "sets the mute on or off (not a toggle), "
            "state displays if the mute is on or off"
        )
    )
    parser.add_argument(
        "--artmode",
        type=str,
        default=None,
        choices=['off', 'on', 'state'],
        help=(
            "sets the art mode for Frame TV's, "
            "state displays if the art mode is on or off"
        )
    )

    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help=(
            "changes the input source to the one specified. "
            "You can either enter the TV source name "
            "eg: HDMI1 HDMI2, USB, PC...."
            "or you can enter the programmed label for the source. "
            "This is going to be what is displayed on the OSD when you change "
            "the source from the remote. If you enter 'state' for the source "
            "name it will print out the currently "
            "active source label and name."
        )
    )

    parser.add_argument(
        "--source-label",
        type=str,
        default=None,
        help=(
            "changes the label for a source. "
            "If you do not use --source to specify the source to change the "
            "label on. It will automatically default to the currently "
            "active source. If you set the label to 'state' it will print out "
            "the current label for a source if specified using --source or "
            "the currently active source"
        )
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="socket timeout in seconds (0 = no timeout)"
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default=None,
        help="configuration file to load and/or save to"
    )
    parser.add_argument(
        "--start-app",
        help="start an application --start-app \"Netflix\""
    )
    parser.add_argument(
        "--app-metadata",
        help=(
            "pass options string of information the application "
            "can use when it starts up. And example would be the browser. "
            "To have it open directly to a specific URL you would enter: "
            "\"http\/\/www.some-web-address.com\". wrapping the meta data in "
            "quotes will reduce the possibility of a command line parser "
            "error."
        )
    )
    parser.add_argument(
        "--key-help",
        action="store_true",
        help="print available keys. (key support depends on tv model)"
    )
    parser.add_argument(
        "key",
        nargs="*",
        default=[],
        type=get_key,
        help="keys to be sent (e.g. KEY_VOLDOWN)"
    )

    args = parser.parse_args()

    if args.quiet:
        log_level = logging.ERROR
    elif not args.verbose:
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    if args.key_help:
        keys_help(args.key)

    try:

        if args.config_file is None:
            config = _read_config()
            config.update(
                {
                    k: v for k, v in vars(args).items()
                    if v is not None
                }
            )
            config = Config(**config)
        else:
            config = {
                k: v for k, v in vars(args).items()
                if v is not None
            }
            config = Config.load(args.config_file)(**config)

    except exceptions.ConfigError:
        import traceback
        traceback.print_exc()

        return

    config.log_level = log_level

    if config.upnp_locations is None:
        config.upnp_locations = []

    if not config.host or not config.uuid:
        configs = discover(config.host)
        if len(configs) > 1:

            while True:
                for i, cfg in enumerate(configs):
                    print(i + 1, ':', cfg.model)
                try:
                    # noinspection PyCompatibility
                    answer = raw_input(
                        'Enter the number of the TV you want to pair with:'
                    )
                except NameError:
                    answer = input(
                        'Enter the number of the TV you want to pair with:'
                    )

                try:
                    answer = int(answer) - 1
                    cfg = configs[answer]
                    break
                except (TypeError, ValueError, IndexError):
                    pass

        elif configs:
            cfg = configs[0]

        else:
            print('Unable to discover any TV\'s')
            exit_func(0)
            # this never actually happens it is only here to make my IDE happy
            raise RuntimeError
    else:
        cfg = config

    try:
        with Remote(cfg) as remote:
            if args.interactive:
                logging.getLogger().setLevel(logging.ERROR)
                from . import interactive
                inter = interactive.Interactive(remote)
                inter.run()
                exit_func(0)

            if (
                args.key and
                args.key[0] in ('KEY_POWER', 'KEY_POWERON') and
                cfg.paired and
                not remote.power
            ):
                args.key.pop(0)

                import threading

                event = threading.Event()

                def callback(_, state):
                    if state:
                        event.set()

                auto_discover.register_callback(callback, cfg.uuid)
                remote.power = True

                event.wait(10.0)
                auto_discover.unregister_callback(callback, cfg.uuid)

                if not event.isSet():
                    print('Unable to send command TV is not powered on.')
                    exit_func(1)

            if cfg.method == 'websocket' and args.start_app:
                app = remote.get_application(args.start_app)
                if args.app_metadata:
                    app.run(args.app_metadata)
                else:
                    app.run()
            else:
                for key in args.key:
                    if key is None:
                        continue
                    key(remote)

            if args.volume is not None:
                if args.volume == -1:
                    print('Volume:', remote.volume, '%')
                else:
                    remote.volume = args.volume

            elif args.mute is not None:
                if args.mute == 'state':
                    print('Mute:', 'ON' if remote.mute else 'OFF')
                else:
                    remote.mute = args.mute == 'on'

            elif args.artmode is not None:
                if args.artmode == 'state':
                    print('Art Mode:', 'ON' if remote.artmode else 'OFF')
                else:
                    remote.artmode = args.artmode == 'on'

            if args.brightness is not None:
                if args.brightness == -1:
                    print('Brightness:', remote.brightness, '%')
                else:
                    remote.brightness = args.brightness

            if args.contrast is not None:
                if args.contrast == -1:
                    print('Contrast:', remote.contrast, '%')
                else:
                    remote.contrast = args.contrast

            if args.sharpness is not None:
                if args.sharpness == -1:
                    print('Sharpness:', remote.sharpness, '%')
                else:
                    remote.sharpness = args.sharpness

            if args.source_label is not None:
                if args.source is None:
                    if args.source_label == 'state':
                        print('Source Label:', remote.source.label)
                    else:
                        remote.source.label = args.remote_label
                else:
                    for source in remote.sources:
                        if args.source in (source.label, source.name):
                            if args.source_label == 'state':
                                print('Source Label:', source.label)
                            else:
                                source.label = args.source_label
                            break

            elif args.source is not None:
                if args.source == 'state':
                    source = remote.source
                    print(
                        'Source: Label =', source.label,
                        'Name =', source.name
                    )
                else:
                    remote.source = args.source

    except exceptions.ConnectionClosed:
        logging.error("Error: Connection closed!")
    except exceptions.AccessDenied:
        logging.error("Error: Access denied!")
    except exceptions.ConfigUnknownMethod:
        logging.error("Error: Unknown method '{}'".format(cfg.method))
    except socket.timeout:
        logging.error("Error: Timed out!")
    except OSError as e:
        logging.error("Error: %s", e.strerror)

    if args.config_file:
        cfg.save()
        exit_func(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit_func(2)
