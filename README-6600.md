# XFX RX 6600 XT graphics card on macOS

### Preface

Although graphics cards assembled by XFX have negative comments in Hackintosh forums by having custom BIOS that can be more problematic for macOS that other brands, I have installed a XFX QICK 308 AMD Radeon RX 6600 XT 8GB in Monterey 12.2.1 and the result has been excellent, installation was very simple and performance is much higher than that of the previous card, RX 580 8GB.

This card is one of the 6600 XT cheapest even though it can still be considered expensive compared to what would be logical in other circumstances (shortage of components and mined cryptocurrencies).

Main components of my computer are Z390 Aorus Elite board and Intel i9-9900K CPU.

Current macOS status of AMD 6000 series graphics cards is:

<table>
    <tr><td>Working on macOS</td></tr>
    <tr><td>Family Navi 21</td><td>6800, 6800 XT and 6900 XT (since Big Sur 11.4)</td></tr>
    <tr><td>Family Navi 23</td><td>6600 and 6600 XT (since Monterey 12.1)</td></tr>
    <tr><td>NOT working on macOS</td></tr>
    <tr><td>Family Navi 22</td><td>6700 XT</td></tr>
    <tr><td>Family Navi 24</td><td>6400, 6500 and 6500 XT</td></tr>
</table>

Of course 6800 and 6900 series are clearly more powerful than the 6600 but their current market price is very high. 6600 XT has higher performance than 6600.

The card is long size but no longer than the XFX RX 580 it will replace. Surprisingly, it's even slightly lighter, probably because of the metal housing that the RX 580 incorporates. Requires 8 pin power connector and recommended power supply at least 600-650W. It has 4 DisplayPort ports and 1 HDMI port.

### Installation

Physical placement of the card does not deserve comment, it's like any other PCI-e slot card.

Installation on macOS is very simple. The same EFI with OpenCore 0.7.8 (Lilu and WhateverGreen included) that worked with the RX 580 works for the 6600 XT with a single change: add `agdpmod=pikera` in boot-args to prevent the screen from going black on the desktop.

The card is well recognized in System profile.

### Working on macOS

Overall performance is very good, smooth, with 2560x1440 resolution at 60Hz on a 4K monitor. Score in GeekBench 5 test is around 60% higher than the RX 580 (around **80000** vs **50000**).

### Working on Windows

Many Hackintosh users have double booting with Windows. Here the impressions are also very good, system has kept the same AMD drivers without requiring update.

Score in the Geeks3D FurMark test is double with the RX 6600 XT than with the RX 580 (approx. **6100** vs **3000**).

### Temperature sensor

