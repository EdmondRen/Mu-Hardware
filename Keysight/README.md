# VISA setup in Ubuntu:

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
```

# File description

* Template-funcgen.ipynb:
  * Template for generating pulse with the function generator
* Template-scope.ipynb:
  * Template for acquiring waveform from the scope
* Template-scope-par_scan.ipynb
  * Template for scanning parameters with the scope
* Scope_acquisation.ipynb:
  * Tool for recording waveform with the scope
