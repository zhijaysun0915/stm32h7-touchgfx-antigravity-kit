# Hardware Constraints & UI Specification (UM2488)

## 1. Board Selection & Power Supply Configuration
> Reference: [UM2488 Discovery kits with STM32H745XI and STM32H750XB MCUs (Rev 10)](https://www.st.com/resource/en/user_manual/um2488-discovery-kits-with-stm32h745xi-and-stm32h750xb-mcus-stmicroelectronics.pdf)

| Attribute | STM32H745I-DISCO | STM32H750B-DK |
| :--- | :--- | :--- |
| **MCU Order Code** | `STM32H745XIH6` (Cortex-M7 @ 480 MHz + Cortex-M4 @ 240 MHz) | `STM32H750XBH6` (Cortex-M7 @ 480 MHz) |
| **Internal Flash** | 2 Mbytes (`0x08000000`) | 128 Kbytes (`0x08000000`) |
| **External QSPI Flash** | 2× 512-Mbit (`MT25TL01G`, 128 MB mapped at `0x90000000`) | 2× 512-Mbit (`MT25TL01G`, 128 MB mapped at `0x90000000`) |
| **External SDRAM** | 128-Mbit FMC SDRAM (`0xD0000000`, 8 MB usable) | 128-Mbit FMC SDRAM (`0xD0000000`, 8 MB usable) |
| **Default Power Mode** | **Direct SMPS** (`PWR_DIRECT_SMPS_SUPPLY`) | **LDO** (`PWR_LDO_SUPPLY`) |
| **External Flash Loader** | `MT25TL01G_STM32H745I-DISCO.stldr` | `MT25TL01G_STM32H750B-DISCO.stldr` |
| **STLINK-V3E VCP UART** | `USART3` (`PB10` TX, `PB11` RX) @ 115200 8N1 via CN14 | `USART3` (`PB10` TX, `PB11` RX) @ 115200 8N1 via CN14 |
| **User LEDs / Button** | `LD6` Red (`PI13`), `LD7` Green (`PJ2`), `B1` User (`PC13`) | `LD6` Red (`PI13`), `LD7` Green (`PJ2`), `B1` User (`PC13`) |

---

## 2. Current User UI Prompt (Editable by User or Agent)

### Target UI Concept: Smart Environmental & System Control Dashboard
- **Screen 1 (`DashboardScreen`)**:
  - Dark slate background (`#0F172A`) with a top header bar showing board status and real-time temperature wildcard (`System Temp: <value> C`).
  - Left card (`card_panel.png` at `X=16, Y=48, W=216, H=160`): Displays real-time MCU load progress bar (`loadBar`) and status metrics.
  - Right card (`card_panel.png` at `X=248, Y=48, W=216, H=160`): Interactive control panel with an action button (`btnBoost` to toggle User LED `LD7` / boost mode) and a navigation button (`btnNextScreen`) that slides East to `SettingsScreen`.
- **Screen 2 (`SettingsScreen`)**:
  - Configuration view with brightness/threshold controls and a `Back` button (`btnBack`) that slides West back to `DashboardScreen`.
