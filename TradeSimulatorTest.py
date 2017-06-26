import TradeSimulator
import time

simulator = TradeSimulator.TradeSimulator(['NVDA','NTES'],datetime.date(2010, 10, 1), datetime.date(2017, 3, 20))
simulator.buy('NTES',100,simulator.StockPool['NTES'].data[100].closePrice,100);





        
    
