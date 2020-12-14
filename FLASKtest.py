#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from flask import Flask, request ,jsonify, send_from_directory, render_template
import csv
import threading
import datetime
import pytz
import copy
import time
import os
import traceback

use_mysql = True
try:
    import pymysql.cursors
    connection = pymysql.connect(host="localhost", user="tuyn76801", password="***", db="myflask_db", charset="utf8")
    use_mysql = True
    search_index = 1
    with connection.cursor() as cursor:
        sql = "SELECT search_index FROM menu_requests"
        cursor.execute(sql)
        result = cursor.fetchall()
        result_list = list()
        for row in result:  # type(row) == <class 'tuple'>   ex: (87,)
            result_list.append(row[0])  #  轉成int list
        maxid = max(result_list)
        if maxid > 1:
            search_index = maxid + 1


except ModuleNotFoundError:
    use_mysql = False
    search_index = 1
    print('[warning] not use mysql')

print('[mySQL]set search_index = ' + str(search_index))


class tw_datetime():
	def now_str():
		tw = pytz.timezone('Asia/Taipei')
		dt_str = datetime.datetime.now(tw).strftime("%Y-%m-%d %H:%M:%S")
		return dt_str
	def now_datetime():
		tw = pytz.timezone('Asia/Taipei')
		dt = datetime.datetime.now(tw)
		return dt

#def True_the_init():


app = Flask('MYapp')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/isme" , methods=["GET"])
def check_me():
    return "test_token" , 200

