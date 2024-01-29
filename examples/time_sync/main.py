"""
TUNIO 2023

TIME SYNC
"""

from termcolor import colored
import datetime as dt
import numpy as np
import random
import queue
import time
import zmq
import sys
import os


#%% UTILS
def busy_wait(dt):
    current_time = time.time()
    desired_time = current_time + dt
    while (time.time() < desired_time):
        pass


#%% MASTER

def master():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://127.0.0.1:5555')

    os.system('cls')

    try:
        told = 0
        sync_factor = 0.0 # send on the second accurately
        while True:
            time_raw = dt.datetime.now().time()
            time_print = "M: " + time_raw.strftime("%H:%M:%S:%f")
            time_send = time_raw.strftime("%H:%M:%S:%f")
            socket.send_string("master_raw " + time_send)
            
            tnow = time.time()
            if tnow >= told + 1 + sync_factor:
                told = tnow
                sync_factor = (round(tnow) - (tnow - 0.01)) / 2
                socket.send_string("master " + time_send)
                print(colored(time_print, 'red'), end='\r')
                busy_wait(0.1)
            else:
                print(time_print, end='\r')

                pass
    except:
        socket.close()


#%% LINE
def line(delay_s=0, noise_p=0): # delay in seconds ms acc, noise is probability
    context = zmq.Context()
    rx_line_socket = context.socket(zmq.SUB)
    rx_line_socket.connect('tcp://127.0.0.1:5555')
    rx_line_socket.setsockopt(zmq.SUBSCRIBE, b'master ')
    tx_line_socket = context.socket(zmq.PUB)
    tx_line_socket.bind('tcp://127.0.0.1:5556')

    i=0
    ticks = ["-", "\\", "|", "/", "-", "\\", "|", "/"]
    msg_buf = queue.Queue()
    if delay_s == 'rndm':
        buf_wait = 0
        ms_delay = round(random.random() * 10000)/10000
    elif delay_s > 1.0:
        this_delay = delay_s
        buf_wait = int(delay_s)
        ms_delay = delay_s - int(delay_s)
    else:
        this_delay = delay_s
        buf_wait = 0
        ms_delay = delay_s

    os.system('cls')

    try:
        while True:
            # rx the message
            rx_msg = rx_line_socket.recv()
            msg_buf.put(rx_msg)
            print("line rcvd [" + ticks[i%8] + "] " + str(i), end=' | ')

            if msg_buf.qsize() > buf_wait:
                to_send = msg_buf.get()
            else:
                continue

            if delay_s == 'rndm':
                this_delay = random.choice([0.333, 0.454, 0.555, 0.989, 0, 0.750, 0.212, 0, 0])
                busy_wait(this_delay)
            else:
                busy_wait(ms_delay)
            if random.random() < noise_p: continue
            i+=1
            # re broadcast message
            tx_line_socket.send_string(str(to_send, 'utf'))
            tx_line_socket.send_string('ping ' + str(this_delay))
            prindelay = round(this_delay * 1000)
            print("sent msg (" + str(noise_p) + ", " + str(prindelay) +  "): " + str(rx_msg, 'utf'))
    except Exception as e:
        rx_line_socket.close()
        tx_line_socket.close()
        raise(e)


