import csv
import datetime
from dateutil.relativedelta import relativedelta
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import time
import DataDaily
from tensorflow.contrib import rnn

daily_data = DataDaily.DailyData(['NTES','NOAH','AAPL','MSFT'],datetime.date(2010, 10, 1),datetime.date(2017, 6, 7))
#daily_data.sort_data()
#t_d,t_c = daily_data.PickTrainingData(2000)
t_d = daily_data.data_set[0]
t_c = daily_data.label_set[0]

daily_data_test = DataDaily.DailyData(['NVDA','INTC'],datetime.date(2010, 10, 1),datetime.date(2017, 6, 7))
#daily_data_test.sort_data()
#test_d,test_c = daily_data_test.PickTrainingData(1000)
test_d = daily_data_test.data_set[0]
test_c = daily_data_test.label_set[0]

n_input = 5
n_hidden_state = 20
n_time_steps = 20
n_classes = 7

learning_rate = 0.001
training_iters = 20000

#data = StockData.StockData('AAPL',datetime.date(2010, 10, 1), datetime.date(2017, 6, 7))

print(t_d.shape)
print(t_c.shape)

w = tf.Variable(tf.random_normal([n_hidden_state, n_classes]))
b = tf.Variable(tf.random_normal([n_classes]))

x = tf.placeholder(tf.float32,[None,n_time_steps,n_input])
y = tf.placeholder(tf.float32,[None,n_classes])

x_ = tf.unstack(x,n_time_steps,1)
lstm_cell = rnn.rnn_cell.BasicLSTMCell(n_hidden_state,forget_bias=1.0)
outputs, states = rnn.rnn.rnn(lstm_cell, x_,initial_state=None,dtype=tf.float32)

y_ = tf.add(tf.matmul(outputs[-1],w),b)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=y_, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(y_,1), tf.argmax(y,1)), tf.float32))

init = tf.global_variables_initializer()

results = []
inn_results = []
curr_batch = 0
#saver = tf.train.Saver()
#saver.restore(sess, "model.ckpt")

with tf.Session() as sess:
    sess.run(init)
    for step in range(training_iters):
        if (curr_batch+1)*100 > (t_d.shape[0]-100):
            curr_batch = 0
        batch_x = t_d[curr_batch*100:curr_batch*100+100,:,:]
        batch_y = t_c[curr_batch*100:curr_batch*100+100,:]        
        sess.run(optimizer,feed_dict={x:batch_x,y:batch_y})
        curr_batch = curr_batch + 1
        if step % 50 == 0:           
            currResult = sess.run(accuracy, feed_dict={x: test_d, y: test_c})
            innrResult = sess.run(accuracy, feed_dict={x: t_d, y: t_c})
            results.append(currResult)
            inn_results.append(innrResult)
            #print(step,currResult)
            f = open('log.txt','w')
            for r in range(len(results)):
                f.write(str(results[r]) + ',' + str(inn_results[r]) + str('\n'))
            f.close();
        #save_path = saver.save(sess, 'D:\Study\DeepLearning\TensorFlow\model.ckpt')
