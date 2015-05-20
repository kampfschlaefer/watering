
# copied from github.com/piface/pifacecommon
# to make it work with gevent

from gevent import threading
import multiprocessing
from gevent import select
import time
import errno
import pifacecommon.mcp23s17

from pifacecommon.interrupts import (
    GPIO_INTERRUPT_PIN,
    # GPIO_INTERRUPT_DEVICE,
    GPIO_INTERRUPT_DEVICE_EDGE,
    GPIO_INTERRUPT_DEVICE_VALUE,
    GPIO_EXPORT_FILE, GPIO_UNEXPORT_FILE,
    FILE_IO_TIMEOUT,
    # READY_FOR_EVENTS,
    DEFAULT_SETTLE_TIME,
    Timeout, InterruptEvent,
)

from pifacedigitalio.core import PiFaceDigital


class FunctionMap(object):
    """Maps something to a callback function.
    (This is an abstract class, you must implement a SomethingFunctionMap).
    """
    def __init__(self, callback, settle_time=None):
        self.callback = callback
        self.settle_time = settle_time


class PinFunctionMap(FunctionMap):
    """Maps an IO pin and a direction to callback function."""
    def __init__(self, pin_num, direction, callback, settle_time):
        self.pin_num = pin_num
        self.direction = direction
        super(PinFunctionMap, self).__init__(callback, settle_time)

    def __str__(self):
        s = "Pin num:  {pin_num}\n" \
            "Direction:{direction}\n"
        return s.format(pin_num=self.pin_num,
                        direction=self.direction)


class EventQueue(object):
    """Stores events in a queue."""
    def __init__(self, pin_function_maps):
        super(EventQueue, self).__init__()
        self.last_event_time = [0]*8  # last event time on each pin
        self.pin_function_maps = pin_function_maps
        self.queue = multiprocessing.Queue()

    def add_event(self, event):
        """Adds events to the queue. Will ignore events that occur before the
        settle time for that pin/direction. Such events are assumed to be
        bouncing.
        """
        # print("Trying to add event:")
        # print(event)
        # find out the pin settle time
        for pin_function_map in self.pin_function_maps:
            if _event_matches_pin_function_map(event, pin_function_map):
            # if pin_function_map.pin_num == event.pin_num and (
            #         pin_function_map.direction == event.direction or
            #         pin_function_map.direction == IODIR_BOTH):
                pin_settle_time = pin_function_map.settle_time
                # print("EventQueue: Found event in map.")
                break
        else:
            # Couldn't find event in map, don't bother adding it to the queue
            # print("EventQueue: Couldn't find event in map:")
            # for pin_function_map in self.pin_function_maps:
            #     print(pin_function_map)
            return

        threshold_time = self.last_event_time[event.pin_num] + pin_settle_time
        if event.timestamp > threshold_time:
            self.put(event)
            self.last_event_time[event.pin_num] = event.timestamp

    def put(self, thing):
        self.queue.put(thing)

    def get(self):
        return self.queue.get()


class PortEventListener(object):
    """Listens for port events and calls the registered functions.

    >>> def print_flag(event):
    ...     print(event.interrupt_flag)
    ...
    >>> port = pifacecommon.mcp23s17.GPIOA
    >>> listener = pifacecommon.interrupts.PortEventListener(port)
    >>> listener.register(0, pifacecommon.interrupts.IODIR_ON, print_flag)
    >>> listener.activate()
    """

    TERMINATE_SIGNAL = "astalavista"

    def __init__(self, port, chip, return_after_kbdint=True):
        self.port = port
        self.chip = chip
        self.pin_function_maps = list()
        self.event_queue = EventQueue(self.pin_function_maps)
        self.detector = multiprocessing.Process(
            target=watch_port_events,
            args=(
                self.port,
                self.chip,
                self.pin_function_maps,
                self.event_queue,
                return_after_kbdint))
        self.dispatcher = threading.Thread(
            target=handle_events,
            args=(
                self.pin_function_maps,
                self.event_queue,
                _event_matches_pin_function_map,
                PortEventListener.TERMINATE_SIGNAL))

    def register(self, pin_num, direction, callback,
                 settle_time=DEFAULT_SETTLE_TIME):
        """Registers a pin number and direction to a callback function.

        :param pin_num: The pin pin number.
        :type pin_num: int
        :param direction: The event direction
            (use: IODIR_ON/IODIR_OFF/IODIR_BOTH)
        :type direction: int
        :param callback: The function to run when event is detected.
        :type callback: function
        :param settle_time: Time within which subsequent events are ignored.
        :type settle_time: int
        """
        self.pin_function_maps.append(
            PinFunctionMap(pin_num, direction, callback, settle_time))

    def deregister(self, pin_num=None, direction=None):
        """De-registers callback functions

        :param pin_num: The pin number. If None then all functions are
                        de-registered
        :type pin_num: int
        :param direction: The event direction. If None then all functions for
                          the given pin are de-registered
        :type direction:int
        """
        to_delete = []
        for i, function_map in enumerate(self.pin_function_maps):
            if (
                pin_num is None
                or (
                    function_map.pin_num == pin_num
                    and (
                        direction is None
                        or function_map.direction == direction
                    )
                )
            ):
                to_delete.append(i)
        for i in reversed(to_delete):
            del self.pin_function_maps[i]

    def activate(self):
        """When activated the :class:`PortEventListener` will run callbacks
        associated with pins/directions.
        """
        self.detector.start()
        self.dispatcher.start()

    def deactivate(self):
        """When deactivated the :class:`PortEventListener` will not run
        anything.
        """
        self.event_queue.put(self.TERMINATE_SIGNAL)
        self.dispatcher.join()
        self.detector.terminate()
        self.detector.join()


