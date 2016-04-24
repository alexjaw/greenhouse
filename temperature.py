#!/usr/bin/env python
#
# Measures temperature using w1 sensor DS18B20
# http://www.electrokit.com/temperatursensor-vattentat-ds18b20.49197
# Connections: Black = GND, Red = VDD, White = Data
# rpi2 pinout
# http://www.jameco.com/Jameco/workshop/circuitnotes/raspberry-pi-circuit-note.html
# Connection to rpi
# http://www.reuk.co.uk/DS18B20-Temperature-Sensor-with-Raspberry-Pi.htm
# w1 data:
# ls -l /sys/bus/w1/devices/
# cat /sys/bus/w1/devices/28-000007a6f1c4/w1_slave
import datetime
from email.mime.text import MIMEText
import smtplib
import time

import logging
import logging.config

HOME_DIR = '/home/pi/' + '/python/rpi_gpio/'

LOGGING_CONF_FILE = HOME_DIR + 'logging.conf'
logging.config.fileConfig(LOGGING_CONF_FILE, disable_existing_loggers=False)
logger = logging.getLogger('temperature.py')

try:
    import RPi.GPIO as GPIO
except Exception as e:
    log_err = 'WARNING. Failed importing RPi.GPIO'
    logger.error(log_err)

#------------------------------------#
#               SETTINGS             #
#------------------------------------#

T_CALIBRATION = 0.0  # TODO: calibrate!
T_MAX = 25
T_MIN = 10
UPDATE_INTERVAL = 10 * 60  # seconds
UPLOAD_TO_GMAIL = True
W1 = '/sys/bus/w1/devices/28-000007a6f1c4/w1_slave'

#------------------------------------#
#           END OF SETTING           #
#------------------------------------#


def _print_start_information():
    logger.info('---------- Starting temperature logger... ----------')
    if UPLOAD_TO_GMAIL:
        logger.info('Gmail logging enabled')
    else:
        logger.info('Gmail logging disabled')

    logger.info('Updating interval [s] = %s', str(UPDATE_INTERVAL))
    logger.info('W1 sensor path = %s', W1)


def is_temp_ok(t):
    if T_MIN <= t and t <= T_MAX:
        return True
    else:
        return False


def _send_email(subject, msg):
    GMAIL_USER = 'rpi.bohmeraudio@gmail.com'
    GMAIL_PASS = 'rpi+dsp=fun'
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
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


def worker(sleep_time):
    _print_start_information()
    while True:
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
            upload_log(msg)

        time.sleep(sleep_time)

