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
'''
def on_QTlinker(t):
    time.sleep(t)
    QTlinker(True)

def on_poster(t):
    time.sleep(t)
    poster(True)


gevent.joinall([
    
    gevent.spawn(on_QTlinker, 1),
    gevent.spawn(on_poster, 5)
])
'''

def handle_error(e):
    '''處理 child process 的錯誤，不然 code 寫錯時，不會回報任何錯誤'''
    traceback.print_exception(type(e), e, e.__traceback__)
    
if __name__=='__main__':
    #print('all strat!!!!!!!!!')
    #print(traceback.format_stack())
    manager = multiprocessing.Manager()
    list_Poster = manager.list()
    dict_ClientLinker = manager.dict()
    Poster2ClientLinker = manager.Queue()
    ClientLinker2Poster = manager.Queue()
    lock = manager.Lock()
    
    with multiprocessing.Pool(processes=4) as pool:
        #print('CPUs = ', end='')
        #print(os.cpu_count())
        
        pool.apply_async(Poster, args=(True, list_Poster, lock, ClientLinker2Poster, Poster2ClientLinker), error_callback=handle_error)
        time.sleep(10)
        
        pool.apply_async(ClientLinker, args=(True, dict_ClientLinker, lock, Poster2ClientLinker, ClientLinker2Poster), error_callback=handle_error)
        time.sleep(2)
        #pool.apply_async(on_poster, args=(dict_ClientLinker,), error_callback=handle_error)
        #time.sleep(1)
        pool.apply_async(BroadCast, args=(list_Poster, dict_ClientLinker, lock), error_callback=handle_error)
        time.sleep(1)

        #pool.apply_async(set_camera, error_callback=handle_error)
        #time.sleep(10)

        
        
        

        # 關掉 pool 不再加入任何 child process
        pool.close()
        
        #while True:
        #    time.sleep(3)
        #    print('tttttttttttttt')
        #    print(dict_ClientLinker)
        
        # 調用 join() 之前必須先調用close()
        pool.join()
        



