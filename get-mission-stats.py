#!/usr/bin/python3

version = 0.16

#############################################################
# This monstrosity was created by crash_horror (373vFS_Crash)
# and comes without warranty of any kind,
# read the licence at the bottom.
# (https://github.com/crash-horror)
#############################################################

import os
import csv
import webbrowser
from tkinter import *
from tkinter.filedialog import askopenfilename
import tkinter.messagebox
from time import strftime


aclock = strftime("%H:%M:%S %d-%m-%Y")
interestEvent = ('S_EVENT_DEAD',
                 'S_EVENT_PILOT_DEAD',
                 'S_EVENT_EJECTION')
interestTable = ('Time', 'Initiator Coalition', 'Initiator Player',
                 'Initiator Type', 'Weapon Category', 'Weapon Name',
                 'Event', 'Target Coalition', 'Target Player',
                 'Target Type')
interestTarget = ('GROUND', 'AIRPLANE', 'HELICOPTER', 'SHIP')
pilotStatKEYS = ('PILOT', 'GROUND', 'AIRPLANE', 'HELICOPTER', 'SHIP', 'TOTAL')
coalitionStatKEYS = ('COALITION', 'GROUND', 'AIRPLANE', 'HELICOPTER', 'SHIP', 'TOTAL')

homedir = os.path.expanduser("~")
htmlpath = homedir + "/Desktop/mission_stat.html"


# cli output
# -------------------------------------------------------
def print_event_row(row):

    for key in interestTable:
        print(row[key], end=' | ')
    print()


def print_pilotstat(dictionarylist):

    print('Pilot\t\t\tGround\tPlane\tHeli\tShip\tTotal')

    for row in dictionarylist:

        if len(row['PILOT']) < 8:
            print(row['PILOT'], end='\t\t\t')
        elif len(row['PILOT']) > 15:
            print(row['PILOT'], end='\t')
        else:
            print(row['PILOT'], end='\t\t')

        for key in pilotStatKEYS[1:]:
            print(row[key], end='\t')
        print()


def print_total_losses_table(listof2dicts):

    print('Losses\tGround\tPlane\tHeli\tShip\tTotal')
    for row in listof2dicts:
        for i in coalitionStatKEYS:
            print(row[i], end='\t')
        print()


# logic
# -------------------------------------------------------
def total_losses_table(dictionarylist):

    bluelist = []
    redlist = []
    losseslist = []

    for row in dictionarylist:
        if row['Initiator Coalition'] == 'blue':
            bluelist.append(row['Initiator Group Category'])

        if row['Initiator Coalition'] == 'red':
            redlist.append(row['Initiator Group Category'])

    # blue:
    coalitionROWblue = dict.fromkeys(coalitionStatKEYS, 0)
    for el in interestTarget:
        coalitionROWblue[el] = bluelist.count(el)
    coalitionROWblue['TOTAL'] = sum(coalitionROWblue.values())
    coalitionROWblue['COALITION'] = 'Blue'
    losseslist.append(coalitionROWblue)

    # red:
    coalitionROWred = dict.fromkeys(coalitionStatKEYS, 0)
    for el in interestTarget:
        coalitionROWred[el] = redlist.count(el)
    coalitionROWred['TOTAL'] = sum(coalitionROWred.values())
    coalitionROWred['COALITION'] = 'Red'
    losseslist.append(coalitionROWred)

    return losseslist


def event_table(dictionarylist):

    deadlist = []
    eventlist = []

    for row in dictionarylist:
        if row['Event'] in interestEvent:
            deadlist.append(row)

    # for something in deadlist:  # <<=============================== DEBUG
    #     print(something)

    for rowDEAD in deadlist:
        for row in dictionarylist:
            if rowDEAD['Initiator ID'] == row['Target ID']:
                eventROW = dict(row)
                # print(row)  # <<=============================== DEBUG
                eventROW['Event'] = rowDEAD['Event']
                eventROW['Time'] = rowDEAD['Time']
                eventlist.append(eventROW)

        # remove duplicates
        fixeventlist = []
        for i in range(0, len(eventlist)):
            if eventlist[i] not in eventlist[i+1:]:
                fixeventlist.append(eventlist[i])

    return fixeventlist, deadlist


def kill_table(dictionarylist):

    playerlist = []
    pilotStatLIST = []

    for row in dictionarylist:
        if row['Initiator Player'] not in playerlist:
            playerlist.append(row['Initiator Player'])

    for pilot in playerlist:
        pilotROW = dict.fromkeys(pilotStatKEYS, 0)
        pilotROW['PILOT'] = pilot
        totalsum = 0
        for elmnt in interestTarget:
            for row in dictionarylist:
                if row['Target Group Category'] == elmnt and row['Initiator Player'] == pilot:
                    pilotROW[elmnt] += 1
                    totalsum += 1

        pilotROW['TOTAL'] = totalsum
        pilotStatLIST.append(pilotROW)

    return playerlist, pilotStatLIST


