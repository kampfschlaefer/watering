# watering

[![Build Status](https://travis-ci.org/kampfschlaefer/watering.svg?branch=master)](https://travis-ci.org/kampfschlaefer/watering)

Watering for my plants

## TODO-list

- [x] make pifacecommon.interrupts play with gevent
- [x] add MaxState when the reservoir is filled (shouldn't allow manual pumping then)
- [x] stop pump on exit
- [x] add timer for timeouts
- ~~Look at guv as replacement for gevent (gevent is not py3, err seems to need py3)~~
- [x] Switch to python3.4 and replace gevent with asyncio
- [ ] add jabber bot to send notification in alarm-state and ask status
- [ ] sense state on startup, when the upper switch is closed, it should start with max-state
- [ ] remove threading and multiprocess module from interrupts handling and replace with asyncio
