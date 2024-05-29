First_script.py: 
This script analyses the given data and creates output files that contain only UDDS profiles.



Second_script.py:  
This script takes buffer time as an input from the user. Based on this buffer time, the script will then create IMFs using the PyEMD library. The value of Vc(t) is calculated by subtracting the highest IMF from the original voltage value signal. This value of Vc(t) is then used to extract features, which will ultimately be used as input into LSTM.  






