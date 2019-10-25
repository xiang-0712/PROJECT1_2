# -*- coding: utf-8 -*-
__author__ = 'xiang0712'

import  socket
from binascii import unhexlify
import math
import bch
import time
import threading
import select
from multiprocessing.pool import ThreadPool

class tools():
    # 转换为八位的二进制
    def bin2encode(s,key=None):
        if type(s) == type('a'):
            s = list(s.encode())
        if key==1:
            return ''.join([bin(c)[2:].zfill(8) for c in s])
        temp=''.join([bin(c)[2:].zfill(8) for c in s])
        list1 = list(map(''.join, zip(*[iter(temp)] * 1)))
        return list1
        # 二进制转换为字节流
    def bin2bytes(Frames, key=None):
        res = b''
        # 调试的时候试下将其改为type（Frames）==list
        if type(Frames) == type(['1', '2']):
            Frames1 = []
            for i in Frames:
                for j in i:
                    Frames1 += j
                Frames = ''.join(Frames1)
        s = list(map(''.join, zip(*[iter(Frames)] * 8)))
        for i in s:
            binary = eval('0b' + i)
            # tmp=bytes(binary)[2:]
            tmp = unhexlify(hex(binary)[2:])
            res += tmp
        return res
    def divide(self,str):
        l=len(str)
        tmp=math.ceil(l/8)
        res=[]
        for i in range(tmp):
            if i==tmp:
                tmp1=str[i*8:]
            else:
                tmp1=str[i*8:(i+1)*8]
            res.append(tmp1)
        return(res)
    def direction(mes, keystart, keyend):
        # find函数，返回值为该str中的位置
        mes=mes.decode()
        start = mes.find(keystart)
        end = mes.find(keyend)
        aa=mes.find('aa')
        bb=mes.find('bb')
        cc=mes.find('cc')
        if (start != -1 and end != -1):
            data_Frame=mes[cc+2:end]
            sum_Frame = mes[aa+2:bb]
            num_Frame = mes[bb+2:cc]

            return data_Frame,sum_Frame,num_Frame
        else:
            return -1


def process(request, client_address):
    print(request,client_address)
    conn = request
    data=b''
    filename=input("请输入文件名称（带格式）：")
    while True:
        recv_data=conn.recv(9000)
        conn.send(b'1')
        data_Frame,sum_Frame,num_Frame = tools.direction(recv_data, '1110111011111111', '1111111111101110')
        print("总共发送",sum_Frame,"帧，已收到",num_Frame,"帧")

        tmpe = list(map(''.join, zip(*[iter(data_Frame)] * 1)))
        list_data = [int(i) for i in tmpe]
        correct_data = bch.decode_data(list_data)[:]
        correct_data=correct_data[:4096]
        list1_data = [str(i) for i in correct_data]
        if sum_Frame == num_Frame:
            tep=''.join(list1_data)
            end=tep.find('111111111')
            list1_data=list1_data[:end]
        orgin_data=tools.bin2bytes(list1_data)
        with open(filename, 'a', errors='ignore') as fp:
            fp.write(orgin_data.decode("utf8", errors="replace"))
        # data=data+orgin_data
        # if sum_Frame==num_Frame:
        #     with open(filename,'w+',errors='ignore') as fp:
        #         fp.write(data.decode("utf8", errors="replace"))


s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.bind(('127.0.0.1',30000))
s1.listen(5)
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.bind(('127.0.0.1',8021))
s2.listen(5)

while True:
    r, w, e = select.select([s1,],[],[],1)
    for s in r:
        print('get request')
        request, client_address = s.accept()
        t = threading.Thread(target=process, args=(request, client_address))
        t.daemon = False
        t.start()

s1.close()
s2.close()

