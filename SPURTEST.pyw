import tkinter as tk
import pyvisa
from time import sleep
import csv
import os
from os import path
from datetime import datetime, timedelta

rm = pyvisa.ResourceManager()
noerror = True

try:
    inst1 = rm.open_resource('GPIB0::18::INSTR')
    inst2 = rm.open_resource('GPIB0::4::INSTR')
except Exception as e:
    with open('SP_test_error.txt', 'a', newline='', encoding='utf-8') as f:
        write = csv.writer(f)
        write.writerow([str(e)])
    noerror = False

def psgrun(f, p):
    inst2.write('FREQ:CW {} MHZ'.format(f))
    inst2.write('POWer {} DBM'.format(p))
    inst2.write('OUTP:STAT ON')
    sleep(1)
    
def Spurtest(S):
    inst1 = rm.open_resource('GPIB0::18::INSTR')
    inst2 = rm.open_resource('GPIB0::4::INSTR')
    freq = [[5161.25, -17.24], [161.25, -17.24], [11.25, -17.24]]
    lst = [S]
    highest = -1000

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
        sleep(3)#3 
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
        sleep(3)#3 
        inst1.write('CALC:MARK1:STAT ON')
        inst1.write('CALC:MARK:MAX')
        noise = float(inst1.query('CALC:DATA1:COMP? MEAN'))
        sleep(2)#2

        print('sOURCE >> ', source, end = '\n')
        data_i = noise - source
        print('sPUR(dBc) >> ', data_i, end = '\n\n')
        lst.append(data_i)
        if data_i > 50:
            ERROR_CUT()
        if highest < data_i:
            highest = data_i
    a = 'Passed' if highest <= -93 else 'Failed'
    lst.append(a)
    return lst

def Insert_SN():
    global SN
    global r
    try:
        SN = int(entry.get())
        r = Spurtest(SN)
        word  = 'SN: ' + str(SN)
        b = 1
        for i in [[5161.25, -17.24], [161.25, -17.24], [11.25, -17.24]]:
            word = word + "\n      {} MHz: {} dBc".format(i[0],'%.2f' %r[b])
            b = b + 1
        word  = word + '\n      result: ' + str(r[-1])
        print(word)
        text.delete('1.0', tk.END)
        text.insert(tk.INSERT, word)
    except Exception as e:
        print(e)
        text.delete('1.0', tk.END)
        text.insert(tk.INSERT, "CANNOT TEST")
        text.insert(tk.INSERT, "\nERROR!")
        
def Save_Data():
    global r
    try:
        #DATE 
        entry.delete(0, "end") 
        entry.insert(tk.INSERT, SN)
        a = datetime.now()
        year_month_day = "{}_{}_{}".format(a.year, a.month, a.day)
        if r[1] != variable.get():
            r.insert(1, variable.get())
            r.insert(2, a)
        if len(r) < 6:
            ERROR_CUT()
            
        #WRITE
        try:
            fields = '' if path.exists('Z:\\Patchradanai\\New folder\\orion\\log\\spurdata\\SP_log.csv') else ['SN', 'DATE','Tester', '5.16125 GHz', '161.25 MHz','11.25 MHz','Result']
            with open('Z:\\Patchradanai\\New folder\\orion\\log\\spurdata\\SP_log.csv', 'a', newline='', encoding='utf-8') as f:
                write = csv.writer(f)
                if fields != '':
                    write.writerow(fields)
                write.writerow(r)
        except:
            pass
        with open('Z:\\Patchradanai\\New folder\\orion\\log\\spurdata\\Spur_{}_{}_{}.txt'.format(year_month_day, r[0], r[-1]), 'a', newline= '', encoding='utf-8') as f:
            f.write('SN: {}'.format(SN))
            f.write('\n')
            f.write('Tester: {}'.format(r[1]))
            f.write('\n')
            f.write('Date: {}'.format(r[2]))
            f.write('\n')
            f.write('Result: {}'.format(r[-1]))
            f.write('\n')
            for i in [[5161.25, -17.24], [161.25, -17.24], [11.25, -17.24]]:
                f.write('{} MHz: {} dBc'.format(i[0], r.pop(3)))
                f.write('\n')
                
    except Exception as e:
        print(e)
        text.delete('1.0', tk.END)
        text.insert(tk.INSERT, "SAVE FAILED")
        text.insert(tk.INSERT, "\nCHECK DATA LOG!")

root = tk.Tk(className=' Automatic Spurtest')
root.geometry("500x500")
root['bg']='black'

frame = tk.Frame(root)
frame.pack(side = 'right')
bottomframe = tk.Frame(root)
bottomframe.pack(side = 'bottom')

n = open("operator.txt", "r")
choices = n.read().split('\n')
variable = tk.StringVar(root)
variable.set('Select your name')
c = tk.OptionMenu(root, variable, *choices)
c.pack()

tk.Label(root, text='Serial Number', font=("Arial", 21),bg='black', fg='#e4e809').pack(side = 'top')
entry = tk.Entry(root, font=("Arial", 21))
entry.pack(side = 'top')

text = tk.Text(root ,font=("Arial", 21), spacing1 = 5,bg='black', fg='#e4e809')
text.pack()
b1 = tk.Button(frame, text="TEST", width=5, font=("Arial", 21), command = Insert_SN, bg='#a30018', fg='white')
b1.pack(side = 'top')
b2 = tk.Button(frame, text="SAVE", width=5, font=("Arial", 21), command = Save_Data, bg='#00b840', fg='white')
b2.pack(side = 'bottom')

if not noerror:
    text.delete('1.0', tk.END)
    text.insert(tk.INSERT, "NO CONNECTION")

root.mainloop()
