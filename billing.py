import time

entry_time = time.time()

def calculate_bill():
    exit_time = time.time()
    duration = (exit_time - entry_time) / 60
    bill = duration * 5
    print("Total Bill:", bill)