Starting with the Radeon VII model, it is necessary to use kexts to read the temperature of AMD graphics cards since macOS stopped exposing that data directly. This also applies to the 6000 series. To know the temperature of the card you can use [RadeonSensor](https://github.com/ChefKissInc/RadeonSensor). It consists of 3 elements:

- Radeon sensor.kext: Lilu plugin to read card temperature
- SMCRadeonGPU.kext: to export data via VirtualSMC to monitoring tools such as iStat Menus
- RadeonGadget.app: to display the temperature in the menu bar, it requires RadeonSensor.kext only.

Note: SMCRadeonGPU.kext has to go after RadeonSensor.kext in the config file.plist of OpenCore and of course both after Lilu and VirtualSMC.

I have tested these 2 extensions together and they seem to work well, iStat Menus adds the temperature of the 6600 XT as one more sensor to display in the menu bar.

### Resizable BAR (ReBAR)

AMD Radeon 6600 cards support ReBAR. To activate this feature you must:

- Enable it in BIOS menu (usually next to Above 4G Decoding option, ReBAR is displayed when enabling this option)
- Set config file.plist in order for OpenCore to boot with ReBAR enabled, you have to set the value of Boot >> Quirks >> ResizeAppleGpuBars=0 (instead of -1, default value).

**Note**: UEFI >> Quirks >> ResizeGpuBars must always be -1.

I have tested the card with ReBAR on and off and I have not noticed any difference. GeekBench 5 test scores on macOS and FurMark on Windows have been virtually identical.
It is likely that with a CPU of 10th generation or newer and games of big graphic demand the performance will improve with ReBAR enabled but, at least in my system, there is no gain in it.

---

### AMD 5000 and 6000 performance issue in Monterey 12.3 (fixed in Monterey **12.3.1** and newer)

The release of macOS Monterey 12.3 has broken the operation of Radeon 5000 and 6000 families, not in all cases but in quite a few of them judging by comments posted on the forums. This problem has also happened on real Macs but it seems to be more much more frequent on Hackintosh. 5500, 5700, 6800 and 6900 models (XT and non XT) have been most affected. 6600 models (XT and non XT) seem to be free of the issue that manifests itself in a very evident drop in graphic performance after updating to 12.3, in some cases the system becomes unusable and in other cases a big part of the graphic power is simply lost.

My GPU is RX 6600 XT so it has not been affected by this issue.

Solutions have been proposed to fix this. The simplest is to add in DeviceProperties of config.plist some properties that set Henbury framebuffer for each of the 4 ports of this GPU. By default Radeon framebuffer (ATY,Radeon) is loaded. But, in `AMDRadeonX6000Framebuffer.kext >> Contents >> Info.plist`, AMDRadeonNavi23Controller has "ATY,Henbury" and 6600 series are Navi 23. This is why this framebuffer is specifically proposed.

The patch is added in this way: 

```xml
<key>DeviceProperties</key>
    <dict>
        <key>Add</key>
        <dict>
            <key>PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)</key>
            <dict>
                <key>@0,name</key>
                <string>ATY,Henbury</string>
                <key>@1,name</key>
                <string>ATY,Henbury</string>
                <key>@2,name</key>
                <string>ATY,Henbury</string>
                <key>@3,name</key>
                <string>ATY,Henbury</string>
            </dict>
        </dict>
        <key>Delete</key>
        <dict/>
    </dict>
```

Note: PCI path to the GPU may be the same on your system but it is convenient to check it with Hackintool (app) or `gfxutil` (Terminal utility).

#### Patch and Zero RPM

Although my GPU has not been affected by this Monterey 12.3 issue, I have tried the patch motivated by curiosity to check if the card works differently (better or worse). When booting with the patch, it gets my attention that the GPU temperature is, with idle system, 10-15º below the usual 50º. The cause is in the deactivation of the Zero RPM feature: fans spin all the time with a small drawback that is the noise generated (very low volume, almost imperceptible except in quiet environment).

Graphics performance is good with the patch. GeekBench 5 metal scores are lower but other benchmarks such as Unigine Valley or GFXBench Metal are almost identical. Maximum temperature when forcing the GPU has not changed, about 80º, the same as without the patch. But basic temperature at iddle system ranges from 35 to 40º. Sensations when performing common tasks on macOS are the same (excellent) with or without patch. 

Unexpectedly, I have seen a way to disable Zero RPM in macOS, it is easier to implement than creating sPPT in Windows and its subsequent transfer to macOS.

It is up to you to choose what you prefer.

- Without patch: base temperature is around 50º, fans are usually stopped and GeekBench 5 score is higher.
- With patch: base temperature is below 40º, fans are always running although the noise produced is very low but GeekBench 5 score is lower.

#### Framebuffers

This patch can be applied to the other Radeon models affected by the Monterey 12.3 issue to fix that bad behaviour and not only to disable Zero RPM.

Framebuffers available in AMDRadeonX6000Framebuffer.kext >> Contents >> Info.plist.

<table>
    <tr><td><b>5700</b> - Navi 10 - AMDRadeonNavi10Controller</td></tr>
    <tr><td>device-id: 0x73101002 0x73121002 0x73181002 0x73191002 0x731A1002 0x731B1002 0x731F1002 0x73BF1002</td></tr>
    <tr><td>framebuffer: ATY,Adder / ATY,Ikaheka</td></tr>
    <tr><td height="24"></td></tr>
    <tr><td><b>5600</b> - Navi 12 - AMDRadeonNavi12Controller</td></tr>
    <tr><td>device-id: 0x73601002 0x73621002</td></tr>
    <tr><td>framebuffer: ATY,Sunbeam</td></tr>
    <tr><td height="24"></td></tr>
    <tr><td><b>5500</b> - Navi 14 - AMDRadeonNavi14Controller</td></tr>
    <tr><td>device-id: 0x73401002 0x73411002 0x73431002 0x73471002 0x734F1002</td></tr>
    <tr><td>framebuffer: ATY,Python / ATY,Keelback / ATY,Boa</td></tr>
    <tr><td height="24"></td></tr>
    <tr><td><b>6800</b> and <b>6900</b> - Navi 21 - AMDRadeonNavi21Controller</td></tr>
    <tr><td>device-id: 0x73A01002 0x73A21002 0x73A31002 0x73AB1002 0x73AE1002 0x73AF1002 0x73BF1002</td></tr>
    <tr><td>framebuffer: ATY,Belknap / ATY,Carswell / ATY,Deepbay</td></tr>
    <tr><td height="24"></td></tr>
    <tr><td><b>6600</b> - Navi 23 - AMDRadeonNavi23Controller</td></tr>
    <tr><td>device-id: 0x73E31002 0x73FF1002 0x73E01002</td></tr>
    <tr><td>framebuffer: ATY,Henbury</td></tr>
</table>
