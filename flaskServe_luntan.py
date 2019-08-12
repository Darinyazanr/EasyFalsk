#coding=utf-8
'''
Author:hutongfeng
To:论坛预估ctr,得到训练数据
'''
from flask import Flask
import flask_restful
from flask import request
from flask import jsonify
import time
import logging
import json
import random

app=Flask(__name__)
api=flask_restful.Api(app)
app.config['JSON_AS_ASCII'] = False

from sklearn.ensemble import GradientBoostingRegressor
import pickle

clf=pickle.load(open('./gbdt_ressgion.pickle','rb'))

import preData

class LunTanCtrPredict(flask_restful.Resource):
    def __init__(self):
        pass
        #self.log_file_name= 'logger-' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
        #self.handler = logging.FileHandler('./logs/' + self.log_file_name, 'a', encoding='utf-8')
        #self.handler.setLevel(logging.WARNING)
       # logging_format = logging.Formatter(
        #    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
        #self.handler.setFormatter(logging_format)
        #app.logger.addHandler(self.handler)

    def post(self):
        #print('post')
        if request.method == 'POST':
            try:
                data = request.get_json()
                initDic={}
                ID = data['contentID']  # bbs_id-post_id
                initDic['title']=data['title']
                initDic['new_tag']=data['new_tag']
                initDic['series_tags']=data['series_tags']
                initDic['business_category']=data['business_category']
                initDic['in_forum']=data['in_forum']
                initDic['is_jinghua']=data['is_jinghua']
                initDic['contentID']=ID
                x=preData.online2feature(initDic)
                prob=clf.predict(x.toarray())/10
                addProb=0


                #bug
                if len(data['title'])<=10:
                    addProb +=len(data['title'])*0.0007
                if len(data['title'])>10:
                    addProb +=len(data['title'])*0.00001
                if len(data['new_tag'])<=12:
                    addProb +=len(data['new_tag'])*0.0005
                if len(data['series_tags'])<=9:
                    addProb +=len(data['series_tags'])*0.0003
                if "美女" in data['business_category']:
                    addProb +=0.005
                if "提车" in data['business_category']:
                    addProb +=0.002
                if "用车" in data['business_category']:
                    addProb +=0.0015
                if "汽车实拍" in data['business_category']:
                    addProb +=0.004

                if initDic['is_jinghua']=="精选":
                    addProb+=0.03

                Lovetag=["美女","用车感受","评车","提车"]
                for tag in Lovetag:
                    if tag in  data['new_tag']:
                        addProb+=0.02

                for tag in Lovetag:
                    if tag in  data['title']:
                        addProb+=0.01

                seriesList=["宝马","奔驰","本田","丰田","吉利","大众"]

                for tag in seriesList:
                    if tag in  data['series_tags']:
                        addProb+=0.03

                #按天生成日志文件
                #nowStr='logger-' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
                #if nowStr != self.log_file_name:
                #    self.log_file_name=nowStr
                #    self.handler = logging.FileHandler('./logs/' + self.log_file_name, 'a', encoding='utf-8')

                #app.logger.warning('postDic#'+str(initDic))
                return {'contentID':ID,'prob':str((prob+addProb)*100),'code':200}
            except Exception as  e:
                print (e)
                return {'error': str(e)}

class feedBack(flask_restful.Resource):
    def __init__(self):
        pass
    def post(self):
        #print('post')
        if request.method == 'POST':
            try:
                data = request.get_json()
                #app.logger.warning('feedBack#'+str(data))
                return {'code':200}
            except Exception as  e:
                print (e)
                return {'error': str(e)}

api.add_resource(LunTanCtrPredict,'/ctrpredict')
api.add_resource(feedBack,'/feedback')
if __name__=='__main__':
    #app.run(host='0.0.0.0',port=8888,debug=False,threaded=True)
    app.run(host='0.0.0.0', port=9999,debug=False)