#%% SLAVE
def slave():
    context = zmq.Context()
    rx_socket = context.socket(zmq.SUB)
    rx_socket.connect('tcp://127.0.0.1:5556')
    rx_socket.setsockopt(zmq.SUBSCRIBE, b'ping')
    rx_socket.setsockopt(zmq.SUBSCRIBE, b'master')
    
    out_socket = context.socket(zmq.PUB)
    out_socket.bind('tcp://127.0.0.1:5557')
    
    try:
        current_ping = 0.0
        random_starting_offset = random.random() * 3600 * 3
        offset = dt.timedelta(seconds=random_starting_offset)

        time_correction = dt.timedelta(seconds=0)
        ping_correction = dt.timedelta(seconds=0)
        latest_time_in = bytes(dt.datetime.now().strftime("%H:%M:%S:%f"), 'utf')

        os.system('cls')

        while True:
            time_raw = dt.datetime.now()
            time_raw_offset = time_raw + offset

            if rx_socket.poll(33, zmq.POLLIN):
                # rx the message
                rx_string = rx_socket.recv()
                topic, messagedata = rx_string.split()

                if topic == b'ping':
                    current_ping = float(messagedata)
                    # correct for latency
                    ping_correction = dt.timedelta(seconds=current_ping)

                elif topic == b'master':
                    latest_time_in = messagedata
                    # correct for time difference
                    latest_time_in_dt = dt.datetime.strptime(str(latest_time_in, "utf"), "%H:%M:%S:%f")
                    time_correction = latest_time_in_dt - time_raw_offset

                # get corrected local time
                time_corrected = time_raw_offset + time_correction + ping_correction
                time_corrected_print = time_corrected.strftime("%H:%M:%S:%f")
                show_str = "S: " + time_corrected_print + ", time in: " + str(latest_time_in,'utf') + ", ping: " + str(current_ping)

                # show freshly corrected as red
                print(colored(show_str, 'red'), end='\r')
                # print(colored(correction, 'red'), end='\r')
                busy_wait(0.1)

            else:
                # get corrected local time
                time_corrected = time_raw_offset + time_correction + ping_correction
                time_corrected_print = time_corrected.strftime("%H:%M:%S:%f")
                show_str = "S: " + time_corrected_print + ", time in: " + str(latest_time_in,'utf') + ", ping: " + str(current_ping)

                # show stale corrected
                print(show_str, end='\r')
                # print(correction, end='\r')
            
            out_socket.send_string("slave_raw " + time_corrected_print)

    except Exception as e:
        rx_socket.close()
        raise(e)


#%% MONITOR

"""
RECEIVES LATEST TIME FROM MASTER AND SLAVE
CALCULATES THE DELTA DOWN TO MICROSECOND - LIVE
CALCULATES THE AVERAGE ERROR OVER 20 SECONDS
DISPLAYS MTIME, STIME, DELTA, AVG.ERR
"""

def monitor():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://127.0.0.1:5555')
    socket.setsockopt(zmq.SUBSCRIBE, b'master_raw')
    socket.connect('tcp://127.0.0.1:5557')
    socket.setsockopt(zmq.SUBSCRIBE, b'slave_raw')
    
    master_time_str = dt.datetime.now().strftime("%H:%M:%S:%f")
    slave_time_str = dt.datetime.now().strftime("%H:%M:%S:%f")
    master_time_dt = dt.datetime.strptime(master_time_str, "%H:%M:%S:%f")
    slave_time_dt = dt.datetime.strptime(slave_time_str, "%H:%M:%S:%f")
    
    delta_cache = [0] * 20
    dex = 0
    dexmax = len(delta_cache)
    avg_delta_str = 0.0
    
    last_update = time.time()
    
    os.system('cls')
        
    while True:
        rx_msg = socket.recv()
        topic, messagedata = rx_msg.split()

        if topic == b'master_raw':
            master_time_str = str(messagedata, 'utf')
            master_time_dt = dt.datetime.strptime(master_time_str, "%H:%M:%S:%f")

        elif topic == b'slave_raw':
            slave_time_str = str(messagedata, 'utf')
            slave_time_dt = dt.datetime.strptime(slave_time_str, "%H:%M:%S:%f")
        
        tnow = time.time()
        if tnow <= last_update + 0.113: continue
        last_update = tnow

        
        delta = (slave_time_dt - master_time_dt).total_seconds()
        delta_str = "%15.6f"%delta
        
        delta_cache[dex] = delta
        dex+=1
        dex = dex%dexmax
        if dex == 0:
            avg_delta = np.mean(delta_cache)
            avg_delta_str = "%15.6f"%avg_delta

        print(master_time_str, slave_time_str, delta_str, avg_delta_str, end='\r')
        

#%% MAIN

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'master':
            print("MASTER CLOCK " * 10)
            master()
        elif sys.argv[1] == 'line':
            if len(sys.argv) > 2:
                delay_in_ms = sys.argv[2]
                if delay_in_ms == 'rndm':
                    line(delay_s='rndm')
                else:
                    delay_set = float(delay_in_ms)/1000
                    line(delay_s=delay_set)
            else:
                line()
            print("LINE " * 10)

        elif sys.argv[1] == 'slave':
            print("SLAVE " * 10)
            slave()
            
        elif sys.argv[1] == 'monitor':
            print("MONITOR " * 10)
            monitor()
        else:
            pass







