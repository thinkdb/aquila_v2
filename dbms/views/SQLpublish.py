from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from dbms import forms
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from django.conf import settings
from scripts import functions
from scripts.functions import JsonCustomEncoder, get_uuid, result_tran, Logger
from scripts.Inception import Inception
from dbms.tasks import work_run_task
import json
import datetime, time


@method_decorator(AuthAccount, name='dispatch')
class SqlCommit(View):
    def __init__(self, **kwargs):
        super(SqlCommit, self).__init__(**kwargs)
        self.result_dict = {'data': {}, 'status': 0, 'error': '', 'running': 0, 'post_flag': 0}

    def get(self, request):
        user_info = GetUserInfo(request)
        obj = forms.SqlComForm()

        return render(request,
                      'inception/SqlCommit.html',
                      {'user_info': user_info,
                       'SqlComFormObj': obj,
                       'AuditResult': self.result_dict,
                       })

    def post(self, request):
        user_info = GetUserInfo(request)
        obj = forms.SqlComForm(request.POST)

        if obj.is_valid():
            self.result_dict['post_flag'] = 1
            work_order_id = get_uuid()
            host_id = obj.cleaned_data['host']
            port = obj.cleaned_data['port']
            db_name = obj.cleaned_data['db_name']
            run_time = obj.cleaned_data['run_time']
            sql_content = 'use ' + db_name + ';' + obj.cleaned_data['sql_content']

            db_info = models.HostAPPAccount.objects.filter(host_id=host_id,
                                                           host__app_type__app_name='MySQL',
                                                           app_port=port
                                                           ).values('host__host_ip', 'app_user', 'app_pass')
            # check db info
            if not db_info:
                self.result_dict['error'] = '无当前数据库信息，请确认数据库地址与端口号！！！'
            # check db login
            else:
                db_host = db_info[0]['host__host_ip']
                db_user = db_info[0]['app_user']
                db_passwd = db_info[0]['app_pass']

                db_check_flag = functions.DBAPI(db_host, db_user, db_passwd, port)
                if db_check_flag.error:
                    self.result_dict['error'] = '无连接当前数据库，请确认联系管理员！！！'
                else:
                    self.result_dict['status'] = 1

                sql_audit = functions.SplitSql(3, obj.cleaned_data['sql_content'])
                sql_audit_status = sql_audit.get_audit()
                if not sql_audit_status['status']:
                    self.result_dict['status'] = 0
                    self.result_dict['error'] = '语句不合法'

                if self.result_dict['status'] == 1:
                    # auto audit sql
                    ince = Inception(db_host=db_host,
                                     db_user=db_user,
                                     db_passwd=db_passwd,
                                     db_port=port,
                                     sql_content=sql_content)
                    result = ince.audit_sql()

                    if isinstance(result, dict):
                        self.result_dict['status'] = 0
                        self.result_dict['error'] = '无连接 Inception，请联系管理员！！！'
                    else:
                        self.result_dict = result_tran(result, self.result_dict)
                if obj.cleaned_data['is_commit'] == '1' and self.result_dict['status'] == 1:
                        # commit audit sql
                        self.result_dict['running'] = 1
                        master_result = functions.get_master(db_host, db_user, db_passwd, port, db_name)
                        master_ip = master_result['data']
                        # InceptionWorkOrderInfo
                        models.InceptionWorkOrderInfo.objects.create(
                            work_title=obj.cleaned_data['title'],
                            work_order_id=work_order_id,
                            work_user=user_info[0]['user_name'],
                            db_host=db_info[0]['host__host_ip'],
                            db_name=db_name,
                            master_host=master_ip,
                            review_user_id=obj.cleaned_data['review_name'],
                            work_cron_time=datetime.datetime.now() if run_time == None else run_time,
                            comm=obj.cleaned_data['comm']
                        )

                        # InceptionAuditDetail
                        for id in self.result_dict['data']:
                            models.InceptionAuditDetail.objects.create(
                                work_order_id=work_order_id,
                                sql_sid=id,
                                flag=1,
                                status=self.result_dict['data'][id]['status'],
                                status_code=self.result_dict['data'][id]['status_code'],
                                error_msg=self.result_dict['data'][id]['error_msg'],
                                sql_content=self.result_dict['data'][id]['sql'],
                                aff_row=self.result_dict['data'][id]['rows'],
                                rollback_id=self.result_dict['data'][id]['rollback_id'],
                                backup_dbname=self.result_dict['data'][id]['backup_dbname'],
                                execute_time=self.result_dict['data'][id]['execute_time'],
                                sql_hash=self.result_dict['data'][id]['sql_hash']
                            )

                        # InceAuditSQLContent
                        models.InceAuditSQLContent.objects.create(
                            work_order_id=work_order_id,
                            sql_content=sql_content
                        )
                        # WorkOrderTask
                        models.WorkOrderTask.objects.create(
                            work_order_id=work_order_id,
                            host_ip=master_ip,
                            app_user=db_user,
                            app_pass=db_passwd,
                            app_port=port,
                            db_name=db_name
                        )

        else:
            self.result_dict['error'] = json.dumps(obj.errors)
        return render(request,
                      'inception/SqlCommit.html',
                      {'user_info': user_info,
                       'SqlComFormObj': obj,
                       'AuditResult': self.result_dict,
                       })


