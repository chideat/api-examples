#!/usr/bin/env python
# encoding=utf8

""" The api sign example
    Author: lipixun
    Created Time : 五  9/30 17:37:17 2016

    File Name: sign.py
    Description:

"""

import sys
reload(sys)
sys.setdefaultencoding("utf8")

from datetime import datetime

import jwt
import rfc3339

def getNowSignTime():
    """Get now sign time (Discard microsecond part)
    """
    return datetime.utcnow().replace(microsecond = 0)

def signHttpViaRS256(appID, path, time, key):
    """Sign http
    Returns:
        The signature string
    """
    return jwt.encode({
        "appID": appID,
        "path": path,
        "utctime": rfc3339.rfc3339(time, utc = True, use_system_timezone = False),
        }, key, algorithm = "RS256")

def signHttpViaHS256(appID, path, time, secret):
    """Sign http
    Returns:
        The signature string
    """
    return jwt.encode({
        "appID": appID,
        "path": path,
        "utctime": rfc3339.rfc3339(time, utc = True, use_system_timezone = False),
        }, secret, algorithm = "HS256")

def verifyHttpViaRS256(appID, path, time, key, signature):
    """Verify http
    Returns:
        True / False
    """
    try:
        sign = jwt.decode(signature, key, algorithm = "RS256")
        assert sign.get("appID") == appID and sign.get("path") == path and sign.get("utctime") == rfc3339.rfc3339(time, utc = True, use_system_timezone = False)
        return True
    except:
        return False

def verifyHttpViaHS256(appID, path, time, secret, signature):
    """Verify http
    Returns:
        True / False
    """
    try:
        sign = jwt.decode(signature, secret, algorithm = "HS256")
        assert sign.get("appID") == appID and sign.get("path") == path and sign.get("utctime") == rfc3339.rfc3339(time, utc = True, use_system_timezone = False)
        return True
    except:
        return False

if __name__ == "__main__":

    from argparse import ArgumentParser

    def getArguments():
        """Get arguments
        """
        parser = ArgumentParser(description = "API Sign Utility")
        subParsers = parser.add_subparsers(dest = "action")
        # Sign http parser
        signHttpParser = subParsers.add_parser("signhttp")
        signHttpParser.add_argument("-i", "--appid", dest = "appID", required = True, help = "The application id")
        signHttpParser.add_argument("-p", "--path", dest = "path", required = True, help = "The request url path")
        signHttpParser.add_argument("-k", "--key", dest = "key", help = "The private key file (PEM encoded)")
        signHttpParser.add_argument("--secret", dest = "secret", help = "The secret")
        signHttpParser.add_argument("-t", "--time", dest = "time", required = False, type = int, help = "The sign time, unix timestamp in utc. Will use now time if not specified")
        # Verify http parser
        verifyHttpParser = subParsers.add_parser("verifyhttp")
        verifyHttpParser.add_argument("-i", "--appid", dest = "appID", required = True, help = "The application id")
        verifyHttpParser.add_argument("-p", "--path", dest = "path", required = True, help = "The request url path")
        verifyHttpParser.add_argument("-k", "--key", dest = "key", help = "The public key file (PEM encoded)")
        verifyHttpParser.add_argument("--secret", dest = "secret", help = "The secret")
        verifyHttpParser.add_argument("-t", "--time", dest = "time", required = False, type = int, help = "The sign time, unix timestamp in utc. Will use now time if not specified")
        verifyHttpParser.add_argument("-s", "--sign", dest = "sign", required = True, help = "The signature to verify")
        # Done
        return parser.parse_args()

    def main():
        """The main entry
        """
        args = getArguments()
        if args.key and args.secret or not args.key and not args.secret:
            raise ValueError("Please either provide key or secret")
        # Get time
        if args.time:
            time = datetime.utcfromtimestamp(float(args.time))
        else:
            time = getNowSignTime()
            print "Generate Time:", time.strftime("%s")
        # Check action
        if args.action == "signhttp":
            # Sign http
            if args.key:
                with open(args.key, "rb") as fd:
                    sign = signHttpViaRS256(args.appID, args.path, time, fd.read())
            else:
                sign = signHttpViaHS256(args.appID, args.path, time, args.secret)
            # Print
            print "Signature:", sign
        elif args.action == "verifyhttp":
            if args.key:
                with open(args.key, "rb") as fd:
                    verified = verifyHttpViaRS256(args.appID, args.path, time, fd.read(), args.sign)
            else:
                verified = verifyHttpViaHS256(args.appID, args.path, time, args.secret, args.sign)
            # Print
            print "Verified" if verified else "Not verified"
        else:
            raise ValueError("Unknown action [%s]" % args.action)

    main()
