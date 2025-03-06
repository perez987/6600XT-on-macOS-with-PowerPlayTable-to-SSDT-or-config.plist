#!/bin/bash

#█▀ █▄█ █▀▀ █░█ █▀▀ █░█
#▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

#Author: <Anton Sychev> (anton at sychev dot xyz) 
#win-reg-to-hex-hash (c) 2023 
#Created:  2024-02-08 11:04
#Desc: extract PPT from reg export file and convert to hex hash format 
#       for implement in kext or directly in your config.plist file
#
#<key>PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)/Pci(0x0,0x0)</key>
#<dict>
#         <key>PP_PhmSoftPowerPlayTable</key>
#         <data>RESULT HAST GOES HERE</data>
#</dict>
#
#--------------------------------
#
#Usage: 
#   1) Print result to console just simply run and copy / paste
#       ./win-reg-to-hex-hash.sh <input_file.reg>
#       ./win-reg-to-hex-hash.sh /path/to/file.reg
#   2) Save result to file
#       ./win-reg-to-hex-hash.sh <input_file.reg> > output.txt



export LC_ALL=C

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <file>"
    echo -e "\n\n-------\nSample file content: Windows Registry Editor Version 5.00\n\n[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0001]\n\"DriverDesc"="AMD Radeon RX 6900 XT\"\n\"ProviderName\"=\"Advanced Micro Devices, Inc.\"\n\"DriverDateData\"=hex:00,00,61,20,9d,ba,d9,01\"\n-------\n"
    exit 1
fi

file_path=$1

if [ ! -f "$file_path" ]; then
    echo "Error: File '$file_path' not found."
    exit 1
fi

file_content=$(cat "$file_path")

PPT=""
prev_line=""

BLOCK=$(echo -e "$file_content" | grep -A 5000 '\"PP_PhmSoftPowerPlayTable\"=hex:.*')

while IFS= read -r line; do
    if [[ "$line" == *"["* ]]; then
        break
    fi
    
    PPT+="$line"$'\n'  # Use $'\n' to preserve newlines
    prev_line="$line"
done <<< "$BLOCK"

formatted_content=$(echo "$PPT" | sed 's/ - / /g')
formatted_content=$(echo "$formatted_content" | sed -e 's/^[^=]*=hex://; s/,//g; s/,\\//g; s/\\//g' | tr '[:lower:]' '[:upper:]')
formatted_content=$(echo "$formatted_content" | tr -d '[:space:]') 

echo "$formatted_content"