@method_decorator(AuthAccount, name='dispatch')
class SqlAudit(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        audit_sql_info = models.InceptionWorkOrderInfo.objects.filter(
            review_user=user_info[0]['id'],
            review_status=10
        ).all()
        detail_sql_info = models.InceptionWorkOrderInfo.objects.filter(
            review_user=user_info[0]['id'],
            review_status=10
        ).all().values(
            'work_order_id',
            'inceptionauditdetail__sql_sid',
            'inceptionauditdetail__status',
            'inceptionauditdetail__error_msg',
            'inceptionauditdetail__sql_content',
            'inceptionauditdetail__aff_row',
        )

        return render(request, 'inception/SqlAudit.html', {'user_info': user_info,
                                                           'audit_sql_info': audit_sql_info,
                                                           'detail_sql_info': detail_sql_info})

    def post(self, request):
        result_dict = {'status': 0, 'error_msg': 1}
        audit_flag = request.POST.get('flag', None)
        wid = request.POST.get('wid', None)
        now_time = datetime.datetime.now()
        if audit_flag and wid:
            if audit_flag == '驳回':
                audit_flag = 1
            else:
                audit_flag = 0
            try:
                models.InceptionWorkOrderInfo.objects.filter(work_order_id=wid).update(review_status=audit_flag,
                                                                                       review_time=now_time)
                models.WorkOrderTask.objects.filter(work_order_id=wid).update(audit_status=audit_flag)
                result_dict['status'] = 1
            except Exception as e:
                result_dict['data'] = str(e)
        else:
            result_dict['data'] = '发送数据不对, 请联系管理员'
        return HttpResponse(json.dumps(result_dict))


@method_decorator(AuthAccount, name='dispatch')
class SqlRunning(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        run_work_info = models.InceptionWorkOrderInfo.objects.filter(work_user=user_info[0]['user_name'],
                                                                     review_status=0,
                                                                     work_status=10).all()
        detail_sql_info = models.InceptionWorkOrderInfo.objects.filter(
            review_user=user_info[0]['id'],
            review_status=0
        ).all().values(
            'work_order_id',
            'inceptionauditdetail__sql_sid',
            'inceptionauditdetail__status',
            'inceptionauditdetail__error_msg',
            'inceptionauditdetail__sql_content',
            'inceptionauditdetail__aff_row',
        )
        return render(request, 'inception/SqlRunning.html', {'user_info': user_info,
                                                             'run_work_info': run_work_info,
                                                             'detail_sql_info': detail_sql_info})

    def post(self, request):
        result_dict = {'status': 0, 'error_msg': 111, 'data': {}}
        run_flag = request.POST.get('flag', None)
        wid = request.POST.get('wid', None)
        if run_flag == '取消':
            models.InceptionWorkOrderInfo.objects.filter(work_order_id=wid).update(work_status=4)
            models.WorkOrderTask.objects.filter(work_order_id=wid, audit_status=0).update(work_status=4)
            result_dict['status'] = 1
        else:
            # 提交时，调用任务执行函数去执行任务， 接着返回提交任务成功的信息到前端显示

            # 获取任务列表
            task_info = models.WorkOrderTask.objects.filter(work_order_id=wid, audit_status=0, work_status=10).values(
                'work_order__inceauditsqlcontent__sql_content',
                'host_ip',
                'app_pass',
                'app_user',
                'app_port'
            )
            if not task_info:
                result_dict['error_msg'] = '工单不存在任务队中，请联系管理员'
                return HttpResponse(json.dumps(result_dict))

            # 执行任务前检测目标库能否正常通信
            master_result = functions.get_master(task_info[0]['host_ip'],
                                                 task_info[0]['app_user'],
                                                 task_info[0]['app_pass'],
                                                 task_info[0]['app_port'],
                                                 'test')
            if not master_result['status']:
                result_dict['error_msg'] = master_result['data']
                return HttpResponse(json.dumps(result_dict))

            # 更新工单状态为 进入执行队列, 添加定时任务后使用此状态
            # models.InceptionWorkOrderInfo.objects.filter(work_order_id=wid).update(work_status=2,
            #                                                                        work_run_time=datetime.datetime.now())
            result_dict['status'] = 1

            # 以下内容为任务执行函数中的内容
            master_ip = master_result['data']
            
            # 更新工单状态为执行状态
            models.InceptionWorkOrderInfo.objects.filter(work_order_id=wid).update(work_status=3,
                                                                                   work_run_time=datetime.datetime.now())

            models.InceptionAuditDetail.objects.filter(work_order_id=wid).update(status_code=8)

            # 提交到后台执行, Linux下需要改成： work_run_task.delay, windowns 如下
            work_run_task(master_ip, task_info[0]['app_user'],
                          task_info[0]['app_pass'],
                          task_info[0]['app_port'],
                          task_info[0]['work_order__inceauditsqlcontent__sql_content'],
                          wid)

        return HttpResponse(json.dumps(result_dict))


@method_decorator(AuthAccount, name='dispatch')
class SqlView(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        review_work_info = models.InceptionWorkOrderInfo.objects.filter(
            work_user=user_info[0]['user_name']).all()

        audit_work_info = models.InceptionWorkOrderInfo.objects.filter(review_user=user_info[0]['id'],
                                                                       review_status=10).all()

        detail_sql_info = models.InceptionWorkOrderInfo.objects.filter(
            work_user=user_info[0]['user_name']
        ).all().values(
            'work_order_id',
            'inceptionauditdetail__sql_sid',
            'inceptionauditdetail__status',
            'inceptionauditdetail__error_msg',
            'inceptionauditdetail__sql_content',
            'inceptionauditdetail__aff_row',
            'inceptionauditdetail__sql_hash',
            'inceptionauditdetail__status_code',
        )
        rollback = models.InceptionAuditDetail.objects.filter(flag=3).exclude(backup_dbname='None').all()

        return render(request, 'inception/SqlWorkView.html', {'user_info': user_info,
                                                              'review_work_info': review_work_info,
                                                              'audit_work_info': audit_work_info,
                                                              'detail_sql_info': detail_sql_info,
                                                              'rollback_flag': rollback})

    def post(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})


@method_decorator(AuthAccount, name='dispatch')
class SqlProgress(View):
    def get(self, request):
        time.sleep(2)
        sql_hash_str = request.GET.get('sql_hash', None)
        sql_hash_list = sql_hash_str.split('*')[1:]
        result_dict = {'status': 1}
        # result_dict = {'ptosc_flag': 0, 'wid_status': 1, 'wid': ''}
        # wid_status: 1=audit, 2=running, 3=over
        sql_hash_list = set(sql_hash_list)
        if not sql_hash_list:
            return HttpResponse(json.dumps(result_dict))
        # result_dict = {'wid':'', 'per': '', 'time_consuming': '', 'ptosc_flag': 0, 'wid_status': 1}
        # 需要查询sql_hash 对应工单的状态，如果是执行中，则获取进度，如果为执行结束，则返回 100， 如果未执行，则返回0
        for sql_hash in sql_hash_list:
            new_sql_hash = '*'+sql_hash
            sql_status = models.InceptionAuditDetail.objects.filter(sql_hash=new_sql_hash, flag__gt=1).values('flag')
            if sql_status:
                flag = sql_status[0]['flag']
            else:
                flag = 3

            if flag == 2:
                result_dict['status'] = 1
                ince_host = settings.INCEPTION['default']['INCEPTION_HOST']
                ince_port = settings.INCEPTION['default']['INCEPTION_PORT']
                conn = functions.DBAPI(host=ince_host, password='', port=int(ince_port), user='')
                result = conn.conn_query("inception get osc_percent '%s'" % new_sql_hash)
                if result:
                    result_dict[sql_hash] = {}
                    result_dict[sql_hash]['per'] = result[0][3]
                    result_dict[sql_hash]['time_consuming'] = str(result[0][4])
                else:
                    if sql_hash in result_dict.keys():
                        result_dict[sql_hash]['per'] = 100
                        result_dict[sql_hash]['time_consuming'] = 0
            else:
                result_dict['status'] = 1
                result_dict[sql_hash] = {}
                result_dict[sql_hash]['per'] = 100
                result_dict[sql_hash]['time_consuming'] = 0
        return HttpResponse(json.dumps(result_dict))
