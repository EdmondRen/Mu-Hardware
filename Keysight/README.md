Working in Ubuntu:

1. Install Keysight IO library and driver: https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html
2. Install pyvisa and pyusb: pip install pyusb pyvisa
3. Configure the pyvisa to use IVI visa backend. Add the Path to VISA library in .pyvisarc file:
    vim ~/.pyvisarc   
    [Paths]   
    VISA library: /opt/keysight/iolibs/libktvisa32.so   

4. Restart computer

Basic test exemple:


``` python
  import pyvisa
  rm = pyvisa.ResourceManager()
  # /rm = pyvisa.ResourceManager("/opt/keysight/iolibs/libktvisa32.so")
  print(rm.visalib)
  print(rm.list_resources()) # Prints "()" => No instruments found!