# Artifacts of: faulTPM: Exposing AMD fTPMs’ Deepest Secrets"

This repository contains all modifications and additional scripts we had to do while reproducing

# psptool

- patching executable firmware with supplied .elf file instead of a premodified binary blob

# amd-sp-glitch

- `.gitignore`: ignore **pycache**
- `attack-code/teensy_cli.txt`: Deduplicate help
- `attack-code/teensy_firmware/Makefile`: Use `#` instead of `//` for comments
- `attack-code/teensy_firmware/Makefile`: Update `COMPILERPATH` and `TEENSY4_PATH` to use new paths
- `attack-code/teensy_firmware/attack.cpp`: Fix timeout for "attack" loop (it didn't terminate before)
- `attack-code/teensy_firmware/teensy_pins.hpp`: Use `inline` instead of `constexpr` (was necessary for our compiler version)
- `attack-code/attack.py`: Was only in `attack-code/ParameterDetermination.md`

- `attack-code/attack.py`: Updated values for our system
- `attack-code/plot.py`: Added ability to create relative graphs
- `attack-code/plot.py`: Fixes to stop crashing
- `attack-code/teensy.py`: Small fix (detect success), Formatting & reduced delay
- `attack-code/pyproject.toml`: Added to enable usage of [uv](https://docs.astral.sh/uv/)
  - Can be used with e.g. `uv run attack.py` and `source .venv/bin/activate`

# attack-scripts

These scripts are intended to aid in visualization during the attack. \
They should be copied into `amd-sp-glitch/attack-code/` and run from there

- monitor.sh: Shows overview of the most recent attack
- python.sh: Runs attack and pipes the output into a file with the current date and time
- show-updating-graph: Repeatedly shows the resulting graph

# Using sigrok-cli with custom so (specific to the Sipeed SLogic16U3)

- Install `sigrok-cli` using package manager
- Download AppImage from [https://dl.sipeed.com/shareURL/SLogic](https://dl.sipeed.com/shareURL/SLogic)
- Extract AppImage: `./PulseView-SLogic-260424-x86_64.AppImage --appimage-extract`
- Capture 10M samples `LD_LIBRARY_PATH="/path/to/extracted/folder/squashfs-root/usr/lib/:$LD_LIBRARY_PATH" sigrok-cli -d sipeed-slogic-analyzer --config "logic_channels=8:voltage_threshold=1.6-1.6,samplerate=20M" --samples 10M --channels D0=VCC,D1=Teensy,D2=SPI_RESET,D3=CS,D4=CLK,D5=DO,D6=DI,D7=WP -t Teensy=1 --output-format binary > /tmp/test.bin`

# hexdump_to_csv.py

- Script to convert sigrok/pulseview generated .bin trace-file into the saleae format as required by [psptrace](https://github.com/PSPReverse/PSPTrace)
- Note: The timestamps are incorrect and estimated only using the sample rate (`BYTE_RATE_HZ`)!

