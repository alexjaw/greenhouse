#!/usr/bin/env python
#
# Measures temperature using w1 sensor DS18B20
# This script is controlled by cron (for pi), there should be a backup of

import datetime
from email.mime.text import MIMEText
import os
import smtplib

import logging.config


HOME_DIR = os.path.dirname(os.path.realpath(__file__))

LOGGING_CONF_FILE = os.path.join(HOME_DIR, 'logging.conf')
logging.config.fileConfig(LOGGING_CONF_FILE, disable_existing_loggers=False)
logger = logging.getLogger('temperature.py')


try:
    import RPi.GPIO as GPIO
except Exception as e:
    log_err = 'WARNING. Failed importing RPi.GPIO'
    logger.error(log_err)

try:
    import thingspeak
except Exception as e:
    log_err = 'WARNING. Failed importing thingspeak'
    logger.error(log_err)

#------------------------------------#
#               SETTINGS             #
#------------------------------------#

T_ERROR = -300
T_CALIBRATION = 0.0  # TODO: calibrate!
T_MAX = 30
T_MIN = 8
#UPDATE_INTERVAL = 10 * 60  # seconds
UPLOAD_TO_GMAIL = False
UPLOAD_TO_THINGSPEAK = True
W1 = '/sys/bus/w1/devices/28-000007a6f1c4/w1_slave'

# GMAIL
GMAIL_USER = 'rpi.bohmeraudio@gmail.com'
GMAIL_PASS = os.environ.get('GMAIL_PASS')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# THINGSPEAK
# using: pip install thingspeak
# or https://github.com/mchwalisz/thingspeak
THINGSPEAK_APIKEY_W = os.environ.get('THINGSPEAK_APIKEY_W')
THINGSPEAK_APIKEY_R = os.environ.get('THINGSPEAK_APIKEY_R')
THINGSPEAK_CHANNEL = 109814
THINGSPEAK_FIELD = 1  # Temperature
#------------------------------------#
#           END OF SETTING           #
#------------------------------------#


def _print_start_information():
    logger.info('---------- Starting temperature logger... ----------')
    if UPLOAD_TO_GMAIL:
        logger.info('Gmail logging enabled')
    elif UPLOAD_TO_THINGSPEAK:
        logger.info('ThingSpeak logging enabled')
    else:
        logger.info('Gmail logging disabled')

    #logger.info('Updating interval [s] = %s', str(UPDATE_INTERVAL))
    logger.info('W1 sensor path = %s', W1)


def is_temp_ok(t):
    if T_MIN <= t and t <= T_MAX:
        return True
    else:
        return False


def _send_email(subject, msg):
    #logger.info('Starting to send email...')
    smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(GMAIL_USER, GMAIL_PASS)
    msg['Subject'] = subject
    msg['From']    = GMAIL_USER
    msg['To']      = GMAIL_USER
    smtpserver.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
    smtpserver.close()


def get_data_from_hw():
    # This is directly communicationg with hardware
    try:
        with open(W1, 'r') as w1:
            data = w1.read()
        return data
    except Exception as e:
        raise


def get_temp_from_w1_data(data):
    # Returns float
    tmp = data.split('\n')[1].split(' ')[9]
    t = tmp.split('=')[1]
    temperature = float(t)/1000 - T_CALIBRATION
    return temperature


def measure_temp():
    try:
        data = get_data_from_hw()
    except Exception as e:
        raise
    temperature = get_temp_from_w1_data(data)
    return temperature


def upload_log(data):
    text = ''
    date_time = str(datetime.datetime.now())
    subject = 'Greenhouse temperature, ' + data
    msg = date_time + ': ' + data
    email_msg = MIMEText(msg)
    text += email_msg.get_payload()
    email_msg.set_payload(text)
    try:
        _send_email(subject, email_msg,)
    except Exception as e:
        msg = 'ERROR. Gmail failed: ' + str(e)
        logger.error(msg)


def upload_to_thingspeak(data):
    '''
    Update thingspeak channel with data
    :param ch: thingspeak channel object
    :param data: float
    :return:
    '''
    ch = thingspeak.Channel(id=THINGSPEAK_CHANNEL, write_key=THINGSPEAK_APIKEY_W)
    msg = {}
    msg[THINGSPEAK_FIELD] = data
    return ch.update(msg)


def main():
    #_print_start_information()
    temp = T_ERROR
    try:
        temp = measure_temp()
    except Exception as e:
        msg = 'ERROR. Failed getting temp' + str(e)
        logger.info(msg)
    else:
        if not is_temp_ok(temp):
            msg = 'WARNING. Temp = ' + str(temp)
        else:
            msg = 'Temp is ok, temp =  ' + str(temp)

    logger.info(msg)
    if UPLOAD_TO_GMAIL:
        try:
            upload_log(msg)
        except Exception as e:
            logger.error('ERROR. gmail fail, {}'.format(e))

    elif UPLOAD_TO_THINGSPEAK:
        try:
            if temp != T_ERROR:
                logger.info('RECV: {}'.format(upload_to_thingspeak(temp)))
            else:
                # do something when temperature error
                pass
        except Exception as e:
            logger.error('ERROR. thingspeak fail, {}'.format(e))
            logger.info('API key: {}'.format(THINGSPEAK_APIKEY_W))


if __name__ == '__main__':
    main()
