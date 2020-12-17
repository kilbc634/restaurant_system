import time
import datetime

menus_list = list()
users_list = list()
def root(get_list, get_dict , m_lock):
    global menus_list
    global users_list
    #加載所需資料
    while True:
        
        m_lock.acquire()
        ''' # sample
        =============================================
        get_dict =
        {"('192.168.1.103', 3052)": 'administrator'}
        get_list =
        []
        =============================================
        =============================================
        get_dict =
        {}
        get_list =
        [['5', 'cake5555555555', '1', '2019-04-06 15:26:52', '', '2', '3'],]
        [[table, name, value, time, hint, index, priority],]
        =============================================
        '''
        
        menus_list.clear()
        for menu in get_list:
            menus_list.append(menu)
        users_list.clear()
        for key in get_dict.keys():
            users_list.append(get_dict[key][1])

        m_lock.release()

        broad_cast()

        time.sleep(0.4)

def broad_cast():
    global menus_list
    global users_list

    if len(users_list) > 0 :
        # 產生菜單列表
        menus_obj = list()
        menus_obj.clear()
        for line in menus_list:
            menu = dict()
            menu.clear()
            menu['menu'] = line[1]
            menu['value'] = line[2]
            menu['table'] = line[0]
            menu['time'] = line[3]
            menu['hint'] = line[4]
            menu['index'] = line[5]
            menu['priority'] = line[6]
            menus_obj.append(menu)
        # 發送給每個登入者
        for user in users_list:
            json_temp = dict()
            json_temp.clear()
            json_temp['base-root'] = {'online-requests' : menus_obj}
            try:
                user.send_json(json_temp)
            except:
                print('send Error for ' + user.user_name)




        

