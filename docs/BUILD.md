# How the map is built

`tools/build.sh` does everything:

1. On first run it downloads and builds [StormLib](https://github.com/ladislav-zezula/StormLib) (to write the MPQ archive) and [pjass](https://github.com/lep/pjass) (to check the script) into `tools/.cache/`. Both are pinned to exact commits at the top of `tools/build.sh` (`STORMLIB_REF`, `PJASS_REF`), because the map bytes depend on the StormLib version. Changing a pin rebuilds the tools on the next run.
2. Runs `tools/build.py`, which:
   - copies `src/map/`;
   - sets the map name in `war3map.wts` (STRING 1), in the file header and in the encoded copy checked by the anti-tamper check (see NOTES.md);
   - puts the version in the loading screen subtitle (STRING 11) and in the top-right text (STRING 1229);
   - checks the script with pjass against every version in `refs/`;
   - packs it with `newmpq`, which reads the archive back and verifies every file.

The version and the texts that show it are configured at the top of `tools/build.py`.

## Requirements

Linux or WSL with `git`, `gcc`, `g++`, `make` and `python3`. Optional: `cmake` (otherwise StormLib is built by hand), and `flex` and `bison` for pjass.

On WSL (Ubuntu): `sudo apt install build-essential cmake flex bison python3 git`

## pjass references (`refs/`)

pjass needs `common.j` and `Blizzard.j` from each game version. They are Blizzard files, so they are not in the repo. Expected layout:

```
refs/1.27b/common.j
refs/1.27b/Blizzard.j
refs/reforged/common.j
refs/reforged/Blizzard.j
```

Where to get them: on 1.27b, `Scripts\common.j` and `Scripts\Blizzard.j` inside `War3Patch.mpq`; on Reforged, `war3.w3mod:scripts\common.j` and `blizzard.j` inside the CASC storage.

Without `refs/` the map still builds, but the script is not checked.

## Continuous build (GitHub Actions)

`.github/workflows/build.yml` builds the map on every push to `main`, on pull requests and on demand (Actions tab, "Run workflow"). The `.w3m` is attached to the run as an artifact.

The runner has no game files, so `refs/reforged/` is taken from [lep/jassdoc](https://github.com/lep/jassdoc) at a pinned commit (`JASSDOC_REF` in the workflow). Those files carry `/** */` documentation blocks that pjass rejects; `tools/jass_strip.py` removes them. The pjass check is mandatory in CI: the job fails if it does not run.

CI checks against Reforged only. There is no public copy of the 1.27b files that pjass accepts, so the 1.27b check stays local.

### Publishing a version

Pushing a tag builds the map and publishes a GitHub Release with the `.w3m` and its SHA-256. The tag must be equal to `VERSION` in `tools/build.py`, otherwise the build fails before publishing:

```
git tag -a fix1 -m "fix1: ..."
git push origin fix1
```

If a release step fails, delete the release (if it was created) and re-run the workflow, or delete and push the tag again.