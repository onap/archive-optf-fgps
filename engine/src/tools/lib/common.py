#
# -------------------------------------------------------------------------
#   Copyright (c) 2019 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#


import os
import select
import sys


def set_argument(arg=None, prompt=None, multiline=False):
    """Return argument from file, cmd line, read from a pipe or prompt user """

    if arg:
        if os.path.isfile(arg):
            f = open(arg)
            message = f.readlines()
            f.close()
        else:
            message = arg
    else:
        if sys.stdin in select.select([sys.stdin], [], [], .5)[0]:
            message = sys.stdin.readlines()
        else:
            print prompt,
            if multiline:
                sentinel = ''
                message = list(iter(raw_input, sentinel))
            else:
                message = [raw_input()]

    return message


def list2string(message):
    return ''.join(message)


def chop(message):

    if message.endswith('\n'):
        message = message[:-1]

    return message


# MAIN
if __name__ == "__main__":

    msg = set_argument(sys.argv[0])
    for row in msg:
        print row,
    print "\n", list2string(msg)

    msg = set_argument(prompt="Message? ")
    for row in msg:
        print row,
    print "\n", list2string(msg)
