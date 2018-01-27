#! python3

import os
import subprocess
import sys
import shlex
import time
import re
import ctypes

#Config Values
GPUIndex = sys.argv[1]

workingDir = "C:\\Users\ADE\ethWatchdog"

def executeSubprocess(commandString):
    args = shlex.split(commandString, posix=0)
    process = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return process

def readLastLine(filePath, mode):
    outputFile = open(filePath, mode)
    outputLines = outputFile.readlines()
    outputFile.close()
    lastLine = outputLines[len(outputLines)-1]
    return lastLine

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin(): 

    restartCounter = 0
    while (restartCounter <100):

        i = 0
        while True:
            i = i + 1
    
            #Get the current clock, and power settings
            nvidiaSMI = executeSubprocess(f'nvidia-smi -i {GPUIndex} -q')
            try:
                #print('timout communicate started')
                output = nvidiaSMI.communicate(timeout=15)
                #print('timeout communicate ended')
                nvidiaSMI.terminate()

            except TimeoutExpired:
                #print(' communicate started')
                output = nvidiaSMI.communicate()
                #print(' communicate ended')
                nvidiaSMI.terminate()

            time.sleep(5)
                       
            
            # Get Power Readings_
            powerRegex = re.compile(r'\S*(?=\sW\\r\\n\s+Power Limit)')
            currentPower = 'No power output match'
            matchPower = powerRegex.search(str(output[0]))
            if matchPower:
                currentPower = matchPower.group(0)

            # Get Clock Readings
            clockRegex = re.compile(r'\S+(?=\sMHz\\r\\n\s+SM)')
            currentClock = 'No clock output match'
            matchClock = clockRegex.search(str(output[0]))
            if matchClock:
                currentClock = matchClock.group(0)

            # Get Memory Readings
            memoryRegex = re.compile(r'\S+(?=\sMHz\\r\\n\s+Video)')
            currentMemory = 'No memory output match'
            matchMemory = memoryRegex.search(str(output[0]))
            if matchMemory:
                currentMemory = matchMemory.group(0)
            



            open(f'{workingDir}\\nvidiaInfo{GPUIndex}.log', 'w').write(f'{currentClock},{currentMemory},{currentPower}')
            print(f'{workingDir}\\nvidiaInfo{GPUIndex}.log')

'''
else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'C:\\Users\ADE\ethWatchdog\ethWatch.py {GPUIndex} {memoryOffset}', None, 1)
'''