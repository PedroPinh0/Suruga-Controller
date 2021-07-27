import sys
import os
import time
#import pyvisa as visa
import numpy as np

rm=visa.ResourceManager()
rm.list_resources()
dev = rm.open_resource('ASRL9::INSTR')
dev.write_termination = '\r'
dev.read_termination = '\r'
dev.baud_rate = 9600
dev.query('*IDN?')
dev.close()

inst_xy = visa.ResourceManager().open_resource('ASRL9::INSTR')
inst_z = visa.ResourceManager().open_resource('ASRL8::INSTR')
inst_xy.write_termination='\r'
inst_xy.read_termination='\r'
inst_z.write_termination='\r'
inst_z.read_termination='\r'
inst_xy.baud_rate = 9600
inst_z.baud_rate = 9600

def step(axis, step_meters, direction):
    #print values
    str_dir = 'CCW'
    str_dir_z = 'CW'

    if direction == 1:
        str_dir = 'CW'
        str_dir_z = 'CCW'

    if abs(step_meters)<50e-9:
        speed='0'
    elif abs(step_meters)<100e-9:
        speed='1'
    elif abs(step_meters)<500e-9:
        speed='2'
    elif abs(step_meters)<1e-6:
        speed='3'
    elif abs(step_meters)<5e-6:
        speed='4'
    elif abs(step_meters)<10e-6:
        speed='5'
    elif abs(step_meters)<100e-6:
        speed='6'
    elif abs(step_meters)<500e-6:
        speed='7'
    elif abs(step_meters)<1e-3:
        speed='8'
    else:
        speed='9'

    #Controlador-> 1 pulso = 1 micron
    #Pág. 72 do manual - position C--> 1 step = 10 nm
    step = round(step_meters/10e-9);
    step_str = str(step);

    if float(step) != 0.001:
        #driv_div = str(0)
        if axis == 1:
            cmd = 'AXI1:selsp ' + speed + ' :PULS ' + step_str + ':GO ' + str_dir + ':DW'
            print (cmd)
            inst_xy.write(cmd)

        if axis == 2:
            cmd = 'AXI2:selsp ' + speed + ' :PULS ' + step_str + ':GO ' + str_dir + ':DW'
            print(cmd)
            inst_xy.write(cmd)

        elif axis == 3:
            cmd = 'AXI1:selsp ' + speed + ' :PULS ' + step_str + ':GO ' + str_dir_z + ':DW'
            print(cmd)
            inst_z.write(cmd)



# X -> 1
# Y -> 2
# Z -> 3
# DIRECTION -> 1 OR -1
z_step = 50e-6

max_limit = 50e-6
if z_step > max_limit:
    print("!!!")
else:
    step(3,z_step,-1) # Z-axis, Step, direction (-1,1)



#CLOSE PORTS
inst_xy.close()
inst_z.close()
