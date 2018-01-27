
import requests
import subprocess
import sys
import shlex
import time

GPUIndex = sys.argv[1]

def executeSubprocess(commandString):
    args = shlex.split(commandString, posix=0)
    print(f'arguement: {args}')
    process = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return process

api_base = 'https://api.ethermine.org'
miner = '0xA61DA3437F3e861ED245F8A869E478c8eb7a03Ac'
worker = 'MINER'
previousHashRate = 999999999
print(f'System Hashrate Manager: {GPUIndex}')
time.sleep(60*60)
while True:
    
    response = requests.get(api_base + f'/miner/:{miner}/worker/:{worker}{GPUIndex}/currentStats')
    # print(response.json())
    hashRate = response.json()['data']['currentHashrate']
    # print(f'Hashrate: {hashRate}')
    print(f'previousHash: {previousHashRate}')
    print(f'currentHash: {hashRate}\n')
    if hashRate < 39000000 and previousHashRate < 39000000:
        myReboot = executeSubprocess('shutdown /r')

    previousHashRate = hashRate
    # print('sleep')
    time.sleep(60*60)