def _event_matches_pin_function_map(event, pin_function_map):
    # print("pin num", event.pin_num, pin_function_map.pin_num)
    # print("direction", event.direction, pin_function_map.direction)
    pin_match = event.pin_num == pin_function_map.pin_num
    direction_match = pin_function_map.direction is None
    direction_match |= event.direction == pin_function_map.direction
    return pin_match and direction_match


def watch_port_events(port, chip, pin_function_maps, event_queue,
                      return_after_kbdint=False):
    """Waits for a port event. When a port event occurs it is placed onto the
    event queue.

    :param port: The port we are waiting for interrupts on (GPIOA/GPIOB).
    :type port: int
    :param chip: The chip we are waiting for interrupts on.
    :type chip: :class:`pifacecommon.mcp23s17.MCP23S17`
    :param pin_function_maps: A list of classes that have inheritted from
        :class:`FunctionMap`\ s describing what to do with events.
    :type pin_function_maps: list
    :param event_queue: A queue to put events on.
    :type event_queue: :py:class:`multiprocessing.Queue`
    """
    # set up epoll
    gpio25 = open(GPIO_INTERRUPT_DEVICE_VALUE, 'r')  # change to use 'with'?
    epoll = select.epoll()
    epoll.register(gpio25, select.EPOLLIN | select.EPOLLET)

    while True:
        # wait here until input
        try:
            epoll.poll()
        except KeyboardInterrupt as e:
            if return_after_kbdint:
                return
            else:
                raise e
        except IOError as e:
            # ignore "Interrupted system call" error.
            # I don't really like this solution. Ignoring problems is bad!
            if e.errno != errno.EINTR:
                raise

        # find out where the interrupt came from and put it on the event queue
        if port == pifacecommon.mcp23s17.GPIOA:
            interrupt_flag = chip.intfa.value
        else:
            interrupt_flag = chip.intfb.value

        if interrupt_flag == 0:
            continue  # The interrupt has not been flagged on this board
        else:
            if port == pifacecommon.mcp23s17.GPIOA:
                interrupt_capture = chip.intcapa.value
            else:
                interrupt_capture = chip.intcapb.value
            event_queue.add_event(InterruptEvent(
                interrupt_flag, interrupt_capture, chip, time.time()))

    epoll.close()


def handle_events(
        function_maps, event_queue, event_matches_function_map,
        terminate_signal):
    """Waits for events on the event queue and calls the registered functions.

    :param function_maps: A list of classes that have inheritted from
        :class:`FunctionMap`\ s describing what to do with events.
    :type function_maps: list
    :param event_queue: A queue to put events on.
    :type event_queue: :py:class:`multiprocessing.Queue`
    :param event_matches_function_map: A function that determines if the given
        event and :class:`FunctionMap` match.
    :type event_matches_function_map: function
    :param terminate_signal: The signal that, when placed on the event queue,
        causes this function to exit.
    """
    while True:
        # print("HANDLE: Waiting for events!")
        event = event_queue.get()
        # print("HANDLE: It's an event!")
        if event == terminate_signal:
            return
        # if matching get the callback function, else function is None
        functions = map(
            lambda fm: fm.callback
            if event_matches_function_map(event, fm) else None,
            function_maps)
        # reduce to just the callback functions (remove None)
        # TODO: I think this can just be filter(None, functions)
        functions = filter(lambda f: f is not None, functions)

        for function in functions:
            function(event)


def bring_gpio_interrupt_into_userspace():  # activate gpio interrupt
    """Bring the interrupt pin on the GPIO into Linux userspace."""
    try:
        # is it already there?
        with open(GPIO_INTERRUPT_DEVICE_VALUE):
            return
    except IOError:
        # no, bring it into userspace
        with open(GPIO_EXPORT_FILE, 'w') as export_file:
            export_file.write(str(GPIO_INTERRUPT_PIN))

        wait_until_file_exists(GPIO_INTERRUPT_DEVICE_VALUE)


def deactivate_gpio_interrupt():
    """Remove the GPIO interrupt pin from Linux userspace."""
    with open(GPIO_UNEXPORT_FILE, 'w') as unexport_file:
        unexport_file.write(str(GPIO_INTERRUPT_PIN))


def set_gpio_interrupt_edge(edge='falling'):
    """Set the interrupt edge on the userspace GPIO pin.

    :param edge: The interrupt edge ('none', 'falling', 'rising').
    :type edge: string
    """
    # we're only interested in the falling edge (1 -> 0)
    start_time = time.time()
    time_limit = start_time + FILE_IO_TIMEOUT
    while time.time() < time_limit:
        try:
            with open(GPIO_INTERRUPT_DEVICE_EDGE, 'w') as gpio_edge:
                gpio_edge.write(edge)
                return
        except IOError:
            pass


def wait_until_file_exists(filename):
    """Wait until a file exists.

    :param filename: The name of the file to wait for.
    :type filename: string
    """
    start_time = time.time()
    time_limit = start_time + FILE_IO_TIMEOUT
    while time.time() < time_limit:
        try:
            with open(filename):
                return
        except IOError:
            pass

    raise Timeout("Waiting too long for %s." % filename)


## From pifacedigitalio.core
##
class InputEventListener(pifacecommon.interrupts.PortEventListener):
    """Listens for events on the input port and calls the mapped callback
    functions.

    copied from pifacedigitalio.core
    """
    def __init__(self, chip=None):
        if chip is None:
            chip = PiFaceDigital()
        super(InputEventListener, self).__init__(
            pifacecommon.mcp23s17.GPIOB,
            chip
        )
