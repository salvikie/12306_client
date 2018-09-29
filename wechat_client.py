#!/usr/bin/env python3
# coding:UTF-8

import requests
import itchat
import time
import os
from train_book import ticket_query
from train_book import pre_login
from train_book import login
from train_book import ticket_book
#import cv2


sendMsg = u"{消息助手}：暂时无法回复"
usageMsg = u"使用方法：\n1.运行CMD命令：cmd xxx (xxx为命令)\n" \
           u"-例如关机命令:\ncmd shutdown -s -t 0 \n" \
           u"2.获取当前电脑用户：cap\n3.启用消息助手(默认关闭)：ast\n" \
           u"4.关闭消息助手：astc"
flag = 0 #消息助手开关

'''
nowTime = time.localtime()
filename = str(nowTime.tm_mday)+str(nowTime.tm_hour)+str(nowTime.tm_min)+str(nowTime.tm_sec)+".txt"
myfile = open(filename, 'w')
'''

@itchat.msg_register('Text')
def text_reply(msg):
    global flag
    message = msg['Text']
    fromName = msg['FromUserName']
    toName = msg['ToUserName']

    global train_date
    global train_no

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

        # 2018-10-10
        if message[0:4] == "2018":
            dict_left_ticket = ticket_query(message)

            if len(dict_left_ticket) != 0:
                for key, value in dict_left_ticket.items():
                    print("\"%s\":\"%s\"" % (key, value))
                    itchat.send(key, "filehelper")

            while flag == 2 and len(dict_left_ticket) == 0:
                dict_left_ticket = ticket_query(message)

                if len(dict_left_ticket) != 0:
                    for key, value in dict_left_ticket.items():
                        print("\"%s\":\"%s\"" % (key, value))
                        itchat.send(key, "filehelper")
                    break

            flag = 3
            train_date = message[0:10]


        # G1002
        if message[0:1] == "G" and flag == 3:
            pre_login()
            itchat.send('@img@%s' % u'12306_yzm.png', 'filehelper')
            flag = 4
            train_no = message
            print(train_no)

        # V348
        if message[0:1] == "V" and flag == 4:
            verification_code = message.strip('V')
            print(verification_code)
            rc = login(verification_code)
            if rc == -1:
                itchat.send("验证码错误", "filehelper")
                flag = 3
            else:
                print(train_no + train_date)
                ticket_book(train_no, train_date)





















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


def main():
    send_news()
    #parse_friendns()


if __name__ == '__main__':
    itchat.auto_login()
    itchat.send(usageMsg, "filehelper")
    itchat.run()


