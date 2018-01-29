# coding: utf-8

from django.core.wsgi import get_wsgi_application
from leancloud import Engine
from leancloud import LeanEngineError
from leancloud import Object
from leancloud import Query
from datetime import datetime,timezone
import json
engine = Engine(get_wsgi_application())

class Doodle(Object):
    pass 

def timebefore(d):  
    chunks = (  
                       (60 * 60 * 24 * 365, u'年'),  
                       (60 * 60 * 24 * 30, u'月'),  
                       (60 * 60 * 24 * 7, u'周'),  
                       (60 * 60 * 24, u'天'),  
                       (60 * 60, u'小时'),  
                       (60, u'分钟'),  
     )  
    #如果不是datetime类型转换后与datetime比较
    if not isinstance(d, datetime):
        d = datetime(d.year,d.month,d.day)
    now = datetime.now(timezone.utc)
    delta = now - d
    #忽略毫秒
    before = delta.days * 24 * 60 * 60 + delta.seconds
    #刚刚过去的1分钟
    if before <= 60:
        return '刚刚'
    if(d.year != now.year):
        return '%s年%s月%s日'%(d.year,d.month,d.day)
    if(before > 60 * 60 * 24 * 7):
        return '%s月%s日'%(d.month,d.day) 
    for seconds,unit in chunks:
        count = before // seconds
        if count != 0:
            break
    return str(count)+unit+"前"

@engine.define
def explore(**params):
    page = 1
    if 'page' in params:
        page = params['page']
    pageSize = 10  
    skip = (page-1)*pageSize
    query = Doodle.query
    query.add_descending('createdAt')
    count = query.count()
    query.limit(10)
    query.skip(skip)
    doodles = query.find()
    ret = {}
    ret['code'] = 200
    dataList = []
    for doodle in doodles:
        data = {}
        data['id'] = doodle.id
        data['thumb'] = doodle.get('thumb')
        #data['time'] = timebefore(doodle.get('publishAt'))
        dataList.append(data)
    ret['count'] = count
    ret['hasMore'] = count > (page*pageSize) 
    ret['page'] = page    
    ret['data'] = dataList
    return ret


@engine.define
def detail(**params):
    try:
        id = params['id']
        query = Doodle.query
        doodle = query.get(id)
        data = {}
        data['id'] = doodle.id
        data['thumb'] = doodle.get('thumb')
        data['path'] = json.loads(doodle.get('path'))
        #data['time'] = timebefore(doodle.get('createdAt'))
        
        result = {'code':200,'data':data}
        return result
    except LeanCloudError as e:
        result = {'code':e.code,'message':e.error}
        return result