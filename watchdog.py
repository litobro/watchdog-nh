import os
import sys
import asyncio
import kasa
import logging
from logging.handlers import RotatingFileHandler
import nicehash
from creds import *

host = 'https://api2.nicehash.com'

worker_name = 'worker1'
kasa_ip = '192.168.0.206'
logfile = '/opt/watchdog-nh/output.log'

def main(argv):
    logger = logging.getLogger('WATCHDOG-NH-LOG')
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler(logfile, maxBytes=5*1024*1024, backupCount=2)
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info('Watchdog on: {}'.format(argv[1]) + ' Using switch: {}'.format(argv[2]))

    api = nicehash.private_api(host, org_id, key, secret)
    rigs = api.get_rigs()['miningRigs']

    status = ''
    for rig in rigs:
        if rig['name'] == argv[1]:
            status = rig['minerStatus']
            logger.info(argv[1] + ' STATUS: ' + status)

    if status == 'OFFLINE':
        # Device appears to be offline, restart it using smart switch
        logger.info('Device offline, restarting')
        dev = kasa.SmartDevice(argv[2])
        asyncio.run(dev.update())
        asyncio.run(dev.turn_off())
        asyncio.run(dev.turn_on())
        asyncio.run(dev.update())
        try:
            assert dev.is_on
        except Exception as e:
            logger.warning('Device did not come back online!')
    else:
        logger.info('Device OK!')


if __name__ == '__main__':
    main([sys.argv[0], worker_name, kasa_ip])
