/*
 * Linker Script for STM32H750XBH6 (STM32H750B-DK) & STM32H745XIH6 (STM32H745I-DISCO)
 * Reference: UM2488 Rev 10
 * - Internal Flash: 0x08000000 (128K on H750XB, 2048K on H745XI)
 * - AXI SRAM (D1):  0x24000000 (512K)
 * - External SDRAM: 0xD0000000 (8M usable via FMC)
 * - External QSPI:  0x90000000 (128M Dual Quad-SPI MT25TL01G)
 */
ENTRY(Reset_Handler)

MEMORY
{
  FLASH (rx)      : ORIGIN = 0x08000000, LENGTH = 128K
  DTCMRAM (xrw)   : ORIGIN = 0x20000000, LENGTH = 128K
  RAM_D1 (xrw)    : ORIGIN = 0x24000000, LENGTH = 512K
  SDRAM (xrw)     : ORIGIN = 0xD0000000, LENGTH = 8M
  QSPI (r)        : ORIGIN = 0x90000000, LENGTH = 128M
}

_estack = ORIGIN(DTCMRAM) + LENGTH(DTCMRAM);

SECTIONS
{
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.rodata)
    *(.rodata*)
    KEEP (*(.init))
    KEEP (*(.fini))
    . = ALIGN(4);
    _etext = .;
  } >FLASH

  .ARM.extab : { *(.ARM.extab* .gnu.linkonce.armextab.*) } >FLASH
  .ARM : {
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
  } >FLASH

  .preinit_array :
  {
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array*))
    PROVIDE_HIDDEN (__preinit_array_end = .);
  } >FLASH

  .init_array :
  {
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
  } >FLASH

  .fini_array :
  {
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array*))
    PROVIDE_HIDDEN (__fini_array_end = .);
  } >FLASH

  _sidata = LOADADDR(.data);

  .data :
  {
    . = ALIGN(4);
    _sdata = .;
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;
  } >RAM_D1 AT> FLASH

  .bss :
  {
    . = ALIGN(4);
    _sbss = .;
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;
    __bss_end__ = _ebss;
  } >RAM_D1

  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + 0x2000;
    . = ALIGN(8);
  } >DTCMRAM

  /* TouchGFX Framebuffer in External SDRAM (0xD0000000) */
  TouchGFX_Framebuffer (NOLOAD) :
  {
    . = ALIGN(4);
    KEEP(*(TouchGFX_Framebuffer))
    . = ALIGN(4);
  } >SDRAM

  /* TouchGFX Bitmaps, Fonts & Texts in External QSPI NOR Flash (0x90000000) */
  ExtFlashSection :
  {
    . = ALIGN(4);
    KEEP(*(ExtFlashSection))
    KEEP(*(ExtFlashSection*))
    . = ALIGN(4);
  } >QSPI
}
