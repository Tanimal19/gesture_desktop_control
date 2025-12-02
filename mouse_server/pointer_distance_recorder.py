# to record the distance the mouse pointer moves on macOS

import Quartz
import time
import logging
from threading import Thread

logger = logging.getLogger(__name__)


class PointerDistanceRecorder:
    def __init__(self):
        self.running = False
        self.total_distance = 0.0
        self.last_pos = None
        self._tap = None

    def _callback(self, proxy, event_type, event, refcon):
        if not self.running:
            return event

        loc = Quartz.CGEventGetLocation(event)
        x, y = loc.x, loc.y

        if self.last_pos is not None:
            dx = x - self.last_pos[0]
            dy = y - self.last_pos[1]
            self.total_distance += (dx**2 + dy**2) ** 0.5

        self.last_pos = (x, y)
        return event

    def start(self):
        if self.running:
            return
        self.running = True
        self.total_distance = 0.0
        self.last_pos = None

        def run():
            mask = Quartz.CGEventMaskBit(Quartz.kCGEventMouseMoved)
            self._tap = Quartz.CGEventTapCreate(
                Quartz.kCGHIDEventTap,
                Quartz.kCGHeadInsertEventTap,
                Quartz.kCGEventTapOptionDefault,
                mask,
                self._callback,
                None,
            )

            if not self._tap:
                logger.error("Failed to create event tap.")
                return

            loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self._tap, 0)
            Quartz.CFRunLoopAddSource(
                Quartz.CFRunLoopGetCurrent(), loop_source, Quartz.kCFRunLoopDefaultMode
            )
            Quartz.CGEventTapEnable(self._tap, True)
            Quartz.CFRunLoopRun()

        Thread(target=run, daemon=True).start()
        time.sleep(0.1)  # Give tap time to start

    def stop(self) -> float:
        self.running = False
        if self._tap:
            Quartz.CGEventTapEnable(self._tap, False)
        return self.total_distance


if __name__ == "__main__":
    recorder = PointerDistanceRecorder()
    print("Starting distance recording for 5 seconds...")
    recorder.start()
    time.sleep(5)
    distance = recorder.stop()
    print(f"Total distance moved: {distance:.2f}")
