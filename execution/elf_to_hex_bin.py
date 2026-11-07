#!/usr/bin/env python3
"""
ELF Memory Analyzer & Intel HEX / Binary Exporter for STM32H7 + TouchGFX
Uses pyelftools & intelhex to inspect Internal Flash (0x08000000),
External QSPI NOR Flash (0x90000000), and External FMC SDRAM (0xD0000000),
and generates flashable .hex and .bin images.
"""
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile
from intelhex import IntelHex


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: elf_to_hex_bin.py <path/to/firmware.elf>")

    elf_path = Path(sys.argv[1])
    out_dir = elf_path.parent
    stem = elf_path.stem

    ih = IntelHex()
    flash_bytes = 0
    qspi_bytes = 0
    sdram_bytes = 0
    ram_bytes = 0

    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        print("==========================================================================")
        print(f" STM32H7 + TouchGFX Firmware Memory Map Summary ({elf_path.name})")
        print("==========================================================================")
        print(f" {'Section':<24} {'Address':<14} {'Size (Bytes)':<14} {'Region'}")
        print("--------------------------------------------------------------------------")
        for sec in elf.iter_sections():
            size = sec["sh_size"]
            addr = sec["sh_addr"]
            name = sec.name
            if size == 0 or addr == 0:
                continue

            if 0x08000000 <= addr < 0x08200000:
                region = "INTERNAL_FLASH"
                flash_bytes += size
                data = sec.data()
                ih.puts(addr, data)
            elif 0x90000000 <= addr < 0x98000000:
                region = "QSPI_EXT_FLASH"
                qspi_bytes += size
                data = sec.data()
                ih.puts(addr, data)
            elif 0xD0000000 <= addr < 0xD1000000:
                region = "FMC_SDRAM_FB"
                sdram_bytes += size
            else:
                region = "AXI_SRAM/DTCM"
                ram_bytes += size

            print(f" {name:<24} 0x{addr:08X}     {size:<14} {region}")

    hex_path = out_dir / f"{stem}.hex"
    ih.write_hex_file(str(hex_path))

    print("--------------------------------------------------------------------------")
    print(f" Internal Flash (0x08000000) : {flash_bytes:>8} B  ({flash_bytes/1024:.2f} KB)")
    print(f" External QSPI  (0x90000000) : {qspi_bytes:>8} B  ({qspi_bytes/1024:.2f} KB)")
    print(f" External SDRAM (0xD0000000) : {sdram_bytes:>8} B  ({sdram_bytes/1024:.2f} KB - 480x272x2x2 FB)")
    print(f" Internal RAM   (0x24000000) : {ram_bytes:>8} B  ({ram_bytes/1024:.2f} KB)")
    print(f" Intel HEX Image Generated   : {hex_path}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
