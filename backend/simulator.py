import threading
import time
from abc import ABC, abstractmethod

class BaseSimulator(ABC):
    def __init__(self):
        self.running = False
        self.paused = False
        self.rate = 1.0  # Default rate of data generation
        self._stop_event = threading.Event()
        self._thread = None

    @abstractmethod
    def step(self):
        """
        Abstract method to define the behavior of taking a single step
        in the simulation. This method should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def induce_fault(self):
        """
        Induces a fault in the simulation process.
        This will affect the output of the step method.
        """
        pass

    def run(self):
        """
        Main method to run in a separate thread.
        Handles the simulation based on the current state.
        """
        self.running = True
        self._stop_event.clear()

        while not self._stop_event.is_set():
            if not self.paused:
                self.step()
                time.sleep(1 / self.rate) # Adjust sleep based on the rate

    def start(self):
        """
        Starts the simulation in a separate thread.
        """
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run)
            self._thread.start()

    def stop(self):
        """
        Stops the simulation.
        """
        self.running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def pause(self):
        """
        Pauses the simulation.
        """
        self.paused = True

    def resume(self):
        """
        Resumes the simulation.
        """
        self.paused = False

    def reset(self):
        """
        Resets the simulator to its initial state.
        This includes clearing the fault state.
        """
        self.stop()
        self.start()

    def change_rate(self, new_rate):
        """
        Changes the rate of the simulation.
        """
        self.rate = new_rate
