# -*- coding: utf-8 -*-
__author__ = 'xiang0712'

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

