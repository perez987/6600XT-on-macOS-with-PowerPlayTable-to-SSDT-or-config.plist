# AMD 6600 on macOS: Zero RPM disabled with softPowerPlayTable (SSDT or config.plist)

AMD PowerPlay technology allows graphics card to vary performance based on demand, switching between performance and power saving. It has automatic operating modes based on predefined parameters. It also allows user settings.

Windows 10 and 11 can make a copy of these energy profiles in the PP_PhmSoftPowerPlayTable registry key whose value is so called SoftPowerPlayTable (SPPT), long hexadecimal string. It is a way to have a quick reference by the operating system.

This SPPT key can be read and modified. Thanks to this, it is possible to modify parameters of the graphics card operation, changing their behavior and/or energy management and bring these settings to macOS.

---

### Go [here](README-6600.md) to get info about the XFX RX 6600 XT graphics card on macOS.

---

### Zero RPM

AMD Radeon 5000 and 6000 series cards come from factory with Zero RPM feature activated so that fans are stopped below 60º, this makes them completely silent except when graphics processor is demanded (tests, games, etc.).

On my PC, for example, the base temperature is Windows is 35-45º on Windows and 45-55º on macOS. Although these are safe temperatures for daily use, some users would prefer to have values like the ones in Windows.

Quickest and most effective way to achieve this is by disabling Zero RPM so that fans are spinning all the time and not just above a predefined temperature. However, this is very easy to do on Windows with the Radeon software but on macOS this option does not exist.

### SoftPowerPlayTable

One way to disable Zero RPM on macOS without changing any other parameters is by using the SPPT table created in Windows. To obtain the SPPT table you have to go to Windows, where it is generated as a registry key and exported to a file that we bring to macOS where the file is adapted to be added to an SSDT file or to the OpenCore config.plist file.

---

## PHASE 1 ON WINDOWS

We need:

