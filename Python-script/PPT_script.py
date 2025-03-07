"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
PPT_script.py (c) 2024 
Created:  2024-03-04 20:11:00 
Desc: Creation of PPT Power Play Tables from win registry exported files
"""


import os, sys, re, json, binascii, shutil, subprocess
from Scripts import run, utils
from collections import OrderedDict
from datetime import datetime

class PPT_script:
    def __init__(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.output = "./Results"
        self.w = 120
        self.h = 40
        if os.name == "nt":
            self.w = 120
            self.h = 30
            os.system("color") # Run this once on Windows to enable ansi colors
        self.u = utils.Utils("PPT to DSL Tool")
        self.file_path = None
        self.file_data = None
        self.file_type = None
        self.cs = u"\u001b[32;1m"
        self.ce = u"\u001b[0m"
        self.bs = u"\u001b[36;1m"
        self.rs = u"\u001b[31;1m"
        self.nm = u"\u001b[35;1m"

        print(self)

    def show_error(self,header,error):
        self.u.head(header)
        print("")
        print(str(error))
        print("")
        return self.u.grab("Press [enter] to continue...")

    def create_dsl(self, input_data):
        '''
        Create a DSL file with the input data
        @param input_data: The data to include in the DSL file
        '''

        dsl_file_content = '''
DefinitionBlock ("", "SSDT", 2, "DRTNIA", "AMDGPU", 0x00001000)
{	
    External (_SB_.PCI0, DeviceObj)
    External (_SB_.PCI0.PEG0.PEGP, DeviceObj) // <--- This is the device path for the GPU change it if you have a different path

    Scope (\_SB.PCI0.PEG0.PEGP)               // <--- This is the device path for the GPU change it if you have a different path
    {
        If (_OSI ("Darwin"))
        {
            Method (_DSM, 4, NotSerialized)  // _DSM: Device-Specific Method
            {
                Local0 = Package ()
                {
					
				    ## PPT Data

				}
                DTGP (Arg0, Arg1, Arg2, Arg3, RefOf (Local0))
                Return (Local0)
            }
        }
    }

    Scope (\_SB.PCI0)
    {
        Method (DTGP, 5, NotSerialized)
        {
            If ((Arg0 == ToUUID ("a0b5b7c6-1318-441c-b0c9-fe695eaf949b") /* Unknown UUID */))
            {
                If ((Arg1 == One))
                {
                    If ((Arg2 == Zero))
                    {
                        Arg4 = Buffer (One)
                            {
                                 0x03
                            }
                        Return (One)
                    }

                    If ((Arg2 == One))
                    {
                        Return (One)
                    }
                }
            }

            Arg4 = Buffer (One)
                {
                     0x00
                }
            Return (Zero)
        }
    }
}
'''
        return dsl_file_content.replace("## PPT Data", input_data)
        

    def write_to_file(self, file_name, data):
        '''
        Write the data to a file
        @param file_name: The name of the file to write to
        @param data: The data to write to the file
        '''
        if not os.path.exists(self.output): os.mkdir(self.output)
        out_full_path = f"{self.output}/{file_name}"
        with open(out_full_path, "w") as f:
            f.write(data)            
        print("File generated at: ", out_full_path)


    def parse_file_data(self):
        if not self.file_path or not self.file_data: return

        result = [
            "\t\"PP_PhmSoftPowerPlayTable\",",
            "\tBuffer ()\n\t{\n"
        ]

        if self.file_type == "binary":
            self.u.head("Binary PPTable file -> Parsing Data....")

            formatted_output = ', '.join([f'0x{byte:02X}' for byte in self.file_data])
            formatted_output_list = [formatted_output[i:i+96] for i in range(0, len(formatted_output), 96)]

            # Imprimir las listas en columnas
            for column in formatted_output_list:
                result.append(f"\t\t\t{column}")

        if self.file_type == "reg":
            self.u.head("Windows Registry file -> Parsing Data....")
            
            #patron = re.compile(r'PP_PhmSoftPowerPlayTable"=hex:.*?(?=\n\s*\n|$)', re.DOTALL)
            patron = re.compile(r'PP_PhmSoftPowerPlayTable"=hex:(.*?)(?=\n\s*\n|$)', re.DOTALL)
            found = patron.findall(self.file_data)

            all_parts = []

            for block in found:
                b_pro = block.strip()
                b_pro = b_pro.replace(',\\', ',').replace('\n', '').replace('\r', '').replace(' ', '')
                b_pro = b_pro.split(',')
                all_parts.append(b_pro)
                all_parts = [f"0x{item}" for sublist in all_parts for item in sublist]
                all_parts = [all_parts[i:i + 16] for i in range(0, len(all_parts), 16)]
                all_parts = [', '.join(item) + ',' if i < len(all_parts) - 1 else ', '.join(item) for i, item in enumerate(all_parts)]

            for column in all_parts:
                result.append(f"\t\t\t{column}")

        
        if self.file_type == "txt":
            self.u.head("Windows Text Registry file -> Parsing Data....")

            patron = re.compile(r'PP_PhmSoftPowerPlayTable.*?(\n\s*\n|$)', re.DOTALL)
            match = patron.search(self.file_data)

            if match:
                b_pro = match.group(0)
                all_parts = []
                
                #quiero separar por lineas eitando las tres primeras
                b_pro = b_pro.split("\n")[3:]
                for line in b_pro:
                    line = line.replace(" - ", " ").replace("  ", "\/\/").replace("\t", "")
                    line = re.sub(r'^[0-9a-fA-F]{8}\s*|   ', '', line)
                    line = line.replace("\/\/ ", "")
                    line = re.sub(r'\\\/\\\/.*', '', line)
                    line = line.split(" ")
                    
                    #quitar '\r', '', " " añadir 0x al principio
                    line = [f"0x{item.upper()}" for item in line if item not in ["", " ", "\r"]]

                    #agregar todos los elementos dentro de all_parts por separadaos
                    for i in line:
                        all_parts.append(i)

                all_parts = [all_parts[i:i + 16] for i in range(0, len(all_parts), 16)]
                all_parts = [', '.join(item) + ',' if i < len(all_parts) - 1 else ', '.join(item) for i, item in enumerate(all_parts)]


                for column in all_parts:
                    result.append(f"\t\t\t{column}")

            else:
                return self.show_error("No PP_PhmSoftPowerPlayTable found in the file")


        result.append("\n\t}\n")

        #result join with \n
        result = "\n".join(result)
        
        self.write_to_file("Result.txt", result)
       
        dsl_file_conente = self.create_dsl(result)
        self.write_to_file("Result.dsl", dsl_file_conente)

    
        print("")
        print("Done.")
        print("")
        self.u.grab("Press [enter] to return...")

    
    def main(self,path=None):
        if path is None:
            self.u.resize(self.w, self.h)
            self.u.head()
            print("")
            print("NOTE:  All output files are saved to the 'Results' folder.")
            print("")
            print("Q. Quit")
            print("")
            print("Please drag and drop a Windows registry dump <file>.<txt|reg> on of type ")
            print("or binary <file>.<pp_table> file here to continue.")
            menu = self.u.grab("Dropped File: ")
            if not len(menu): return
            if menu.lower() == "q": self.u.custom_quit()
        else:
            menu = path
        # Check the path
        path = self.u.check_path(menu)
        try:
            # Ensure we have a valid path
            if not path: raise Exception("{} does not exist!".format(menu))
            
            if os.path.isdir(path): path = os.path.join(path,"Contents","input.txt")
            if not os.path.exists(path): raise Exception("{} does not exist!".format(path))
            
            if not os.path.isfile(path): raise Exception("{} is a directory!".format(path))
        except Exception as e:
            return self.show_error("Error Selecting Target",e)
        try:
            with open(path,"rb") as f:
                raw = f.read().replace(b"\x00",b"").decode("utf-8",errors="ignore")
                
                f.seek(0)
                if re.search("Windows Registry|\[HKEY\_LOCAL|\"=\"", raw):
                    print("parsing reg file detected")
                    file_type = "reg"
                    file_data = raw
                elif re.search("REG_SZ|REG_BINARY", raw):
                    print("parsing txt file detected")
                    file_type = "txt"
                    file_data = raw
                else: 
                    print("parsing pp_table file detected")
                    file_type = "binary"
                    file_data = f.read()
                    
        except Exception as e:
            return self.show_error("Error Loading {}".format(os.path.basename(path)),e)
        
        self.file_path = path
        self.file_data = file_data
        self.file_type = file_type
        self.parse_file_data()

if __name__ == '__main__':
    u = PPT_script()
    path = sys.argv[1] if len(sys.argv)>1 else None
    while True:
        u.main(path=path)
        path = None # Prevent a loop on exception
