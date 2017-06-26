import csv
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import time
import StockData


class DailyData:
    def __init__(self,stock_list,start,end):
        self.data_pool = {}    
        self.data_pool_normalized = {}    
        self.data_set = []
        self.label_set = []
        self.sorted_data = []     
        self.hist_length = 20
        self.future_length = 3
        self.n_feature = 5
        self.n_class = 7
        for symbol in stock_list:
            self.data_pool[symbol] = StockData.StockData(symbol,start,end)
            self.normalize_data()
            datas,labels = self.ConstructTrainingSet(self.data_pool_normalized[symbol].data)
            self.data_set.append(datas)
            self.label_set.append(labels)        
    
    def normalize_data(self):
        for symbol in self.data_pool.keys():
            curr_data_mat = np.zeros([len(self.data_pool[symbol].data),self.n_feature])
            for i in range(len(self.data_pool[symbol].data)):
                curr_data_mat[i,0] = self.data_pool[symbol].data[i].openPrice
                curr_data_mat[i,1] = self.data_pool[symbol].data[i].closePrice
                curr_data_mat[i,2] = self.data_pool[symbol].data[i].highPrice
                curr_data_mat[i,3] = self.data_pool[symbol].data[i].lowPrice
                curr_data_mat[i,4] = self.data_pool[symbol].data[i].volume
            for i in range(self.n_feature):
                curr_data_mat[:,i] = (curr_data_mat[:,i]-np.mean(curr_data_mat[:,i]))/np.std(curr_data_mat[:,i])

            self.data_pool_normalized[symbol] = curr_data_mat


    def sort_data(self):
        data_set_count = len(self.data_set)  
        class_count = np.zeros(self.n_class)      
        for i in range(data_set_count):
            class_count = class_count + self.label_set[i].sum(axis=0)
        for c in range(self.n_class):
            self.sorted_data.append(np.zeros([int(class_count[c]),self.hist_length,self.n_feature]))        
        n_c = np.zeros(self.n_class)
        for i in range(data_set_count):
            curr_data = self.data_set[i]
            curr_label = self.label_set[i]
            curr_label_index = np.nonzero(curr_label)[1]
            for j in range(curr_data.shape[0]):
                curr_class = int(curr_label_index[j])
                self.sorted_data[curr_class][int(n_c[curr_class]),:,:] = curr_data[j,:,:]
                n_c[curr_class] = n_c[curr_class] + 1
        

    def PickTrainingData(self,n_samples):
        class_count = np.zeros(self.n_class)        
        picked_data = np.zeros([int(n_samples),self.hist_length,self.n_feature])
        picked_label = np.zeros([int(n_samples),self.n_class])
        n_all_samples = 0
        for i in range(len(self.sorted_data)):
            n_all_samples = n_all_samples + self.sorted_data[i].shape[0]
        if n_all_samples < n_samples:
            return np.empty([1,1]),np.empty([1,1])
        curr_sample = 0
        curr_loop = 0
        while curr_sample < n_samples:
            curr_class = int(curr_loop)%int(self.n_class)
            if class_count[curr_class] < len(self.sorted_data[curr_class]):
                picked_data[curr_sample,:,:] = self.sorted_data[curr_class][int(class_count[curr_class]),:,:]
                picked_label[curr_sample,curr_class] = 1
                class_count[curr_class] = class_count[curr_class] + 1
                curr_sample = curr_sample + 1
            curr_loop = curr_loop + 1
        return picked_data,picked_label
                

    def ConstructTrainingSet(self,data):        
        data_count = data.shape[0] - self.future_length - self.hist_length
        DataSet = np.ndarray([data_count,self.hist_length,self.n_feature])
        LabelSet = np.zeros([data_count,self.n_class])        
        for i in range(data_count):
            #feed data
            for t in range(self.hist_length):
                for f in range(self.n_feature):
                    DataSet[i,t,f] = data[i+t,f]                

            # #normalize data
            # for k in range(self.n_feature):
            #     DataSet[i,:,k] = DataSet[i,:,k]/DataSet[i,:,k].min()

            #compute label
            max = -9999
            min = 999999999
            base = data[i+self.hist_length-1,1]
            for j in range(self.future_length):
                if max < data[i+self.hist_length+j,2]:
                    max = data[i+self.hist_length+j,2]
                if min > data[i+self.hist_length+j,3]:
                    min = data[i+self.hist_length+j,3]
            max_per = (max-base)/np.abs(base)
            min_per = (min-base)/np.abs(base)
            if max_per > 0.08:
                LabelSet[i,6] = 1                
            elif max_per > 0.04 and max_per <= 0.08:
                LabelSet[i,5] = 1                
            elif max_per > 0.02 and max_per <= 0.04:
                LabelSet[i,4] = 1                
            elif min_per < -0.02 and min_per >= -0.04:
                LabelSet[i,2] = 1                
            elif min_per < -0.04 and min_per >= -0.08:                
                LabelSet[i,1] = 1
            elif min_per < -0.08:
                LabelSet[i,0] = 1                
            elif max_per<0.02 and min_per>-0.02:
                LabelSet[i,3] = 1                   
        return DataSet,LabelSet