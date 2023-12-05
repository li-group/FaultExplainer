import pandas as pd
import threading
import redis
from simulator import BaseSimulator

class DataFrameSimulator(BaseSimulator):
    initial_file = './data/fault0.csv'
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        super().__init__()
        self.data_frame = pd.read_csv(self.initial_file)
        self.iterator = self.data_frame.iterrows()
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.fault_id = 0

    def step(self):
        try:
            # Get the next row from the iterator
            _, row = next(self.iterator)
            # print(f"Thread ID: {threading.get_ident()}, Data: {row['time']}")
        except StopIteration:
            # Restart the iterator if we reach the end of the DataFrame
            self.iterator = self.data_frame.iterrows()
            _, row = next(self.iterator)
            # print(f"Thread ID: {threading.get_ident()}, Data: {row['time']}")

        # Convert the row to a string or a suitable format
        data_str = row.to_json()
        # Publish the data to Redis
        self.redis_client.rpush('simulator_data', data_str)

    def induce_fault(self, fault_id):
        self.fault_id = fault_id
        # Change the DataFrame based on the fault_id
        print(f"Changing dataframe to fault{fault_id}.csv")
        new_file = f"./data/fault{fault_id}.csv"
        self.data_frame = pd.read_csv(new_file)
        self.iterator = self.data_frame.iterrows()


if __name__ == "__main__":
    import time

    # Create an instance of the Simulator
    simulator = DataFrameSimulator()
    print(f"Thread ID: {threading.get_ident()}> Starting Simulator")

    # Start the simulator
    simulator.start()
    time.sleep(5)  # Let it run for a while

    print(f"Thread ID: {threading.get_ident()}> Introducing Fault")
    # Induce a fault by setting the counter to 3
    simulator.induce_fault(3)

    time.sleep(5)  # Let it run for a while after inducing the fault

    # Pause, resume, and stop to demonstrate control
    print(f"Thread ID: {threading.get_ident()}> Pausing Simulator")
    simulator.pause()
    time.sleep(2)  # Paused for 2 seconds
    print(f"Thread ID: {threading.get_ident()}> Resuming Simulator")
    simulator.resume()

    time.sleep(5)  # Let it run for a while more
    print(f"Thread ID: {threading.get_ident()}> Stopping Simulator")
    simulator.stop()
