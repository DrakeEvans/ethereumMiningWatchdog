#! python3

import os
import subprocess
import sys
import shlex
import time
import re
import ctypes
import requests

#Config Values
GPUList = sys.argv[1]
GPUIndex = GPUList[0]
memoryOffset = sys.argv[2]
print(f'GPUList: {GPUList}')       
workingDir = "C:\\Users\ADE\ethWatchdog"
api_base = 'https://api.ethermine.org'
miner = '0xA61DA3437F3e861ED245F8A869E478c8eb7a03Ac'
worker = 'MINER'



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
    GPUList = GPUList.replace(',',' ')
    print(f'GPULIST: {GPUList}')
    restartCounter = 0
    while (restartCounter <100):
        powerLevel = readLastLine(f'{workingDir}\powerLevel.config', 'r')
        print(f'Power Level: {powerLevel}')
        ethminerLogName = f'{workingDir}\ethminerOutput{GPUIndex}.log'

        #Start Main Subprocess and write output to file
        argString = shlex.split(f'C:\\Users\ADE\\Nvidia\\nvidiaInspector.exe -setMemoryClockOffset:{GPUIndex},0,{memoryOffset}', posix=0)
        nvidiaInspector = subprocess.Popen(argString)
    
        
        nvidiaPower = executeSubprocess(f'nvidia-smi -pl {powerLevel} -i {GPUIndex}')
        
        arg = shlex.split(f'C:\\Users\ADE\ethminer.exe --farm-recheck 200 -U --cuda-devices {GPUList} -M -S us1.ethermine.org:4444 -FS us2.ethermine.org:4444 -O 0xA61DA3437F3e861ED245F8A869E478c8eb7a03Ac.MINER{GPUIndex}', posix=0)
        print(arg)
        ethminer = subprocess.Popen(arg, stderr=subprocess.STDOUT, stdout=open(ethminerLogName, 'a'))
        
        
        print('Subprocess Started')
        
        
        # Kill unruly EXEs
        time.sleep(3)
        nvidiaInspector.terminate()
        nvidiaPower.terminate()


        #Sleep while ethminer subprocess begins, impossible to access file before it is created
        time.sleep(10)


        #Monitor for Two Hours
        previousLine = "nothing\n"
        lastSpeed = 'nothing\n'
        i = 0
        previousHashRate = 999999999
        while True:
            i = i + 1

            #Every third cycle check for updated power
            '''if i % 3 == 0:
                latestPower = readLastLine(f'{workingDir}\powerLevel.config', 'r')
                #if power has changed from the applied value, update, and reapply the power setting
                if latestPower != powerLevel:
                    powerLevel = latestPower
                    nvidiaPower = executeSubprocess(f'nvidia-smi -pl {powerLevel} -i {GPUIndex}')
                    try:
                        nvidiaPower.communicate(timeout=4)
                    except subprocess.TimeoutExpired:
                        nvidiaPower.terminate()'''
            
            #Get Last Line of the output file
            lastLine = readLastLine(ethminerLogName, 'r')
            # print(lastLine, end="")
            
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
            
            #Get the current clock, and power settings
            nvidiaSMI = executeSubprocess(f'nvidia-smi -i {GPUIndex} -q')
            try:
                output = nvidiaSMI.communicate(timeout=4)
            except subprocess.TimeoutExpired:
                nvidiaSMI.terminate()
                output = 'timeout'
            
            
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
            
            if i % 1 == 0:
                print(f'Current Speed: {currentSpeed}', file=open(ethminerLogName + '_', 'a'))
                print(f'lastSpeed: {lastSpeed}')
                print(f'Last Line: {lastLine}', end='')
                print(f'previousLine: {previousLine}', end='')
                print(f'GPU: {GPUIndex}, ', end='')
                if i > 10 and i % 2 == 0:
                    if lastLine == previousLine or (currentSpeed == 'NA' and lastSpeed == 'NA'):
                        print('Error restarting subprocess')
                        ethminer.terminate()
                        break
                    else:
                        previousLine = lastLine
                        lastSpeed = currentSpeed


            if i % 20 == 0:
                response = requests.get(api_base + f'/miner/:{miner}/worker/:{worker}{GPUIndex}/currentStats')
                # print(response.json())
                hashRate = response.json()['data']['currentHashrate']
                # print(f'Hashrate: {hashRate}')
                print(f'previousHash: {previousHashRate}')
                print(f'currentHash: {hashRate}\n')
                try:
                    if hashRate < 39000000 and previousHashRate < 39000000:
                        ethminer.terminate()
                        break
                except:
                    break

                previousHashRate = hashRate


            print(f'Clock: {currentClock}, Memory: {currentMemory}, Power: {currentPower}, Restarts: {restartCounter}\n\n')
            time.sleep(5)


        ethminer.terminate()
        time.sleep(1)
        restartCounter += 1

else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'C:\\Users\ADE\ethWatchdog\ethWatch.py {GPUList} {memoryOffset}', None, 1)