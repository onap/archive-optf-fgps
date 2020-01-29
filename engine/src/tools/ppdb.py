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
#!/usr/bin/env python2.7


import sys
import os
import json
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='parse results.')
    parser.add_argument('-f', '--file', help='json file required for create/view')
    parser.add_argument('-verbose', action='store_true', help='more output than you want')
    opts = parser.parse_args()

    if opts.file and os.path.exists(opts.file):
            inf = open(opts.file)
    else:
            inf = sys.stdin

    results = json.loads(inf.read())
    if opts.verbose:
        print (json.dumps(results, sort_keys=True, indent=4))
        print ("---------------------------------------------")

    if "request" in results.keys():
        key = "request"
        result = json.loads(results[key])
        print (json.dumps(result, sort_keys=True, indent=4))
        sys.exit(0)

    if "result" in results.keys():
        result = results["result"]

        if not isinstance(result, list):
            sys.stdout.write("result ")
            sys.stdout.flush()
            result = json.loads(result)
            print (json.dumps(result, sort_keys=True, indent=4))
            sys.exit(0)

        for _, row in result.items():
            rr = json.loads(row["result"])

            # for k, d in row.iteritems():
            #     print ("%s)  %s"% (k, d))

            sys.stdout.write("result ")
            sys.stdout.flush()
            print (json.dumps(rr, indent=4))
            # for f in rr:
            #     for line in (json.dumps(f, sort_keys=True, indent=4)).splitlines():
            #         print "\t%s"%line
            # print "}"

        sys.exit(0)

    if "resource" in results.keys():
        key = "resource"
        result = json.loads(results[key])
        print (json.dumps(result, sort_keys=True, indent=4))

        if not isinstance(result, list):
            sys.stdout.write("resource ")
            sys.stdout.flush()
            result = json.loads(result)
            print (json.dumps(result, sort_keys=True, indent=4))
            sys.exit(0)

        print (json.dumps(result, sort_keys=True, indent=4))
        sys.exit(0)

    print (results.keys())