# html output
# -------------------------------------------------------
def html_coalition(listof2dicts):
    outhtmlfile = open(htmlpath, 'a')
    outhtmlfile.write("""<html>
<head>
<style type="text/css">
table.hovertable {
    font-family: verdana,arial,sans-serif;
    font-size:11px;
    color:#333333;
    border-width: 1px;
    border-color: #999999;
    border-collapse: collapse;
}
table.hovertable th {
    background-color:#c3dde0;
    border-width: 1px;
    padding: 8px;
    border-style: solid;
    border-color: #a9c6c9;
}
table.hovertable tr {
    background-color:#d4e3e5;
}
table.hovertable td {
    border-width: 1px;
    padding: 8px;
    border-style: solid;
    border-color: #a9c6c9;
}
</style>
</head>
<body>

<p align=center>
Mission Statistics @ """)
    outhtmlfile.write(aclock)
    outhtmlfile.write("""</p>
<br>
LOSSES BY COALITION:
<table class= "hovertable" id="box-table-b">
  <tr>
   <th>Coalition</th>
   <th>Ground</th>
   <th>Airplane</th>
   <th>Helicopter</th>
   <th>Ship</th>
   <th>Total</th>
  </tr>
""")

    for row in listof2dicts:
        outhtmlfile.write("""   <tr onmouseover="this.style.backgroundColor='#ffff66';" onmouseout="this.style.backgroundColor='#d4e3e5';">
""")
        for i in coalitionStatKEYS:
            outhtmlfile.write('    <td>{0}</td>'.format(row[i]))
        outhtmlfile.write('  </tr>')
    outhtmlfile.write('</table>\n<br><br>')
    outhtmlfile.close()


def html_pilot_kills(dictionarylist):
    outhtmlfile = open(htmlpath, 'a')
    outhtmlfile.write("""DESTROYED UNITS BY PILOT:
<table class= "hovertable" id="box-table-b">
  <tr>
   <th>Pilot</th>
   <th>Ground</th>
   <th>Airplane</th>
   <th>Helicopter</th>
   <th>Ship</th>
   <th>Total</th>
  </tr>
""")

    for row in dictionarylist:
        outhtmlfile.write("""   <tr onmouseover="this.style.backgroundColor='#ffff66';" onmouseout="this.style.backgroundColor='#d4e3e5';">
""")
        for j in pilotStatKEYS:
            outhtmlfile.write('    <td>{0}</td>'.format(row[j]))
        outhtmlfile.write('  </tr>')
    outhtmlfile.write('</table>\n<br><br>')
    outhtmlfile.close()


def html_event_table(dictionarylist):
    outhtmlfile = open(htmlpath, 'a')
    outhtmlfile.write("""EVENT TABLE:
 <table class= "hovertable" id="box-table-b">
  <tr>
   <th>Time</th>
   <th>Coalition</th>
   <th>Player</th>
   <th>Type</th>
   <th>Weapon Category</th>
   <th>Weapon Name</th>
   <th>Event</th>
   <th>Target Coalition</th>
   <th>Target Player</th>
   <th>Target Type</th>
  </tr>
""")
    for row in eventTABLElist:
        outhtmlfile.write("""   <tr onmouseover="this.style.backgroundColor='#ffff66';" onmouseout="this.style.backgroundColor='#d4e3e5';">
""")
        for k in interestTable:
            outhtmlfile.write('    <td>{0}</td>'.format(row[k]))
        outhtmlfile.write('  </tr>')
    outhtmlfile.write('</table>\n</body>\n</html>')
    outhtmlfile.close()


# start tkinter (hidden)
# -------------------------------------------------------
root = Tk()
if sys.platform == 'win32':
    root.iconbitmap(default='favicon.ico')
root.withdraw()


# set the files
# -------------------------------------------------------
openafile = askopenfilename()

outhtmlfile = open(htmlpath, 'w')
outhtmlfile.close()

csvfile = open(openafile, newline='')
dict_read_iterator = csv.DictReader(csvfile)
dictREAD = list(dict_read_iterator)


# (logic & cli) function calls
# -------------------------------------------------------
# for something in dictREAD: # <<=============================== DEBUG
#   print(something)

eventTABLElist, totaldeadTABLElist = event_table(dictREAD)
totalKILLSlist = total_losses_table(totaldeadTABLElist)
PLAYlist, KILLlist = kill_table(eventTABLElist)

for i in eventTABLElist:
    print_event_row(i)

print('-'*80)

# list sorting
# -------------------------------------------------------
SORTED_totalKILLSlist = sorted(totalKILLSlist, key=lambda k: k['TOTAL'], reverse=True)
SORTED_KILLlist = sorted(KILLlist, key=lambda k: k['TOTAL'], reverse=True)

print_pilotstat(SORTED_KILLlist)
print('-'*80)
print_total_losses_table(SORTED_totalKILLSlist)
print('-'*80)


# html generator function calls
# -------------------------------------------------------
html_coalition(SORTED_totalKILLSlist)
html_pilot_kills(SORTED_KILLlist)
html_event_table(eventTABLElist)


# message & open in browser & exit
# -------------------------------------------------------
tkinter.messagebox.showinfo("Success!", "The file: 'mission_stat.html' has been generated at your desktop!")
webbrowser.open(htmlpath)
exit()
root.mainloop()




# scratch pad
# -------------------------------------------------------
"""
TODO:
** make AI kills distinguishable for coalitions
"""
# licence
# -------------------------------------------------------
"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org>
"""