* GPU-Z (from TechPowerUp): Loads the firmware (vBIOS) of the graphics card and exports it to a ROM file that can be read by MorePowerTool.
* MorePowerTool (MPT) (from Igor'sLAB): Reads the ROM file with the firmware and handles the PP_PhmSoftPowerPlayTable registry key (delete or create new).

**GPU-Z** loads the GPU specifications and allows you to export everything to a file with ROM extension.

* To export (Graphics Card tab) use the arrow icon that comes out of a rectangle below the AMD Radeon logo, next to the text box with the BIOS version
* In the Advanced tab you have to write down the Bus number (DeviceLocation key), this number (on my system it is 3) is important later, if we need to look for the SPPT key in the Windows registry.

<Img title="GPU-Z" src="Img/GPU-Z-1.png" alt="" width="500px">
</br>
<Img title="GPU-Z" src="Img/GPU-Z-2.png" alt="" width="500px">

**MPT** is where the task of generating the SPPT key with Zero RPM disabled is performed.

* At the top, choose the GPU model you have installed; it usually shows the bus number (noted above) at the beginning of the name (3 in this case).
* It is advisable to delete the table that may already exist in the registry (Delete SPPT button).
* Load the ROM file generated with GPU-Z (Load button).
* Modify the Zero RPM option by unchecking the checkbox in 2 tabs: Features and Fan.
* Save the new settings in the SPPT registry key (Write SPPT button).

<Img title="MorePoweTool" src="Img/MorePoweTool-1.png" alt="" width="500px">
</br>
<Img title="MorePoweTool" src="Img/MorePoweTool-2.png" alt="" width="500px">

There are 2 ways to export the configuration, both ways end up in a text file with the SPPT table:

<b><u>Method 1</u></b>: Simplest method is, from MorePowerTool, click on the Save button:

* In the Save file dialog choose Save As REG (registry file).
* A text file with REG extension is generated that contains only the PP_PhmSoftPowerPlayTable registry key.
* Save the file somewhere accessible from macOS.

<b><u>Method 2</u></b>: A more complex method is to write the new SPPT table in the registry, this key is located in
`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\`

* There are some numbered keys here, choose the one that matches the bus number you have written down before: `0003\PP_PhmSoftPowerPlayTable` in my system.
* With key 0003 selected, export it as registry file (REG) or text file (TXT). File structure is different in each case. Both are valid but REG file has a more readable structure and it is the file format I recommend choosing.
* Regedit exports the entire 003 key, not just the PP_PhmSoftPowerPlayTable key as in method 1.
* Save the files somewhere accessible from macOS.

---

## PHASE 2 ON MACOS: softPowerPlayTable in SSDT

Convert the text of the Windows files to a formatted hexadecimal string so that it can be included in a SSDT (`softPowerPlayTable in SSDT`) or in config.plist (`softPowerPlayTable in DeviceProperties`), to be loaded by OpenCore.

This task is possible thanks to Anton Sychev ([klich3](https://github.com/klich3)) and the scripts he has developed to make it very easy. 

### softPowerPlayTable table from GPU ROM

Extract SPPT table from ROM: Download `upp` and run it next to the ROM file.

```bash
git clone https://github.com/sibradzic/upp.git && cd upp
python3 setup.py build
sudo python3 setup.py install
sudo python3 -m pip install click
upp --pp-file=extracted.pp_table extract -r <rom_file>.rom
```

* After running `upp`, a file called extracted.pp_table is created.
* In the Scripts folder, simply double click on `PPT_script.command`.
* The program will prompt you to drag and drop the file into the Terminal window.
* Drag and drop the default extracted.pp_table file generated by `upp` to transform it into a hexadecimal string valid for SSDT.
* The final text will appear in the Scripts/Result folder. It will have two versions, one in plain text (Results.txt) and the other as DSL (Results.dsl).
* Copy the content of the selected file and paste into your SSDT.

<u>Note</u>: With this method we have the factory default table. Zero RPM feature has not been changed in any way. **This is not what this tutorial is intended for**.

### softPowerPlayTable table from Windows registry

This allows you to bring a modified SPPT table to macOS to disable or modify the Zero RPM feature, customizing the behavior of the graphics card. In Windows phase we have saved the SPPT table as PP_PhmSoftPowerPlayTable key from the Windows registry and we can have it as 3 different files:

* MorePoweTool -> Save -> Save As REG: contains only the standalone key PP_PhmSoftPowerPlayTable (this has to be the first option)
* MorePowerTool -> Write SPPT -> open Registry Editor -> look for the key in the registry according to the instructions above -> export the entire graphics card section, including but not only PP_PhmSoftPowerPlayTable:
  * Export as REG: Registry 5 file format
  * Export as TXT: hierarchical text format (avoid it).

Either of the 3 files must be transformed into a valid hexadecimal string. This transformation can be done by the Anton Sychev's `PPT_script.command` in a very simple way.

* In the Scripts folder, double click on `PPT_script.command`.
* Script will prompt you to drag and drop the REG file onto the Terminal window.
* Remember that you can select Windows REG or TXT file to transform it into a valid hexadecimal string but REG is preferred.
* Final text will appear in the `Scripts/Result` folder. There will be 2 versions, one in plain text to be copied and pasted into an SSDT (Results.txt) and the other as a valid SSDT to be used directly (Results.dsl).

<u>Note</u>: With this method we have a custom table. Zero RPM feature has been disabled or set up in a value other than default.

### Include the hexadecimal string in the SSDT file

This is the code of a fairly common SSDT used with AMD graphics cards (SSDT folder >> SSDT-ZeroRPM-OFF.dsl). You can use it as reference.

```c++
DefinitionBlock ("", "SSDT", 2, "ETRX", "RPM", 0x00001000)
{
    External (_SB_.PCI0.PEG0.PEGP, DeviceObj)

    Scope (\_SB.PCI0.PEG0.PEGP)
    {
        Device (BRG0)
        {
            Name (_ADR, Zero)  // _ADR: Address
            Device (GFX0)
            {
                Name (_ADR, Zero)  // _ADR: Address
                Method (_DSM, 4, NotSerialized)  // _DSM: Device-Specific Method
                {
                    If ((!Arg2 || !_OSI ("Darwin")))
                    {
                        Return (Buffer (One)
                        {
                             0x03                                             // .
                        })
                    }

                    Return (Package (0x02)
                    {
 
					// Insert here the content of Result.txt file
						
                    })
                }
            }
        }
    }
}

```

SPPT table must go right here:

```c++
// Insert here the content of Result.txt file
```

Remember to set the IOReg path of your graphics card based on your system, it may be different from the code above. To know the IOReg path to the graphics card, it can be done with:

- *gfxutil* tool.
- Hackintool: PCIe tab -> Name of your device (e.g. `Navi 23 [Radeon RX 6600/6600 XT/6600M]`) -> Device Path column -> Context menu -> Copy IOReg path.<br>
This is the path on my system: `PCI0.PEG0.PEGP`. Check yours.

For better identification of the SSDT, rename it to `SSDT-ZeroRPM-OFF.aml` and don't forget to compile it to AML format. When you compile DSL file to AML, compiler formats code, fills buffer sizes and adds header with comments.

Place `SSDT-ZeroRPM-OFF.aml` in APCI folder and config.plist, restart and reload OpenCore.

### Check that the SSDT loads correctly

To see if everything is right, run IORegistryExplorer and compare what you see with this image (PP_PhmSoftPowerPlayTable as one of the properties of GFX0 or whatever graphics device is called on your system):

 ![IORegistryExplorer](Img/IOreg-gfx0-ppt.png)

Changes are being reflected in GPU temperature and fans spin. In the image below you can see temperatures when Zero RPM is disabled, when it is enabled with fans spinning at 45º and when it is enabled with factory setting (fans spinning at 60º).

- Zero RPM off: Zero RPM disabled, temperature does not exceed 35º
- Zero RPM 45º: fans start at 45º and stop at 40º
- Zero RPM on: factory setting, fans stopped below 60º, temps around 50-55º.  
  
  ![Zero RPM](Img/Zero-RPM-on-off.png)

---

## PHASE 2 ON MACOS: softPowerPlayTable in DeviceProperties

It's another way to get the SPPT table into macOS as hexadecimal string to be written into DeviceProperties of config.plist.

My personal experience is that the SSDT method (PHASE 2 ON MACOS: softPowerPlayTable in SSDT) works better. But the SSDT must be well built.

DeviceProperties method usually needs to add SSDT-BRG0.aml to work properly (you have it in the SSDT folder). As with the SSDT above, check that the IOReg path in SSDT-BRG0.aml is the one for your system.

```c++
DefinitionBlock ("", "SSDT", 2, "ACDT", "BRG0", 0x00000000)
{
    External (_SB_.PCI0.PEG0.PEGP, DeviceObj)

    Scope (\_SB.PCI0.PEG0.PEGP)
    {
        /*
         * This is a PCI bridge device present on PEGP.
         * Normally seen as pci-bridge in I/O Registry.
         */
        Device (BRG0)
        {
            Name (_ADR, Zero)
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }

            /*
             * This is an actual GPU device present on the bridge.
             * Normally seen as display in I/O Registry.
             */
            Device (GFX0)
            {
                Name (_ADR, Zero)  // _ADR: Address
            }
        }
    }
}
```

### Easy method using script

- Get one of the REG or TXT files generated in Windows.
- PPT_config-plist.sh in Scripts folder
- Open Terminal and run:<br>
`sh ./PPT_config-plist.sh reg-or-txt-file`
- Output is a long hexadecimal string that must be saved to be used in the config.plist file.

### Manual method using text editor

* Get one of the REG or TXT files generated in Windows.
* Keep the block that begins with `“PP_PhmSoftPowerPlayTable”=` deleting the rest of the text.
* Delete `«PP_PhmSoftPowerPlayTable»=hex:` leaving only the hexadecimal string made up of several lines.
* Search and replace:
  * remove commas
  * remove spaces at the beginning of lines
  * remove backslashes (\) at the end of lines
  * remove line breaks to get a single line string, use Grep in Find and Replace.

Text before looks like this (the entire string is not shown, just a part):

```
"PP_PhmSoftPowerPlayTable"=hex:a6,09,12,00,02,22,03,ae,09,00,00,22,43,00,00,83,\
00,18,00,00,00,1c,00,00,00,00,00,00,76,00,00,00,00,00,00,00,00,00,00,00,00, \
```

After it looks like this:

```
a6091200022203ae0900002243000008300180000001c0000000000007600000000000000000000000 ...
```

### OpenCore

You must know the PCI path to the graphics card, it can be done with

- *gfxutil* tool.
- Hackintool: PCIe tab -> Name of your device (e.g. Navi 23 [Radeon RX 6600/6600 XT/6600M]) -> Device Path column -> Context menu -> Copy PCI path. In my system is:<br>
`PciRoot(0x0)/Pci(0x1.0x0)/Pci(0x0.0x0)/Pci(0x0.0x0)/Pci(0x0.0x0)`.

Open the config.plist file in DeviceProperties >> Add > PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0) and adds PP_PhmSoftPowerPlayTable, its value as Data is the long text string.

![DeviceProperties](Img/DeviceProperties.png)

```html
<key>PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)</key>
<dict>
         <key>PP_PhmSoftPowerPlayTable</key>
         <data>Long string, seen as: hexadecimal in PLIST file editors and as Base64 in plain text editors</data>
