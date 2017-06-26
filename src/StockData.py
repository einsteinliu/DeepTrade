import datetime
import time
import calendar
import requests
import yqd
import os.path

class QuoteInfoDaily(object):
    date = datetime.datetime(2000,1,1)
    openPrice = 0
    closePrice = 0
    lowPrice = 0
    highPrice = 0
    volume = 0
    def average_price(self):
        return (self.openPrice+self.closePrice+self.highPrice+self.lowPrice)/4.0
    def price_sum(self):
        return self.average_price()*self.volume

class StockData(object):
    url_head = 'http://ichart.yahoo.com/table.csv?'
    url_end = 'ignore=.csv'
    def __init__(self, symbol, start, end):
        self.symbol = symbol.upper()
        self.start = start
        self.end = end
        self.data = []
        self.data_lines = []
        self.file_name = self.symbol + '_' + self.start.strftime("%Y%m%d") + '_' + self.end.strftime("%Y%m%d")
        self.update()

    def weighted_average(self,begin_time,end_time):
        if begin_time<self.data[-1].date or end_time>self.data[0].date:
            return -1
        
        volume_sum = 0
        price_sum = 0
        for dataToday in self.data.__reversed__():
            if dataToday.date >= begin_time:
                if dataToday.date <= end_time:
                    volume_sum = volume_sum + dataToday.volume
                    price_sum = price_sum + dataToday.price_sum()
                else:
                    break
        return price_sum/volume_sum
    
    def save(self):
        f = open(self.file_name,'w')
        if len(self.data_lines) > 0:
            for data_line in self.data_lines:
                f.write(data_line+'\n')
        f.close()
    
    def load(self):
        if os.path.exists(self.file_name):
            with open(self.file_name,'r') as openfileobject:
                for line in openfileobject:
                    self.data_lines.append(line.replace('\n',''))
            return True
        else:
            return False

    def parseDailyData(self,data_string):
        quoteInfoDaily = QuoteInfoDaily()
        infoLines = data_string.split(',')
        quoteInfoDaily.date = datetime.datetime.strptime(infoLines[0],'%Y-%m-%d')
        quoteInfoDaily.openPrice = float(infoLines[1])
        quoteInfoDaily.highPrice = float(infoLines[2])
        quoteInfoDaily.lowPrice = float(infoLines[3])
        quoteInfoDaily.closePrice = float(infoLines[5])
        quoteInfoDaily.volume = int(infoLines[6])
        return quoteInfoDaily

    def update(self):
        del self.data[:]
        if not self.load():
            self.data_lines = yqd.load_yahoo_quote(self.symbol,self.start.strftime("%Y%m%d"),self.end.strftime("%Y%m%d"))
            self.save()
        #url = self.construct_url()
        #dataStr = requests.get(url).text
        #dataLines = dataStr.split('\n')        
        for data_line in self.data_lines[1:]:
            if data_line.__len__()>4:
                self.data.append(self.parseDailyData(data_line))

    def construct_url(self):
        url = self.url_head
        url = url +  "s=" + str(self.symbol) + "&"        
        url = url +  "a=" + str(self.start.month - 1) + "&"
        url = url +  "b=" + str(self.start.day) + "&"
        url = url +  "c=" + str(self.start.year) + "&"
        url = url +  "d=" + str(self.end.month - 1) + "&"
        url = url +  "e=" + str(self.end.day) + "&"
        url = url +  "f=" + str(self.end.year) + "&"
        url = url +  "g=d&"
        url = url + self.url_end
        return url
