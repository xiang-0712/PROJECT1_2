import selectors, socket
from binascii import unhexlify
import threading  # for threading.Thread
import math
import bch
import  time
# 创建默认的selectors对象
sel = selectors.DefaultSelector()

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
        if (start != -1 and end != -1):
            return mes[start + len(keystart):end]
        else:
            return -1





import socket
client=socket.socket()
addr=('127.0.0.1',30000)
client.connect(addr)
while True:
    print('input what you want to send ?')
    mesg ="我是一个无情的写代码机器|私は冷酷なコードライターです|I am a ruthless code writer|"*800
    mesg1 = input('>>')
    datasend = tools.bin2encode(mesg)
    len1 = len(datasend)
    print(len1)
    len3 = 4096
    roundnum = math.ceil(len1 / len3)
    for i in range(roundnum):
        while 1:  # 直到对方确认收到无误的帧后再发送下一个
            if i == roundnum - 1:
                len2 = roundnum * len3 - len1
                frames = datasend[i * len3:]
                frames.extend(['1'] * len2)
            else:
                frames = datasend[i * len3:(i + 1) * len3]

            origin_data = ''.join(frames)
            aa = list(map(''.join, zip(*[iter(origin_data)] * 1)))
            origin_data1 = [int(i) for i in aa]
            check_data = bch.encode_data(origin_data1)[:]
            en_data = origin_data1[:]
            en_data.extend(check_data)
            bb = [str(i) for i in en_data]
            en_data1 = ''.join(bb).encode()
            toubu = b'aa' + str(roundnum).encode() + b'bb' + str(i + 1).encode() + b'cc'
            send_data = b'1110111011111111' + toubu + en_data1 + b'1111111111101110'
            client.send(send_data)
            # time.sleep(0.4)
            recv_da = client.recv(5)  # 接受对方发送的数据
            if recv_da == b'1':
                break
client.close()




