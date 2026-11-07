# Hardware Constraints & Memory Specifications (UM2488 Rev 10)

Target Boards: **STM32H750B-DK** (`STM32H750XBH6`) & **STM32H745I-DISCO** (`STM32H745XIH6`)

---

## 1. Physical Connectivity & Ports
- **CN14 (STLINK-V3E Micro-B)**:
  - Powers the board (+5V_ST_LINK).
  - Provides SWD hardware debug interface.
  - Bridges `USART3` (`PB10` TX, `PB11` RX) to Virtual COM Port (VCP) at 115200 8N1.
- **CN13 (USB OTG_FS Micro-B)**:
  - User USB application port. **DO NOT** use for flashing or power.
- **Display**:
  - 4.3" 480×272 RGB capacitive touch LCD (`RK043FN48H`).
  - Active display area: `480` (W) × `272` (H) pixels.

---

## 2. Power Supply & Jumpers
- **JP6 (Power Selection)**: Default jumper position `[STLK]` (pins 1-2).
- **Power Architecture**:
  - `STM32H750B-DK`: Solder bridges configure **LDO Supply** (`PWR_LDO_SUPPLY`).
  - `STM32H745I-DISCO`: Solder bridges configure **Direct SMPS Supply** (`PWR_DIRECT_SMPS_SUPPLY`).
- **Safety Critical Rule**: Never flash a firmware configured with SMPS supply onto an LDO-configured board. It triggers a hardware power lockout after reset.

---

## 3. Memory Architecture
- **Internal Flash (`0x08000000`)**:
  - STM32H750XB: 128 KB
  - STM32H745XI: 2 MB
  - Allocated for: `.isr_vector` (Vector table), `.text` (MVP logic, system init).
- **External QSPI NOR Flash (`0x90000000`)**:
  - 2× 512-Mbit Micron `MT25TL01G` (128 MB total).
  - Allocated for: `ExtFlashSection` (TouchGFX bitmap assets and Unicode font tables).
- **External SDRAM (`0xD0000000`)**:
  - 128-Mbit Micron FMC SDRAM (16-bit wide bus, 8 MB usable).
  - Allocated for: `TouchGFX_Framebuffer` (Double buffer: `480 * 272 * 2 * 2 = 522,240 bytes`).
- **Internal AXI SRAM (`0x24000000`)**:
  - 512 KB high-performance RAM.
  - Allocated for: `.data`, `.bss`, stack, and heap.
