#from gevent import monkey
#monkey.patch_all()
#import asyncio
#import gevent
from FLASKtest import root as Poster
from TCPserver import root as ClientLinker
from TCPbroadcast import root as BroadCast
import time
import multiprocessing
import traceback
import os
from camera_strat_run_VerER import set_camera

def handle_error(e):
    '''處理 child process 的錯誤，不然 code 寫錯時，不會回報任何錯誤'''
    traceback.print_exception(type(e), e, e.__traceback__)
    
if __name__=='__main__':
    manager = multiprocessing.Manager()
    list_Poster = manager.list()
    dict_ClientLinker = manager.dict()
    Poster2ClientLinker = manager.Queue()
    ClientLinker2Poster = manager.Queue()
    lock = manager.Lock()
    
    with multiprocessing.Pool(processes=4) as pool:
        
        pool.apply_async(Poster, args=(True, list_Poster, lock, ClientLinker2Poster, Poster2ClientLinker), error_callback=handle_error)
        time.sleep(10)
        
        pool.apply_async(ClientLinker, args=(True, dict_ClientLinker, lock, Poster2ClientLinker, ClientLinker2Poster), error_callback=handle_error)
        time.sleep(2)

        pool.apply_async(BroadCast, args=(list_Poster, dict_ClientLinker, lock), error_callback=handle_error)
        time.sleep(1)

        #pool.apply_async(set_camera, error_callback=handle_error)
        #time.sleep(10)

        pool.close()
        pool.join()
