

# 项目设计

```
BCH编码模块
	---->bch.py
	---->gftable.py
	
工具函数类tools
    ---->bin2encode   mesg--->encode_data--->ob010...--->'010101..'--->['1','0',,]
    ---->bin2bytes    '0101001....'---->ob1010..--->decode_data
    ---->direction    定位，去帧头帧尾，读取数据
    
客户端
    ---->mesg---->datasend = tools.bin2encode(mesg)//01的strings------>  
    
    |if i == roundnum - 1:
    |            len2 = roundnum * len3 - len1
    |           frames = datasend[i * len3:]
    |            frames.extend(['1'] * len2)
    |        else:
    |            frames = datasend[i * len3:(i + 1) * len3]
    
    --->以4096为一帧-->check_data = bch.encode_data(origin_data1)[:]//使用BCH编码---->
    --->send_data = b'1110111011111111' + toubu + en_data1 + b'1111111111101110'//封装帧----->send
服务器
    ---->使用无阻塞select模块，可以同时并发多个客户端
    ---->将客户端发来的数据存入`.txt`文件,方便读取
    ---->过程为上面的逆过程
    
    
	
```

```
mesg--->encode_data--->ob010...--->'010101..'--->bch_data--->帧头+data+帧尾--->send

recv--->direction--->recv_data--->'001001...'---->ob01..--->decode_data--->mesg

```



没有加物理层模拟软件，可以实现传输长文本详细代码见

但物理层好像使用16进制传输的，传出`b'fccndkjshvls'`另一段收到数据为`b'\xf0\xfccndkjshvls\xda\x9d'`

所以现在还需要再传输和接受短分别加上这个转换的函数，使其能与现在的代码接上

```python
# -*- coding: utf-8 -*-
__author__ = 'xiang0712'
#服务器
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

```

```python
#客户端
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

```

