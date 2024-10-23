import asyncio

class ResettableTimer:
    def __init__(self, timeout, callback):
        """
        Initialize the ResettableTimer.

        :param timeout: Timeout in seconds.
        :param callback: Callback function to be called when the timer expires.
        """
        self.timeout = timeout
        self.callback = callback
        self._task = None

    async def _run(self):
        """Run the timer and call the callback after the timeout."""
        try:
            await asyncio.sleep(self.timeout)
            await self.callback()  # Call the callback asynchronously when the timer expires
        except asyncio.CancelledError:
            # Handle timer being canceled (which happens when reset or stopped)
            pass

    def start(self):
        """Start or restart the timer."""
        self.cancel()  # Cancel any previous task
        self._task = asyncio.create_task(self._run())

    def reset(self):
        """Reset the timer."""
        self.start()  # Restart the timer

    def cancel(self):
        """Cancel the running timer."""
        if self._task:
            self._task.cancel()  # Cancel the running timer task
            self._task = None

async def example_callback():
    print("Timer expired!")

async def main():
    # Create a resettable timer with a 5-second timeout
    timer = ResettableTimer(5, example_callback)

    print("Starting timer...")
    timer.start()

    await asyncio.sleep(2)
    print("Resetting timer after 2 seconds...")
    timer.reset()

    await asyncio.sleep(3)
    print("Resetting timer after 3 more seconds...")
    timer.reset()

    await asyncio.sleep(6)  # Let the timer expire after 6 seconds
    print("Timer completed.")

if __name__ == "__main__":
    asyncio.run(main())
