 /* Check your IOReg path, it may be different */

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

