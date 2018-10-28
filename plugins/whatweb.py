# encoding:utf8
from modules.mongo import MyMongodb
from config.config import config
import datetime
import uuid
import os,re

class  Whatweb:

    def __init__(self):
        self.table_name = 'whatweb'
        self.search_result = {'status':0,'msg':None,'res_list':[]}
        self.query = ''
        self.db = MyMongodb()
        self.db.set_database('whatweb')
        self.db.set_table(self.table_name)
        self.convert_search = {
            'ip':'plugins.IP.string',
            'target':'target',
            'status':'http_status',
            'charset':'plugins.Charset.string',
            'content-type':'plugins.Content-Type.string',
            'footer-hash':'plugins.Footer-Hash.string',
            'server':'plugins.HTTPServer.string',
            'links':'plugins.Links.string',
            'keywords':'plugins.Meta-Keywords.string',
            'meta':'plugins.MetaGenerator.string',
            'php':'plugins.PHP.version',
            'title':'plugins.Title.string',
            'by':'plugins.X-Powered-By.string'
        }

    def api(self,query):
        if query == '':
            for result in self.db.find_all():  # 查询所有
                if result['http_status'] != None:  # 将无效请求进行过滤
                    result['_id'] = str(result['_id'])
                    self.search_result['res_list'].append(result)
            self.search_result['status'] = 0
            self.search_result['msg'] = '查询成功！'
        else:
            key = ''
            value = ''
            search_query = {}
            like_query = {'$regex':None}
            query = query.strip().split(":", 1)
            if len(query) != 2:
                self.search_result['status'] = -1
                self.search_result['msg'] = '条件错误'
                return self.search_result
            value = query[1].strip()  # 数字

            if value.isdigit():
                value = int(value)  # 转化类型
            if self.convert_search.has_key(query[0].strip()) is False:
                self.search_result['status'] = -1
                self.search_result['msg'] = '条件错误'
                return self.search_result
            key = self.convert_search[query[0].strip()]
            if key != 'http_status':
                like_query['$regex'] = str(value)
                search_query[key] = like_query
            else:
                search_query[key] = value
            for result in self.db.find_all(search_query):  # 条件查询
                if result['http_status'] is not None:  # 将无效请求进行过滤
                    result['_id'] = str(result['_id'])
                    self.search_result['res_list'].append(result)
            self.search_result['status'] = 0
            self.search_result['msg'] =  "查询成功！"
        return self.search_result

    def run(self, target):
        command = "ruby {whatweb_path} {whatweb_default_args} {whatweb_plugins} {whatweb_plugins} {target}".format(
            whatweb_path=config['whatweb_path'],
            whatweb_default_args=config['whatweb_default_args'],
            whatweb_plugins=config['whatweb_plugins'],
            target=target)
        print "[+]Job " + command
        if config['process']:
            os.popen(command)
        else:
            os.system(command)

    def add(self,aps_scheduler,target):
        target = target.strip()
        match_result =re.match(r'[a-z:/0-9]{1,}',target)
        if match_result == None:
            self.search_result['status'] = 0
            self.search_result['msg'] = "添加失败！"
        else:
            self.search_result['status'] = 1
            self.search_result['msg'] = "添加成功！"
            time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            job_id = uuid.uuid4().hex
            aps_scheduler.add_job(id=job_id, func=self.run, trigger='date', args=(target,), next_run_time=time,name=target)
        return self.search_result
