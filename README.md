# Aftershock to Quake 3 demo converter

(**experimental**) Convert Aftershock-XE (revision 330v2) to Quake 3 demos. [Aftershock-XE](https://github.com/Irbyz/aftershock-xe) mod demos are incompatible with Q3 demos. This app converts the demo to Q3 protocol 68 (.dm_71 extension for OpenArena) that can be played in [wolfcamql](https://github.com/brugal/wolfcamql). Note that some AS info is removed in the conversation process, namely scoreboard stats. Also, some event fixes are hardcoded, and therefore you cannot convert the same demo back to AS. So keep the original demos!

What was fixed:

- most entities (correct shooting animations and sounds)
- correct health, armor, and ammo display

What was not fixed:

- some entities may still give wrong sounds, especially ones viewed from non-demo taker POV
- scoreboard stats like damage dealt, weapon accuracies, etc. (would require conversion to QL demo)

# Build

- create a `venv` environment with requirements inside the project then run `tox` to build the executable
- run the executable `dist/democonverter -h`

```sh
python -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/tox
```

# Usage

```
usage: democonverter [-h] [-i] [-o OUTPUT] [demos ...]

Convert Aftershock demo to WolfcamQL friendly demo.

positional arguments:
  demos                 Input demo(s)

options:
  -h, --help            show this help message and exit
  -i, --info            Show info without converting demo.
  -o OUTPUT, --output OUTPUT
                        Output directory. Default is "out"
```
