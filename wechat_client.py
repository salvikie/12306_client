#!/usr/bin/env python3
# coding:UTF-8

import requests
import itchat
import time
import os
#import _thread as thread
import threading
from train_book import ticket_query
from train_book import pre_login
from train_book import login
from train_book import ticket_book
#import cv2


sendMsg = u"{消息助手}：暂时无法回复"
usageMsg = u"使用方法：\n1.运行CMD命令：cmd xxx (xxx为命令)\n" \
           u"-例如关机命令:\ncmd shutdown -s -t 0 \n" \
           u"2.自动刷票：auto\n" \
           u"3.查票：2018-10-10 或者 2018-10-10 衡阳东 深圳北 1\n" \
           u"4.获取验证码: G1002 或者G 随机刷票\n" \
           u"5.输入验证码登录并抢票：V34 \n" \
           u"6.打开关闭消息助手：ast 或者 astc"

flag = 0 #消息助手开关
train_date = ""
train_from = ""
train_to = ""
contact_id = ""
train_no = ""
message_list = []


'''
nowTime = time.localtime()
filename = str(nowTime.tm_mday)+str(nowTime.tm_hour)+str(nowTime.tm_min)+str(nowTime.tm_sec)+".txt"
myfile = open(filename, 'w')
'''

def is_vaild_date(strdate):
    try:
        if ":" in strdate:
            time.strptime(strdate, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(strdate, "%Y-%m-%d")
        return True
    except:
        return False


def train_book_main_loop():
    global flag
    global train_date
    global train_from
    global train_to
    global contact_id
    global train_no
    global message_list

    print("train_book_main_loop begin")

    while True:

        if len(message_list) != 0 and message_list[0][0:4] == "2018":
            #print(message_list[0])
            if is_vaild_date(message_list[0]) == False:
                itchat.send("日期不对", "filehelper")
                message_list.clear()
                continue

            if len(message_list) == 1 or len(message_list) == 2:
                dict_left_ticket = ticket_query(message_list[0])
                train_date = message_list[0]
                train_from = "default"
                train_to = "default"
                contact_id = "default"

            elif len(message_list) == 3:
                dict_left_ticket = ticket_query(message_list[0], message_list[1], message_list[2])
                train_date = message_list[0]
                train_from = message_list[1]
                train_to = message_list[2]
                contact_id = "default"

            else:
                dict_left_ticket = ticket_query(message_list[0], message_list[1], message_list[2])
                train_date = message_list[0]
                train_from = message_list[1]
                train_to = message_list[2]
                contact_id = message_list[3]

            while flag == 2 and len(dict_left_ticket) == 0:
                dict_left_ticket = ticket_query(message_list[0])

            if len(dict_left_ticket) != 0:
                keystr = ""
                for key, value in dict_left_ticket.items():
                    print("\"%s\":\"%s\"" % (key, value))
                    keystr = keystr + key + ":" + value + " "
                itchat.send(keystr, "filehelper")
            else:
                itchat.send("没有票", "filehelper")

            flag = 3
            message_list.clear()

        elif len(message_list) != 0 and message_list[0][0:1] == "G":
            pre_login()
            itchat.send('@img@%s' % u'12306_yzm.png', 'filehelper')

            if len(message_list[0]) == 1:
                train_no = "auto"
            else:
                train_no = message_list[0]
            #print(train_no)
            flag = 4

            message_list.clear()

        elif len(message_list) != 0 and message_list[0][0:1] == "V":
            verification_code = message_list[0].strip('V')
            print(verification_code)
            rc = login(verification_code)
            if rc == -1:
                itchat.send("验证码错误", "filehelper")
                flag = 3
            elif train_from == "default" and train_to == "default":
                # print(train_no + train_date)
                if contact_id == "default":
                    ticket_book(train_no, train_date)
                else:
                    ticket_book(train_no, train_date, "深圳北", "衡阳东", "ADULT", contact_id)

            else:
                if contact_id == "default":
                    ticket_book(train_no, train_date, train_from, train_to, "ADULT")
                else:
                    ticket_book(train_no, train_date, train_from, train_to, "ADULT", contact_id)

            message_list.clear()

        time.sleep(2)



@itchat.msg_register('Text')
def text_reply(msg):
    global flag
    message = msg['Text']
    fromName = msg['FromUserName']
    toName = msg['ToUserName']

    global train_date
    global train_from
    global train_to
    global contact_id
    global train_no
    global message_list

    if toName == "filehelper":
        '''
        if message == "cap":
            cap = cv2.VideoCapture(0)
            ret, img = cap.read()
            cv2.imwrite("weixinTemp.jpg", img)
            itchat.send('@img@%s'%u'weixinTemp.jpg', 'filehelper')
            cap.release()
        '''
        if message[0:3] == "cmd":
            os.system(message.strip(message[0:4]))
        if message == "ast":
            flag = 1
            itchat.send("消息助手已开启", "filehelper")
        if message == "astc":
            flag = 0
            itchat.send("消息助手已关闭", "filehelper")
        #auto
        if message == "auto":
            flag = 2
            itchat.send("自动抢票开启", "filehelper")
        if message == "manual":
            flag = 0
            itchat.send("自动抢票关闭", "filehelper")

        # 2018-10-10 深圳北 衡阳东 1
        if message[0:4] == "2018":
            message_list = message.split()
            #print("message_list len %d " % (len(message_list)))


        # G1002/G
        if message[0:1] == "G" and flag == 3:
            message_list = message.split()


        # V348
        if message[0:1] == "V" and flag == 4:
            message_list = message.split()


    elif flag == 1:
        itchat.send(sendMsg, fromName)
        '''
        myfile.write(message)
        myfile.write("\n")
        myfile.flush()
        '''

def get_news():
    url = "http://open.iciba.com/dsapi"
    r = requests.get(url)
    contents = r.json()['content']
    translation = r.json()['translation']
    return contents, translation

def parse_friendns():
    itchat.login()
    text = dict()
    friedns = itchat.get_friends(update=True)[0:]
    print(friedns)
    male = "male"
    female = "female"
    other = "other"
    for i in friedns[1:]:
        sex = i['Sex']
        if sex == 1:
            text[male] = text.get(male, 0) + 1
        elif sex == 2:
            text[female] = text.get(female, 0) + 1
        else:
            text[other] = text.get(other, 0) + 1

    total = len(friedns[1:])

    print("男性好友: %d" % (text[male]) + "\n" +
          "女性好友：%d" % (text[female]) + "\n" +
          "其他：%d" % (text[other]))


    print("总共: %d" % (total))



def send_news():
    try:
        # 登陆你的微信账号，会弹出网页二维码，扫描即可
        itchat.auto_login(hotReload=True)

        # 获取你对应的好友备注，这里的小明我只是举个例子
        # 改成你最心爱的人的名字。
        my_friend = itchat.search_friends(name=u'石头')
        # 获取对应名称的一串数字
        XiaoMing = my_friend[0]["UserName"]
        # 获取金山字典的内容
        message1 = str(get_news()[0])
        content = str(get_news()[1][17:])
        message2 = str(content)
        message3 = "来自你最爱的人"
        # 发送消息
        itchat.send(message1, toUserName=XiaoMing)
        itchat.send(message2, toUserName=XiaoMing)
        itchat.send(message3, toUserName=XiaoMing)
        # 每86400秒（1天），发送1次，
        # 不用linux的定时任务是因为每次登陆都需要扫描二维码登陆，
        # 很麻烦的一件事，就让他一直挂着吧
        # t = time(86400, send_news())
        # t.start()
    except:
        message4 = u"今天最爱你的人出现了 bug /(ㄒoㄒ)/~~"
        itchat.send(message4, toUserName=XiaoMing)

def wechat_main():
    #send_news()
    #parse_friendns()
    itchat.auto_login()
    itchat.send(usageMsg, "filehelper")
    itchat.run()


def main():
    t1 = threading.Thread(target=wechat_main)
    t1.setDaemon(True)
    t1.start()

    time.sleep(2)

    t2 = threading.Thread(target=train_book_main_loop)
    t2.setDaemon(True)
    t2.start()

    while True:
        pass

    #wechat_main()
    #thread.start_new_thread(train_book_main_loop(), ())


if __name__ == '__main__':
    main()


