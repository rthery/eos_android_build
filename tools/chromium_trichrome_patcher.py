#!/usr/bin/env python3

import os
import subprocess
import sys
import zipfile

infilename, sign_key = sys.argv[1:]

def ExtractFingerprint(cert):
    cmd = ['openssl', 'x509', '-sha256', '-fingerprint', '-noout', '-in', cert]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE)
    return proc.stdout.decode('utf-8').split('=')[1].replace(':', '')

def patch_trichrome(infilename, sign_key):
    orig_certdigest = "c8a2e9bccf597c2fb6dc66bee293fc13f2fc47ec77bc6b2b0d52c11f51192ab8"
    new_certdigest = ExtractFingerprint(sign_key).lower().rstrip()

    with zipfile.ZipFile(infilename, 'r') as zin, zipfile.ZipFile(infilename + ".patched", 'w') as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == 'AndroidManifest.xml':
                # Make sure we can find the certdigest
                try:
                    data.rindex(orig_certdigest.encode('utf-16-le'))
                except:
                    pass
                # Replace it
                data = data.replace(orig_certdigest.encode('utf-16-le'), new_certdigest.encode('utf-16-le'))
            zout.writestr(info, data)

    # Delete the original file
    os.remove(infilename)

    # Rename the output file to the original file name
    os.rename(infilename + ".patched", infilename)

if "Browser_" in infilename or "BrowserWebView_" in infilename:
    patch_trichrome(infilename, sign_key)
