import pyvisa
from time import sleep
import csv
import os
from os import path

#inst1 = pxa, inst2 = psg
rm = pyvisa.ResourceManager()
noerror = True
highest = -1000

def preset():
    inst1.write("SYST:PRES;*OPC?")
    inst2.write("SYST:PRES;*OPC?")
    sleep(2)

def pxainit(x):
    if x == 5:
        inst1.write('FREQ:CENT {} GHZ'.format(x))
        inst1.write('BWID:RES 10 HZ')
        inst1.write('BWID:VES 10 HZ')
        inst1.write("FREQ:SPAN 0 HZ")
        inst1.write('SWE:TIME 0.5 S')
        inst1.write("POW:ATT 22")
        inst1.write("DISP:WIND:TRAC:Y:RLEV -18 dbm")
    else:
        inst1.write('FREQ:CENT {} MHZ'.format(x))
        inst1.write('BWID:RES 10 HZ')
        inst1.write('BWID:VES 10 HZ')
        inst1.write("FREQ:SPAN 0 HZ")
        inst1.write("POW:ATT 22")
        
        inst1.write("DISP:WIND:TRAC:Y:RLEV -18 dbm")
        inst1.write('SWE:TIME 1 S')
        inst1.write('TRAC:TYPE WRIT')
        inst1.write('TRAC:TYPE MAXH')
        sleep(5)
        inst1.write("CALC:MARK:MAX")
        return float(inst1.query('CALC:MARK:Y?'))

def psgrun(f, p):
    inst2.write('FREQ:CW {} MHZ'.format(f))
    inst2.write('POWer {} DBM'.format(p))
    inst2.write('OUTP:STAT ON')
    sleep(1)

def trace():
    inst1.write('TRAC:TYPE WRIT')
    inst1.write('TRAC:TYPE MAXH')

try:
    inst1 = rm.open_resource('GPIB0::18::INSTR')
    inst2 = rm.open_resource('GPIB0::4::INSTR')
    preset()
    sleep(1)
    print(inst1.query("*IDN?"))
    print(inst2.query("*IDN?"))
except Exception as e:
    print(e)
    with open('SP_test_error.txt', 'a', newline='', encoding='utf-8') as f:
        write = csv.writer(f)
        write.writerow([str(e)])
    noerror = False

if noerror:
    freq = [[5161.25, -17.24], [161.25, -17.24], [11.25, -17.24]]
    lst = []
    for i in freq:
        print("fREQUENCY = {} MHz".format(i[0]))
        #PXA initial
        pxainit(5)

        #PSG power and frequency
        psgrun(i[0], i[1])

        #MH
        inst1.write('TRAC:TYPE WRIT')
        inst1.write('TRAC:TYPE MAXH')
        sleep(5)
        #inst1.write("CALC:MARK:MAX")
        data = str(inst1.query('CALC:MARK:Y?'))
        print('nOISE >> ', data , end = '')
        noise = float(data)

        #SOURCE AMP
        source = pxainit(i[0])
        data_i = noise - source
        lst.append(data_i)

        #PRINT
        print('sOURCE >> ', source, end = ' ')
        print('sPUR(dBc) >> ', data_i, end = '\n\n')

        #HIGHEST
        if highest < data_i:
            highest = data_i

    #EVAL
    a = 'Passed' if highest <= -93 else 'Failed'
    fields = '' if path.exists('SP_result.csv') else ['5.16125 GHz', '161.25 MHz','11.25 MHz','Result']
    lst.append(a)

    #WRITE CSV
    with open('SP_result.csv', 'a', newline='', encoding='utf-8') as f:
        write = csv.writer(f)
        if fields != '':
            write.writerow(fields)
        write.writerow(lst)
    print('Complete')
    print('Complete')
    print('Complete')
else:
    print('')
    print("Please try again.")

'''
import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())
inst = rm.open_resource('GPIB0::18::INSTR')
print(inst.query("*IDN?"))
'''

'''
st_pc = open("phasenoise_setup.txt","r")
string = st_pc.readlines()
s1 = string[0].strip().split()
s2 = string[1].strip().split()
s3 = string[2].strip().split()
'''







