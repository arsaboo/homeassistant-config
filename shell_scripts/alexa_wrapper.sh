#!/bin/bash
#
# Amazon Alexa TTS Home Assistant Wrapper
#
# 2018-06-18: v0.1 initial release
#
# This script is intended to allow the Alexa Remote Control script
# from Alex Lotzimmer to be used as a command line notify platform
# in Home Assistant.
#
# Usage:
# ./alexa_wrapper.sh -d "My Dot Name"
#
# Home Assistant will pass the message to the script via STDIN. The
# Alexa Remote control script requires that spaces be replaced with
# underscores.
#
# Installation:
# Place alexa_wrapper.sh and alexa_remote_control.sh in your Home Assistant
# config directory. In a shell type echo $PATH and replace the below PATH
# variable with your values.
#
# Edit alexa_remote_control.sh with your credentials and
# your location. Test that you can pull a list of devices with
# ./alexa_remote_control.sh -a
#
# Add a command line notify component for each Alexa device
# to Home Assistant as follows:
#
# notify:
#   - platform: command_line
#     name: 'My Dot Name'
#     command: "/home/homeassistant/.homeassistant/alexa_wrapper -d 'My Dot Name'"
#
# You should then be able to call notify.my_dot_name from automations
#

PATH=/home/arsaboo/bin:/home/arsaboo/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ALEXA_REMOTE="$DIR/alexa_remote_control.sh"

usage()
{
        echo "$0 -d <device>|ALL"
}

case "$1" in
        -d)
                if [ "${2#-}" != "${2}" -o -z "$2" ] ; then
                        echo "ERROR: missing argument for ${1}"
                        usage
                        exit 1
                fi
                DEVICE=$2
                shift
                ;;
        *)
                echo "ERROR: unknown option ${1}"
                usage
                exit 1
                ;;
esac
shift

read message

formatted=${message// /_}

$ALEXA_REMOTE -d "$DEVICE" -e speak:$formatted >> /dev/null
exit 0
