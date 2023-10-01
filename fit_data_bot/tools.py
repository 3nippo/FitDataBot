import asyncio
import time


class TextCallback:
    def __init__(self, callback, cancellation_text):
        self.callback = callback
        self.text_to_cb = { cancellation_text: callback }

    def call_back(self, text):
        callback = self.text_to_cb.get(text)
        if not callback:
            return False
        callback()
        return True


class AsyncTimer:
    def __init__(self, callback, every_sec, duration_sec):
        self.callback = callback
        self.every_sec = every_sec
        self.duration_sec = duration_sec
        self.task = None
        self.ts_start = int(time.time())
        self.ts_end = None
    
    async def _job(self):
        ts = 0
        await self.callback(ts)
        while ts < self.duration_sec:
            await asyncio.sleep(self.every_sec)
            ts += self.every_sec
            await self.callback(ts)
        self.ts_end = int(time.time())
    
    async def start(self):
        if not self.task:
            self.task = asyncio.ensure_future(self._job())
        await asyncio.wait_for(self.task, None)

    def cancel(self):
        self.task.cancel()
        self.ts_end = int(time.time())
    
    def elapsed(self):
        assert self.ts_end, "Timer is not stopped!"
        return self.ts_end - self.ts_start
