#!/usr/bin/env python
#
# This is starting the interval worker in temperature.py
import temperature

def main():
    try:
        sleep_time = temperature.UPDATE_INTERVAL
        temperature.worker(sleep_time)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()