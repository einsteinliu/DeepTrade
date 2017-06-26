import csv
import datetime
from dateutil.relativedelta import relativedelta
import StockData
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import time
from tensorflow.contrib import rnn

class TradeSimulator:
    StockPool = {}
    Net = 100000
    Cash = 100000
    Shares = {}
    def __init__(self,stock_list,start,end):
        for symbol in stock_list:
            self.StockPool[symbol] = StockData.StockData(symbol,start,end)
            self.StockPool[symbol].update()
            self.Shares[symbol] = 0

    def update_net(self,index):
        self.Net = 0
        for symbol in self.Shares.keys():
            self.Net = self.Net + self.Shares[symbol]*self.StockPool[symbol].data[index].closePrice
        self.Net = self.Net + self.Cash

    def sell(self, symbol, shares, price, index = -1):
        if symbol in self.Shares:
            if shares == -1:#sell all
                shares = self.Shares[symbol]
            self.Shares[symbol] = self.Shares[symbol] - shares
            self.Cash = self.Cash + shares*price
        if index != -1:
            self.update_net(index)    

    def buy(self, symbol, shares, price, index = -1):        
        if shares == -1:#buy will all the cash         
            shares = int(self.Cash/price)                        
        if symbol not in self.Shares:
            self.Shares[symbol] = 0
        self.Shares[symbol] += shares                                       
        self.Cash = self.Cash - self.Shares[symbol]*price                            
        if index != -1:
            self.update_net(index)
            
def isfloat(value):
    """check if a string is a float"""
    try:
        float(value)
        return True
    except ValueError:
        return False    
