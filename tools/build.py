#!/usr/bin/env python3
"""Builds the Soulkeeper Reforged .w3m maps from src/.

Usage:  python3 tools/build.py

Needs tools/.cache/newmpq (built by tools/build.sh).
If refs/<version>/common.j, Blizzard.j and tools/.cache/pjass exist,
the final script is checked against every version.
"""
import os, re, shutil, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from skname import encode, decode

# ---- configuration -------------------------------------------------------
VERSION = 'fix1'
FILE_BASE = 'soulkeeper-td-v11b'
NAME_BASE = '|cff3366ffSoulkeeperTD Showdown1.1|r'
# Texts that show the version. Everything else (author, description, credits) stays original.
# Loading screen subtitle (war3map.wts STRING 11). Original: "Soulkeeper TD v1.1".
LOADING_SUBTITLE = f'|cff3366ffSoulkeeper TD |r |cffffffffv1.1 {VERSION}|r'
# Top-right text (war3mapSkin.txt UPKEEP_NONE = STRING 1229). Original: "SkTD1.1 b by EnTrA1L".
UPKEEP_TEXT = f'|Cff00ff00SkTD1.1 {VERSION} by EnTrA1L|r'
MAP_FILE = f'{FILE_BASE}-{VERSION}.w3m'
MAP_NAME = f'{NAME_BASE} {VERSION}'
# HM3W header: flags and player count of the original map.
HEADER_FLAGS = 0xdcfa
HEADER_PLAYERS = 8
# --------------------------------------------------------------------------

SRC = os.path.join(ROOT, 'src', 'map')
CACHE = os.path.join(ROOT, 'tools', '.cache')
OUT = os.path.join(ROOT, 'build')


def wts_get(wts, n):
    m = re.search(r'STRING %d\r?\n(?://[^\r\n]*\r?\n)?\{\r?\n(.*?)\r?\n\}' % n, wts, re.S)
    if not m:
        sys.exit(f'STRING {n} not found in war3map.wts')
    return m


def wts_set(files, n, text):
    wp = os.path.join(files, 'war3map.wts')
    wts = open(wp, 'rb').read().decode('utf-8')
    m = wts_get(wts, n)
    old = m.group(1)
    wts = wts[:m.start(1)] + text + wts[m.end(1):]
    open(wp, 'wb').write(wts.encode('utf-8'))
    return old


def set_name(files, name):
    """Sets the map name in wts and in the encoded copy checked by the
    protector's anti-tamper check (name stored in Player(13))."""
    old = wts_set(files, 1, name)

    jp = os.path.join(files, 'war3map.j')
    j = open(jp, 'rb').read().decode('latin1')
    lit_old = 'call SetPlayerName(Player(13),"%s")' % encode(old)
    if j.count(lit_old) != 1:
        sys.exit('Encoded copy of the map name not found in war3map.j')
    enc = encode(name)
    if '"' in enc or '\\' in enc:
        sys.exit('Encoded name contains characters that are not valid in JASS')
    assert decode(enc) == name
    j = j.replace(lit_old, 'call SetPlayerName(Player(13),"%s")' % enc)
    open(jp, 'wb').write(j.encode('latin1'))


def header(name):
    h = b'HM3W' + b'\0' * 4 + name.encode('utf-8') + b'\0' + struct.pack('<ii', HEADER_FLAGS, HEADER_PLAYERS)
    if len(h) > 512:
        sys.exit('Name too long for the header')
    return h + b'\0' * (512 - len(h))


def pjass_check(script):
    pj = os.path.join(CACHE, 'pjass')
    refs = os.path.join(ROOT, 'refs')
    if not os.path.exists(pj) or not os.path.isdir(refs):
        print('  (no pjass or no refs/: script not checked)')
        return True
    ok = True
    for ver in sorted(os.listdir(refs)):
        c, b = os.path.join(refs, ver, 'common.j'), os.path.join(refs, ver, 'Blizzard.j')
        if not (os.path.exists(c) and os.path.exists(b)):
            continue
        r = subprocess.run([pj, c, b, script], capture_output=True, text=True, errors='replace')
        last = (r.stdout.strip().splitlines() or [''])[-1]
        good = r.returncode == 0
        ok &= good
        print(f'  pjass {ver}: {"OK" if good else "ERROR"}')
        if not good:
            print('\n'.join(l for l in r.stdout.splitlines() if 'Parse successful' not in l)[:3000])
    return ok


def build():
    work = os.path.join(OUT, 'work')
    files = os.path.join(work, 'files')
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(SRC, files)
    set_name(files, MAP_NAME)
    wts_set(files, 11, LOADING_SUBTITLE)
    wts_set(files, 1229, UPKEEP_TEXT)
    print(MAP_FILE)
    if not pjass_check(os.path.join(files, 'war3map.j')):
        sys.exit('Script fails pjass: map not built')
    mpq = os.path.join(work, 'map.mpq')
    names = sorted(os.listdir(files))
    r = subprocess.run([os.path.join(CACHE, 'newmpq'), mpq, files] + names, capture_output=True, text=True)
    print('  ' + r.stdout.strip())
    if r.returncode != 0:
        sys.exit('Packing failed')
    dest = os.path.join(OUT, MAP_FILE)
    with open(dest, 'wb') as f:
        f.write(header(MAP_NAME))
        f.write(open(mpq, 'rb').read())
    print(f'  -> build/{MAP_FILE} ({os.path.getsize(dest)} bytes)')


if __name__ == '__main__':
    build()
