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

def psgrun(f, p):
    inst2.write('FREQ:CW {} MHZ'.format(f))
    inst2.write('POWer {} DBM'.format(p))
    inst2.write('OUTP:STAT ON')
    sleep(1)

try:
    inst1 = rm.open_resource('GPIB0::18::INSTR')
    inst2 = rm.open_resource('GPIB0::4::INSTR')
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
        psgrun(i[0], i[1])
        inst1.write("SYST:PRES;*OPC?")
        sleep(1)
        
        inst1.write("INIT:CONT OFF")
        inst1.write('BWID:RES 10 HZ')
        inst1.write('BWID:VES 10 HZ')
        inst1.write("FREQ:SPAN 0 HZ")
        
        #source amp
        inst1.write('FREQ:CENT {} MHZ'.format(i[0]))
        inst1.write("DISP:WIND:TRAC:Y:SCAL:PDIV 20.000000 DB")
        inst1.write("SENS:POW:ATT 22.000000")
        inst1.write("DISP:WIND:TRAC:Y:RLEV 12.000000 DBM")
        inst1.write('SWE:TIME 0.001 S')
        sleep(3)
        inst1.write('CALC:MARK1:STAT ON')
        inst1.write('CALC:MARK:MAX')
        source = float(inst1.query('CALC:MARK:Y?'))

        inst1.write("SYST:PRES;*OPC?")
        sleep(1)

        inst1.write("INIT:CONT OFF")
        inst1.write('BWID:RES 10 HZ')
        inst1.write('BWID:VES 10 HZ')
        inst1.write("FREQ:SPAN 0 HZ")
        
        #noise amp
        inst1.write('FREQ:CENT 5 GHZ')
        inst1.write("DISP:WIND:TRAC:Y:SCAL:PDIV 20.000000 DB")
        inst1.write("SENS:POW:ATT 22.000000")
        inst1.write("DISP:WIND:TRAC:Y:RLEV -18 DBM")
        inst1.write('SWE:TIME 0.5 S')
        sleep(3)
        inst1.write('CALC:MARK1:STAT ON')
        inst1.write('CALC:MARK:MAX')
        noise = float(inst1.query('CALC:DATA1:COMP? MEAN'))
        sleep(8)

        print('sOURCE >> ', source, end = '\n')
        data_i = noise - source
        print('sPUR(dBc) >> ', data_i, end = '\n\n')
        lst.append(data_i)

        if highest < data_i:
            highest = data_i

    #EVALUATION
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































        