@app.route("/poster" , methods=["GET"])
def check_updata():
    gate_sw = False
    try:
        verify_token = request.args.get('token')
        if verify_token == 'test_token':
            gate_sw = True
        else:
            return jsonify({'error-code':'502', 'error-message':'token is Incorrect'})
    except KeyError:
        print("token Failed")
        return jsonify({'error-code':'501', 'error-message':"token Failed"})

    init_dictList = list()
    try:
        with open('menus_init_file.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile) # reader 是一個 2D list
            for data in reader:
                obj_dict = dict()
                obj_dict['menu'] = data[0]
                obj_dict['cost'] = data[1]
                obj_dict['hint'] = data[2]
                init_dictList.append(obj_dict)
    except:
        print(traceback.format_exc())

    if gate_sw:
        re_data = dict()
        re_data = {
            'base-root':
            {
                'menus-init': init_dictList
            }
        }
        #data_json = json.dumps(re_data)
        return jsonify(re_data)

@app.route("/servedMenu/<table_number>" , methods=["GET"])
def return_menusOfserved(table_number):
    gate_sw = False
    try:
        verify_token = request.args.get('token')
        if verify_token == 'servedMenu_token':
            gate_sw = True
        else:
            print("token not good")
            return jsonify({'error-code':'502', 'error-message':'token is Incorrect'})
    except KeyError:
        print("token Failed")
        return jsonify({'error-code':'501', 'error-message':"token Failed"})

    if gate_sw:
        # 取得該桌號的出菜列表list( dict() )
        # 如果沒找到則 s_menu_list 長度為0
        s_menu_list = findDictList_tableOf(table_number)
        re_data = dict()
        re_data = {
            'base-root':
            {
                'reg-gets': s_menu_list
            }
        }
        return jsonify(re_data)


    

@app.route("/download_menufile" , methods=["GET"])
def out_csvfile():
    #print("out_csvfile start")
    gate_sw = False
    try:
        verify_token = request.args.get('token')
        if verify_token == 'download_token':
            gate_sw = True
        else:
            print("token not good")
            return jsonify({'error-code':'502', 'error-message':'token is Incorrect'})
    except KeyError:
        print("token Failed")
        return jsonify({'error-code':'501', 'error-message':"token Failed"})

    if gate_sw:
        #print('token good')
        directory = os.getcwd()  # 假设在当前目录
        return send_from_directory(directory, 'menus_init_file.csv', as_attachment=True)

hub_list = list()
def creat_postHub(hub_str):
    global hub_list
    hub_list.append(hub_str)
    t_del = threading.Thread(target = waiting_delet_hub, args=(hub_str,))
    t_del.start()

def waiting_delet_hub(del_hub_str):
    global hub_list
    # 等待5分鐘
    time.sleep(300)
    list_index = 0
    for hub_key in hub_list:
        if hub_key == del_hub_str:
            del hub_list[list_index]
        list_index += 1

def findDictList_tableOf(target_table):
    global reg_table
    finded_list = list()
    for line in reg_table:
        # 參考用 new_menu = [tabel,menu,val,date,other,index]
        if line[0] == target_table: # line[0]為table的位置
            name = line[1]
            cost = str(get_cost(name))
            value = line[2]
            d = dict()
            d['menu'] = name
            d['cost'] = cost
            d['value'] = value
            finded_list.append(d)

    return finded_list

def regRemove(target_table):
    global reg_table
    #max_row = len(reg_table) - 1
    while True:
        row_index = 0
        for line in reg_table:
            # 參考用 new_menu = [tabel,menu,val,date,other,index]
            if line[0] == target_table: # line[0]為table的位置
                del reg_table[row_index]
                break
            row_index += 1

        if row_index == len(reg_table):
            break

    print('remove complate')

    
    

@app.route("/upload_menufile/<hub>" , methods=["POST"])
def in_csvfile(hub):
    global hub_list
    have_hub = False

    # 確認節點是否允許
    for hub_key in hub_list:
        if hub_key == hub:
            have_hub = True
    if not have_hub:
        return "NO hub", 200

    #m_file = request.form['file']  # str
    m_file_byte = request.get_data()
    print(len(m_file_byte))
    print(m_file_byte)
    try:

        directory = os.getcwd()  # 假设在当前目录
        filename = "menus_init_file.csv"

        #print(m_file)
        #encode_file = m_file.encode(encoding='UTF-8')
        #print(decoded_file)

        with open(filename, 'wb') as csvfile:
            csvfile.write(m_file_byte)
    except:
        print(traceback.format_exc())
        return "upload_failed", 200
        
    return "upload_comlete", 200
    


cutIn_sw = True
cutIn_minutes = 5
file_table = list()
reg_table = list()
def menu_sort(new_list, remove_index = None, moveReg = False):
    global file_table
    global cutIn_sw
    global reg_table
    #print('load global file_table')
    #print(file_table)
    if not remove_index:
        if len(file_table) == 0:
            #print('first data')
            file_table.append(new_list) # 如果是空的直接插入第一筆資料
            return file_table
        else:
            if cutIn_sw:
                #print('more data....')
                for r in range(1 , len(file_table) + 1):  # 由下往上找
                    index = r * -1
                    if file_table[index][0] == new_list[0]: # 如果有相同桌號的訂單
                        #print('index = {0} , table e.q.'.format(index))
                        if index == -1: # 如果在最後尾找到目標，則直接新增於最後尾
                            #print('index is last , use .append')
                            file_table.append(new_list)
                            return file_table
                        else:
                            target_datetime = datetime.datetime.strptime(file_table[index][3], "%Y-%m-%d %H:%M:%S")
                            
                            target_datetime = target_datetime + datetime.timedelta(minutes=cutIn_minutes)
                            
                            new_datetime = datetime.datetime.strptime(new_list[3], "%Y-%m-%d %H:%M:%S")
                            
                            if new_datetime < target_datetime: # 如果新來的訂單沒有超過同桌訂單5分鐘
                                #print('file_table.insert({i}, {n})'.format(i=index + len(file_table),n=new_list))
                                file_table.insert(index + 1, new_list) # 插入同桌的最末尾
                                return file_table
                #print('file_table no insert , use .append')
                file_table.append(new_list) # 如果不符合同桌插隊則加入訂單最末尾
                return file_table
            else:
                file_table.append(new_list) # 不開啟同桌插隊
                return file_table


    else:
        print('menu_sort on remove_index')
        if int(remove_index) <= 0:
            print('remove_index Error')
            return

        else:
            line_count = 0
            for line in file_table:
                if remove_index == line[5]: # search_index的位置
                    if moveReg:
                        # 新增這行的資料到 收銀LIST
                        print("Index " + remove_index + " move to RegZone")
                        reg_table.append(file_table[line_count])
                    del file_table[line_count] # delet 該行(row)的資料
                    return file_table
                line_count += 1


def removeIndex(index, mod):
    global lock
    #print(type(index))
    #print(index)
    if mod == 0:
        removed_list = menu_sort([], remove_index = index)
    elif mod == 1:
        removed_list = menu_sort([], remove_index = index, moveReg = True)
    new_removed_list = copy.deepcopy(removed_list) # 生成新的LIST
    # 每一行最後尾插入priority(順位)，以防list順序亂掉
    priority = 1
    for i in range(len(new_removed_list)):
        new_removed_list[i].append(str(priority))
        priority += 1
    
    # 同步至父進程
    lock.acquire() # 锁住
    global request_list
    request_list[:] = [] # 初始化
    for add in new_removed_list:
        request_list.append(add)
    #print('in ' + __name__)
    #print(request_list)
    lock.release() # 释放

def re_cutIn_data(target_client):
    global cutIn_sw
    global cutIn_minutes
    send_msg = 're_cutIn {0} {1} {2}'.format(str(cutIn_sw), str(cutIn_minutes), str(target_client))
    Queue_send_to_TcpServer.put(send_msg)

def set_cutIn_config(sw_str, time_val_str):
    global cutIn_sw
    global cutIn_minutes
    if sw_str == 'on':
        cutIn_sw = True
    if sw_str == 'off':
        cutIn_sw = False
    cutIn_minutes = int(time_val_str)

def get_cost(name): # 用菜單的名子取得價錢(int)，如果沒找到則回傳-1
    with open('menus_init_file.csv', 'r', newline='', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile) # reader 是一個 2D list
        for data in reader:
            menu_str = data[0]
            cost_val = int(data[1])
            if name == menu_str:
                return cost_val
        return -1
        

      
        

@app.route("/poster" , methods=['POST'])
def request_of_app():
    global lock
    global search_index
    #global file_table

    if len(request.data) > 0:
        try:
            if not json.loads(request.data.decode('utf8'))['base-root'].__contains__('menu-requests'):
                print('!!! poster error : json key error !!!')
                return "Json key error", 200
        except:
            print('!!! poster error : Not json !!!')
            print(request.data)
            #print(request.form)
            return "Not json", 200

        j = json.loads(request.data.decode('utf8'))['base-root']['menu-requests']

    elif request.form.get('main', False):
        try:
            j = json.loads(request.form['main'])['base-root']['menu-requests']
        except:
            print('poster error : request.form errors')
            print(request.form['main'])
            return "form errors", 200
    else:
        print('poster error : other')
        #print(request.form)
        return "other", 200

    print("get ['menu-requests']")
    print(json.dumps(j, indent=4, sort_keys=True))

    if len(j) == 0:
        return "NULL", 200

    for d in j:
        menu = d['menu']
        val = d['value']
        try:
            tabel = d['table']
        except KeyError:
            tabel = "0"
        date = tw_datetime.now_str()
        other = ''
        # 4/26 新增 index(索引)，為每個下單添增唯一ID，方便尋找
        index = str(search_index)
        search_index += 1
        new_menu = [tabel,menu,val,date,other,index]
        # 存至資料庫
        if use_mysql:
            with connection.cursor() as cursor:
                datetime = date.split(' ', 1)
                cost = get_cost(menu)
                if not cost >= 0: # 尋找失敗則回傳-1
                    print('get_cost Error')
                    cost = 0
                if other == '':
                    other = '(no hint)'
                sql = "INSERT INTO menu_requests (search_index, table_number, menu_name, menu_value, cost, date, time, other) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql,(index, tabel, menu, val, cost, datetime[0], datetime[1], other))
                connection.commit()
            print("Data commited.")

        #print('sort menu....')
        menu_table = menu_sort(new_menu) # 經過排序後，擁有優先順序確立
        #print('point 3')
        #print(menu_table)

    new_menu_table = copy.deepcopy(menu_table) # 生成新的LIST
    # 每一行最後尾插入priority(順位)，以防list順序亂掉
    priority = 1
    for i in range(len(new_menu_table)):
        new_menu_table[i].append(str(priority))
        priority += 1
        
    # 同步至父進程
    lock.acquire() # 锁住
    global request_list
    request_list[:] = [] # 初始化
    for add in new_menu_table:
        request_list.append(add)
    #print('in ' + __name__)
    #print(request_list)
    lock.release() # 释放
    #print(menu_table)
    #file_table.append(new_list)

    with open('requests_menu.csv', 'w', newline='') as csvfile:
        #print('file output')
        output_table = list()
        output_table.clear()
        writer = csv.writer(csvfile)
        for menu in new_menu_table:
            output_table.append(menu)
        for output_line in output_table:
            #print(output_table)
            #print(output_line)
            #output_line[3] = output_line[3].strftime("%Y-%m-%d %H:%M:%S")
            if output_line[4] == '':
                output_line[4] = '(no hint)'
        try:
            writer.writerows(output_table)
            # [tabel,menu,val,date,other,index,priority]
        except UnicodeEncodeError:
            print("output_table no save")

    return "OK", 200
    
request_list = None
lock = None
Queue_send_to_TcpServer = None
def root(strating, m_list, m_lock, rev_Queue, send_Queue):

    if strating == True:
        
        global lock
        lock = m_lock

        lock.acquire() # 锁住
        global request_list
        #print('m_list is = ')
        #print(m_list)
        request_list = m_list
        #request_list.append('test_str__FLASK')
        global Queue_send_to_TcpServer
        Queue_send_to_TcpServer = send_Queue
        #print('FLASK')
        lock.release() # 释放
        #print(type(lock))
        #print(lock)
        #time.sleep(1)
        t = threading.Thread(target = waiting_QueueEvent, args=(rev_Queue,))
        t.start()
        app.run(host='0.0.0.0', debug=True, port=21000, use_reloader=False)
        #print('FLASK_end')

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

            if event_type == 'removeIndex': # removeIndex 5 , removeIndex 2 ...
                removeIndex(event_values[0], 0)
            if event_type == 'servingIndex':
                removeIndex(event_values[0], 1)
            if event_type == 'cutIn':
                cutIn_mode = int(event_values[0])
                if cutIn_mode == 0:                  # cutIn 0 (192.168.1.103,3365)
                    target_client = event_values[1]
                    re_cutIn_data(target_client)
                elif cutIn_mode == 1:                # cutIn 1 on 6 , cutIn 1 off 15
                    sw_str = event_values[1]
                    time_val_str = event_values[2]
                    set_cutIn_config(sw_str, time_val_str)
            if event_type == 'creat_postHub':
                creat_postHub_str = event_values[0]
                creat_postHub(creat_postHub_str)

            if event_type == 'regRemove':
                removeTable = event_values[0]
                regRemove(removeTable)