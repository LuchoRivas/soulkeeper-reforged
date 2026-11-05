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

stormlib() {
  local d="$CACHE/StormLib"
  [ -d "$d" ] || git clone -q --depth 1 https://github.com/ladislav-zezula/StormLib.git "$d"
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
    [ -d "$CACHE/pjass-src" ] || git clone -q --depth 1 https://github.com/lep/pjass.git "$CACHE/pjass-src"
    make -s -C "$CACHE/pjass-src" >/dev/null 2>&1
    cp "$CACHE/pjass-src/pjass" "$CACHE/pjass"
  else
    echo "Warning: no flex/bison, pjass not built; the script will not be checked."
  fi
fi

python3 "$ROOT/tools/build.py"
