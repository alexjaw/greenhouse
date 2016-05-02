#!/usr/bin/env python
#
# This is starting the interval worker in temperature.py
# Its started by cron at boot
# Check process with
# pi@greenhouse:~/python/rpi_gpio $ ps -Af | grep app.py
# root       392     1  0 Apr24 ?        00:01:34 python /home/pi/python/rpi_gpio/app.py
import temperature

def main():
    try:
        sleep_time = temperature.UPDATE_INTERVAL
        temperature.worker(sleep_time)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()