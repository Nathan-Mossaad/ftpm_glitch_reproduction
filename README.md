# Artifacts of: faulTPM: Exposing AMD fTPMs’ Deepest Secrets"

This repository contains all modifications and additional scripts we had to do while reproducing

# PSPTool

- patching executable firmware with supplied .elf file instead of a premodified binary blob

# amd-sp-glitch

- `.gitignore`: ignore **pycache**
- `attack-code/teensy_cli.txt`: Deduplicate help
- `attack-code/teensy_firmware/Makefile`: Use `#` instead of `//` for comments
- `attack-code/teensy_firmware/Makefile`: Update `COMPILERPATH` and `TEENSY4_PATH` to use new paths
- `attack-code/teensy_firmware/attack.cpp`: Fix timeout for "attack" loop (it didn't terminate before)
- `attack-code/teensy_firmware/teensy_pins.hpp`: Use `inline` instead of `constexpr` (was necessary for our compiler version)
- `attack-code/attack.py`: Was only in `attack-code/ParameterDetermination.md`

# hexdump_to_csv.py

- Script to convert sigrok/pulseview generated .bin trace-file into the saleae format as required by [psptrace](https://github.com/PSPReverse/PSPTrace)
- Note: The timestamps are incorrect (`BYTE_RATE_HZ` would need to be set)!