```python
# -*- coding: utf-8 -*-
__author__ = 'xiang0712'
#bch.py
import gftable
'''-----------------全局参数--------------------------'''
m = 13
mask1= 2 ** m
mask2=mask1-1
polyred=0b0000000011011
t = 8
bch_n = 4200
bch_k = 4096
bch_c = bch_n - bch_k

g=[0,0,0,1,0,1,0,1,1,1,1,1,1,0,0,1,0,0,0,1,0,1,0,0,1,1,1,0,0,0,0,0,0,1,1,1,1,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1,0,0,1,1,1,0,0,0,0,1,1,1,0,1,0,0,0,0,0,1,1,1,0,0,0,1,0,1,1,1,0,0,0,1,0,0,1,1,1,1,1,0,1,1,0,0,1,0,0,0,1,1]




def encode_data(origin_data):
    zero = [0]
    bb = []
    bb.extend((bch_c)*zero)
    for i in range(bch_k):
        freeback= origin_data[i] ^ bb[0]
        if freeback != 0:
            for j in range(bch_c-1):
                if g[j] !=0 :
                    bb[j]=bb[j+1] ^freeback
                else:
                    bb[j]=bb[j+1]
            bb[bch_c-1] = g[bch_c-1] & freeback
        else:
            for j in range(bch_c-1):
                bb[j]=bb[j+1]
            bb[bch_c-1] = 0
    return bb

'''------------------将整数转为多项式表示---------------'''
def gf2mod(sInt):
    return [(sInt >> i) & 1
            for i in reversed(range(sInt.bit_length()))]
'''-----------------------------------------------------'''

'''-------------------gf列表---------------------------'''
table = {}
rev_table = {}
for (i, j) in enumerate(gftable.gftable):
    table[i + 1] = j
    rev_table[j] = i + 1
'''---------------------------------------------------'''

'''--------------------有限域的加法---------------------'''
"""Add two polynomials in GF(2^m)/g(x)"""
def gf2add(p1,p2):
    return p1 ^ p2
'''-----------------------------------------------------'''
'''--------------------有限域的乘法----------------------'''
"""Multiply two polynomials in GF(2^m)/g(x)"""
def gf2mul(p1,p2):
    p = 0
    while p2:
        if p2 & 1:
            p ^= p1
        p1 <<= 1
        if p1 & mask1:
            p1 ^= polyred
        p2 >>= 1
    return p & mask2
'''----------------------------------------------------'''
'''--------------------求伴随式子----------------------'''
def cal_syn(rcv_data,a):
    s = 0
    for i in range(len(rcv_data)):
        s = gf2add(gf2mul(s,a),rcv_data[i])
    return s

def syn(rcv_data):
    s = []
    a = [0]
    s.extend(16*a)
    for i in range(2*t):
        s[i] = cal_syn(rcv_data,table[i+1])
    # print ("伴随式：",s)
    # print (" ")
    return s
'''----------------------------------------------------'''

'''-----------------无求逆BM算法-------------------------'''
'''***********************1、计算di**********************'''
def di_cal(list_syn,list_sigma):
    mul_add = 0
    for i in range(len(list_syn)):
        mul_add = gf2add(mul_add,gf2mul(list_syn[i],list_sigma[i]))
    return mul_add
'''******************************************************'''
'''*********************2、计算sigma*********************'''
def sigma_op(list_sigma,list_lambda,di,d):
    sigma_new = [0,0,0,0,0,0,0,0,0]
    temp1 = [0,0,0,0,0,0,0,0,0]
    temp2 = [0,0,0,0,0,0,0,0,0]
    for i in range(len(list_sigma)):
        temp1[i] = gf2mul(d,list_sigma[i])
    list_lambda.pop()
    list_lambda.insert(0,0)
    for m in range(len(list_lambda)):
        temp2[m] = gf2mul(di,list_lambda[m])
    for n in range(len(list_sigma)):
        sigma_new[n] = gf2add(temp1[n],temp2[n])
    return sigma_new
'''****************************************************'''
def iBM(x):
    tmp = []
    list_syn    = [x[0],0,0,0,0,0,0,0,0]
    list_sigma  = [1,0,0,0,0,0,0,0,0]
    list_lambda = [1,0,0,0,0,0,0,0,0]
    d  = 1
    di = x[0]
    for i in range((2 * t)):
        if di == 0 :
            list_lambda.pop()
            list_lambda.insert(0,0)
            d = d
            list_sigma = list_sigma
        else :
            tmp = sigma_op(list_sigma,list_lambda,di,d)
            list_lambda = list_sigma
            list_sigma = tmp
            d = di
        if i < 2*t-1 :
            list_syn.pop()
            list_syn.insert(0,x[i+1])
        di = di_cal(list_syn,list_sigma)
    # print ("sigma :",list_sigma)
    # print (" ")
    return list_sigma

'''----------------------------------------------------'''

'''----------------------钱搜索------------------------'''
'''***************1、计算每一项乘积********************'''
def sigma_mul(sig,x,y):
    mul = sig
    for i in range(y):
        mul = gf2mul(mul,x)
    return mul
'''***************2、计算多项式的值********************'''
def poly_cal(sigma,x):
    sum = 0
    for i in range(len(sigma)):
        sum = gf2add(sum,sigma_mul(sigma[i],x,i))
    return sum
'''****************3、***********************'''
def chen_search(sigma,rcv_data):
    s = []
    a = [0]
    s.extend(4200*a)
    for i in range(len(rcv_data)):
        if poly_cal(sigma,table[i+3992]) == 0:
            print("error in %d" % (4199 - i))

            if rcv_data[i] == 0:
                s[i] = 1
            else :
                s[i] = 0
        else :
            s[i] = rcv_data[i]
    print(" ")
    return s
'''----------------------------------------------------'''

def decode_data(rcv_data):
    return chen_search(iBM(syn(rcv_data)),rcv_data)
##gftable.py文件
```