</dict>
```
**Important**: Don't forget to add (ACPI folder and config.plist) the SSDT-BRG0.aml file in which you must check the IOReg path to the graphics card as explained above.

Reboot. If everything goes fine, you will see that fans are spinning all the time with a very low sound, base temperature rarely exceeds 40º (when there is not high graphics load) and test scores have not changed.

Note: slight errors in the hexadecimal string can lead to a black screen when reaching the Desktop, it is highly recommended to have an EFI that works and can boot macOS on a USB device or another disk in case of problems.

---

## April 2023 Note: macOS Ventura 13.4

There are users on macOS Ventura 13.4 who can't disable Zero RPM. Even with it properly loaded from SSDT or from the OpenCore config.plist file (verifiable using IORegistryExplorer), GPU fans are stopped most of the time and temperature ranges between 50 and 55º (approximately 10º more than in Windows), the same as without SPPT string.

There is a way to recover the lost feature. When modifying the vBIOS ROM file in Windows with MorePowerTool, instead of disabling Zero RPM (unchecking option box), it is left checked but the temperatures at which fans start and stop are modified. By default they are configured like this: Stop Temperature 50º and Start Temperature 60º.

I have tried these settings: Start Temperature 40º and Stop temperature 35. With this change, fans spin and stop with the GPU temperature oscillating between 35 and 40º. GeekBench performance is as expected.

<Img title="MorePoweTool" src="Img/MorePoweTool-3.png" alt="" width="500px">

---

## Thanks

* [Igor'sLAB](https://www.igorslab.de/en/) whose editor-in-chief is Igor Wallossek.
* [TechPowerUp](https://www.techpowerup.com/gpuz/), GPU-Z developers.
* Anton Sychev ([klich3](https://github.com/klich3)), SSDT method, `PPT_script.command` and `PPT_config-plist.sh` scripts developer. `PPT_script.command` has its own site as [PPT-table-tool](https://github.com/klich3/PPT-table-tool).
