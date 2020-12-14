#!/usr/bin/python
# -*- coding: utf-8 -*-
from socketserver import BaseRequestHandler, ThreadingTCPServer, TCPServer
import threading
import time
import csv
import copy
import json


class user_client():
    def __init__(self, user_name, client_obj):
        self.user_name = user_name
        self.client_obj = client_obj
    #def print_obj(self):
    #    print(self.client_obj)
    def send(self, string):
        if not isinstance(string, bytes):
            string = bytes(string, encoding='utf8')
        self.client_obj.send(string)

    def send_json(self, dict_response):
        jresp = json.dumps(dict_response).encode('utf-8')
        # send_msg
        #j = json.loads(jresp)
        #print('send json to [{0}]'.format(self.user_name))
        #print(json.dumps(j, indent=4, sort_keys=True))
        # send_msg
        #print(type(jresp))
        self.client_obj.send(jresp)

    '''
    會導致阻塞，不建議使用
    def recv(self , size = 8192):
            msg = self.request.recv(size)
    '''
    def shutdown(self):
        #print(dir(self.client_obj))
        #self.client_obj.shutdown(0) 
        self.client_obj.close()

login_user_list = dict()

class EchoHandler(BaseRequestHandler):
    def handle(self):
        print(threading.enumerate())
        global lock
        global login_user_list
        client_name = str(self.client_address).replace(' ','')
        print('Welcome to ' + client_name)
        # 初始化
        first_nock = True
        ACCOUNT_HAND = 'ac='
        PASSWORD_HAND = 'pw='
        welcome_zone = True

        while welcome_zone: # 處理第一次登入作業
            
            msg = self._recv()
            # 如果對方斷開連結
            if not msg:
                print('lost client from ' + client_name)
                self._shutdown()
                break
            # 詢問登入對象的帳號密碼
            if not login_user_list.__contains__(client_name):
                if first_nock:
                    self._send("WHO_ARE_YOU")
                    first_nock = False
                elif msg.find(ACCOUNT_HAND) >= 0 and msg.find(PASSWORD_HAND) >=0 and len(msg.split(' ')) == 2:
                    msg_list = msg.split(' ')
                    ac = msg_list[0][msg_list[0].find(ACCOUNT_HAND) + len(ACCOUNT_HAND):]
                    pw = msg_list[1][msg_list[1].find(PASSWORD_HAND) + len(PASSWORD_HAND):]
                    #print(msg_list)
                    #print("ac = [{0}] pw = [{1}]".format(ac, pw))
                    with open('user_list.csv', 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            if row[0] == ac:
                                if row[1] == pw:
                                    # 完成登入動作
                                    c_obj = user_client(ac, self.request)
                                    login_user_list[client_name] = [ac , c_obj]
                                    print('user [{0}] is login'.format(ac))

                                    # 同步至父進程
                                    lock.acquire() # 锁住
                                    global user_list
                                    for key in user_list.keys(): # 初始化
                                        del user_list[key]
                                    for key in login_user_list.keys():
                                        user_list[key] = login_user_list[key]
                                    #print('in ' + __name__)
                                    #print(type(user_list))
                                    #print(user_list)
                                    lock.release() # 释放
                                    '''
                                    print('------- orignal obj --------')     原始物件
                                    print(self.request)
                                    #del self.request
                                    print('------- packet obj --------')      和COPY物件互不影響(可以同時存在，也可以其中一方消滅)
                                    print(login_user_list[client_name][1])
                                    login_user_list[client_name][1].print_obj()
                                    login_user_list[client_name][1].send_test('string_test')    兩者皆可以與客戶端溝通
                                    '''
                                    welcome_zone = False
                                    #threading.Thread(target=self.listen_mode, args=(self,client_name,ac))
                                    self._send('LOGIN_COMPLETE')
                                    break
                                    '''
                                    print('_send is return') 送出訊息後，沒得到回覆也不會阻塞
                                    '''
                                    
                                else:
                                    self._send('NOT_PW')
                                    self._shutdown()
                                    break
                            else:
                                self._send('NOT_AC')
                                self._shutdown()
                                break
                else:
                    self._send("LOGIN_FAILED")
                    self._shutdown()
                    break
                continue

        while not welcome_zone: # 登入完成後，改成傾聽模式
            print('listen Mode waiting for ' + ac)
            # 等待傳入
            msg = self._recv()

            if not msg: # 如果對方斷開連結
                print('lost client from ' + client_name)
                #self._shutdown()
                if login_user_list.__contains__(client_name):
                    print('user is logout from ' + client_name)
                    login_user_list[client_name][1].shutdown()
                    del login_user_list[client_name]
                    # 同步至父進程
                    lock.acquire() # 锁住
                    #global user_list
                    for key in user_list.keys(): # 初始化
                        del user_list[key]
                    for key in login_user_list.keys():
                        user_list[key] = login_user_list[key]
                    lock.release() # 释放
                break
            else: # 其他指令
                command_str , value_list = self.readJson_to_command(msg) # 解析指令
                if command_str == "ERROR":
                    print("command_str error")
                    continue
                else:
                    send_msg = ""

                    if command_str == 'serving_index':
                        target_index = value_list[0] # str格式
                        sub_mod = value_list[1]
                        #temp_list = self.copy_menus_list(menus_list)

                        # 告訴FLASKtest 將要被刪除的index
                        if sub_mod == '-d':
                            send_msg = 'removeIndex ' + target_index
                        elif sub_mod == '-s':
                            send_msg = 'servingIndex ' + target_index
                        
                    if command_str == 'cutIn':
                        if value_list[0] == 'view':
                            send_msg = 'cutIn 0 ' + client_name
                        elif value_list[0] == 'set':
                            set_sw = value_list[1]
                            set_time_val = value_list[2]
                            send_msg = 'cutIn 1 {0} {1}'.format(set_sw, set_time_val)

                    if command_str == 'creat_postHub':
                        hub_name = value_list[0]
                        send_msg = 'creat_postHub {0}'.format(hub_name)

                    if command_str == 'regRemove':
                        table_str = value_list[0]
                        send_msg = 'regRemove {0}'.format(table_str)
                    
                    Queue_send_to_poster.put(send_msg)


    def readJson_to_command(self, json_str):
        #print('def readJson_to_command(self, json)')
        dict_temp = json.loads(json_str)
        #print('is load')
        #print(dict_temp)
        if not dict_temp['base-root'].__contains__('command-cast'):
            print('!!! readJson_to_command error !!!')
            return "ERROR" , []

        command_obj = dict_temp['base-root']['command-cast']
        print("get ['command-cast']")
        print(json.dumps(command_obj, indent=4, sort_keys=True))
        command = command_obj['command']
        values = command_obj['values']
        return command , values

    def copy_menus_list(s_list):
        global lock
        output_list = list()
        output_list.clear()
        lock.acquire()
        for line in s_list:
            output_list.append(line)
        lock.release()
        return output_list

    def _send(self, msg):
        if not isinstance(msg, bytes):
            msg = bytes(msg, encoding='utf8')
        print('send msg is {0} to {1}'.format(msg, str(self.client_address)))
        self.request.send(msg)

    def _recv(self , size = 8192):
        try:
            msg = self.request.recv(size)
        except: # 對方意外斷開
            print('except link failed form ' + str(self.client_address))
            return
        try:
            msg = str(msg, encoding='utf-8')
        except UnicodeDecodeError:
            print('get [Error] msg is\n{0}\nby {1}'.format(msg, str(self.client_address)))
            return
        print('get msg is\n{0}\nby {1}'.format(msg, str(self.client_address)))

        return msg

    def _shutdown(self):
        #print(threading.current_thread())
        #print(self.request)
        #print('-------- is shutdown ---------')
        self.server.shutdown_request(self.request)

def find_clientObj(name_key):
    global login_user_list
    obj = login_user_list[name_key][1]
    return obj

def re_cutIn_toClient(sw, time_val, target_client):
    response_obj = dict()
    response_obj['type'] = 'cutIn_view'
    response_obj['sw'] = str(sw)
    response_obj['count'] = str(time_val)

    clientObj = find_clientObj(target_client)
    json_temp = dict()
    json_temp.clear()
    json_temp['base-root'] = {'command-response' : response_obj}
    try:
        clientObj.send_json(json_temp)
    except:
        print('send Error for ' + clientObj.user_name)

user_list = None
lock = None
menus_list = list()
Queue_send_to_poster = None
def root(strating, m_dict, m_lock, rev_Queue, send_Queue):
    
    if strating == True:
        
        global lock
        global Queue_send_to_poster
        lock = m_lock
        Queue_send_to_poster = send_Queue # 傳給FLASKtest的訊息Queue
        lock.acquire() # 锁住
        global user_list
        user_list = m_dict
        #print('TCP')
        serv = ThreadingTCPServer(('0.0.0.0', 20000), EchoHandler)
        serv.daemon_threads = True
        #serv.shutdown_request(self.request)
        #user_list['test'] = 'test_str__TCP'
        print("RUN (ctrl + C to Exit)")
        lock.release() # 释放

        t = threading.Thread(target = waiting_QueueEvent, args=(rev_Queue,))
        t.start()
        serv.serve_forever()
        
        
        '''
        try:
            print("RUN (ctrl + C to Exit)")
            serv.serve_forever()
        except KeyboardInterrupt:
            serv.shutdown()
            exit()
        '''


def waiting_QueueEvent(Queue):
    while True:
        Event_msg = Queue.get()
        print(__name__ + ' :: Event_msg is get : ' + Event_msg)
        if Event_msg == "":
            continue
        else:
            Event_list = Event_msg.split(' ')
            event_type = Event_list[0]
            event_values = list(Event_list[1:])
            #print(event_type, event_values)

            if event_type == 're_cutIn':
                sw = event_values[0]
                time_val = event_values[1]
                target_client = event_values[2]
                re_cutIn_toClient(sw, time_val, target_client)

    