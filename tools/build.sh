#!/usr/bin/env bash
# Sets up the tools (first run only) and builds the map.
# Usage: tools/build.sh
# Works on Linux or WSL. Needs git, gcc/g++, make and python3.
# Checking the script with pjass needs flex and bison, plus the
# references in refs/<version>/common.j and Blizzard.j (see docs/BUILD.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="$ROOT/tools/.cache"
mkdir -p "$CACHE"

# Pinned tool versions. The map bytes depend on StormLib, so changing a pin
# can change the built .w3m. Changing a pin rebuilds the tools on the next run.
STORMLIB_REPO=https://github.com/ladislav-zezula/StormLib.git
STORMLIB_REF=116135c27e8c0dcf8ea0a0c549a6d737ce10fc73   # 2026-10-12
PJASS_REPO=https://github.com/lep/pjass.git
PJASS_REF=654c3cf7731eb472518e6915e9d7672a72652165      # release-2026-10-13

# Shallow checkout of one exact commit.
fetch_ref() {  # <repo> <commit> <dir>
  rm -rf "$3" && mkdir -p "$3"
  git -C "$3" init -q
  git -C "$3" fetch -q --depth 1 "$1" "$2"
  git -C "$3" checkout -q FETCH_HEAD
}

# Tools built with other pins (or before pinning) are discarded.
PINS="stormlib=$STORMLIB_REF pjass=$PJASS_REF"
if [ "$(cat "$CACHE/pins" 2>/dev/null)" != "$PINS" ]; then
  rm -rf "$CACHE/StormLib" "$CACHE/libstorm.a" "$CACHE/newmpq" "$CACHE/pjass-src" "$CACHE/pjass"
fi

stormlib() {
  local d="$CACHE/StormLib"
  fetch_ref "$STORMLIB_REPO" "$STORMLIB_REF" "$d"
  if command -v cmake >/dev/null; then
    mkdir -p "$d/b" && (cd "$d/b" && cmake .. -DCMAKE_BUILD_TYPE=Release -DSTORM_USE_BUNDLED_LIBRARIES=ON >/dev/null && make -s -j"$(nproc)" storm)
    cp "$d/b/libstorm.a" "$CACHE/libstorm.a"
  else
    # No cmake: manual build using the libraries bundled with StormLib.
    mkdir -p "$d/obj" && cd "$d"
    find src \( -name '*.c' -o -name '*.cpp' \) | grep -vE 'DllMain|/wdk/|lzma/C/(Threads|LzFindMt)|^src/Lib[A-Za-z]*\.c$|zlib/compress_zlib\.c' | while read -r s; do
      o="obj/$(echo "$s" | tr '/' '_').o"
      case "$s" in *.c) gcc -O1 -w -c -D_7ZIP_ST "$s" -o "$o" ;; *) g++ -O1 -w -c "$s" -o "$o" ;; esac
    done
    printf '#include <stdio.h>\nFILE* _fdopen(int f,const char*m){return fdopen(f,m);}\n' > obj/stub.c
    gcc -c obj/stub.c -o obj/stub.o
    rm -f "$CACHE/libstorm.a" && ar rcs "$CACHE/libstorm.a" obj/*.o
    cd "$ROOT"
  fi
}

if [ ! -x "$CACHE/newmpq" ]; then
  echo "Building StormLib and newmpq..."
  stormlib
  g++ -O1 -I "$CACHE/StormLib/src" "$ROOT/tools/newmpq.cpp" "$CACHE/libstorm.a" -lpthread -o "$CACHE/newmpq"
fi

if [ ! -x "$CACHE/pjass" ]; then
  if command -v flex >/dev/null && command -v bison >/dev/null; then
    echo "Building pjass..."
    fetch_ref "$PJASS_REPO" "$PJASS_REF" "$CACHE/pjass-src"
    make -s -C "$CACHE/pjass-src" >/dev/null 2>&1
    cp "$CACHE/pjass-src/pjass" "$CACHE/pjass"
  else
    echo "Warning: no flex/bison, pjass not built; the script will not be checked."
  fi
fi

echo "$PINS" > "$CACHE/pins"

python3 "$ROOT/tools/build.py"