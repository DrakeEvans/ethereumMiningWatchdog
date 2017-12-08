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
        
workingDir = "C:\\Users\Miner\ethWatchdog"

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

restartCounter = 0
while (restartCounter <100):

    ethminerLogName = f'{workingDir}\ethminerOutput{GPUIndex}.log'

    #Start Main Subprocess and write output to file
    arg = shlex.split(f'C:\program files\ethminer\ethminer.exe --farm-recheck 1000 -U --cuda-devices {GPUIndex} -M -S us1.ethermine.org:4444 -FS us2.ethermine.org:4444 -O 0x742a902f4a6c6aa1f59a4ef0b7d72fec6717f207.MINER', posix=0)
    print(arg)
    ethminer = subprocess.Popen(arg, stderr=subprocess.STDOUT, stdout=open(ethminerLogName, 'a'))
    print('Subprocess Started')


    #Sleep while ethminer subprocess begins, impossible to access file before it is created
    time.sleep(15)


    #Monitor for Two Hours
    previousLine = "nothing"
    lastSpeed = 'nothing'
    i = 0
    while True:
        i = i + 1
        #Get Last Line of the output file
        lastLine = readLastLine(ethminerLogName, 'r')
        print(lastLine, end="")
        
        #Get the current Time
        timeRegex = re.compile(r'\S+(?=\|)')
        matchTime = timeRegex.search(lastLine)
        currentTime = 'NA'
        if matchTime:
            currentTime = matchTime.group(0)
        
        #Get the current Speed
        speedRegex = re.compile(r'\S+(?=\sMh/s)')
        matchSpeed = speedRegex.search(lastLine)
        currentSpeed = 'NA'
        if matchSpeed:
            currentSpeed = matchSpeed.group(0)
        '''
        #Get the current clock, and power settings
        nvidiaSMI = executeSubprocess(f'nvidia-smi -i {GPUIndex} -q')
        time.sleep(5)
        output = nvidiaSMI.communicate()
        '''
        time.sleep(5)
        output = "h"

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
        
        if i % 3 == 0:
            print(f'\nCurrent Speed: {currentSpeed}', file=open(ethminerLogName + '_', 'a'))
            print(f'lastSpeed: {lastSpeed}')
            print(f'Last Line: {lastLine}', end='')
            print(f'previousLine: {previousLine}', end='')
            if lastLine == previousLine or (currentSpeed == 'NA' and lastSpeed == 'NA'):
                print('Error restarting subprocess')
                break
            else:
                previousLine = lastLine
                lastSpeed = currentSpeed


        print(f'Clock: {currentClock}, Memory: {currentMemory}, Power: {currentPower}, Restarts: {restartCounter}\n')


    ethminer.terminate()
    time.sleep(1)
    restartCounter += 1

