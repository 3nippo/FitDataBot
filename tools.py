import asyncio

class AsyncTimer:
    def __init__(self, callback, every_sec, duration_sec):
        self.callback = callback
        self.every_sec = every_sec
        self.duration_sec = duration_sec
        self.task = asyncio.ensure_future(self._job())
    
    async def _job(self):
        ts = 0
        while ts < self.duration_sec:
            await asyncio.sleep(self.every_sec)
            await self.callback(ts)
            ts += self.every_sec
    
    def cancel(self):
        self.task.cancel()
