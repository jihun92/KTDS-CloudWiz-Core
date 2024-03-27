from datetime import datetime
import pytz
import json
import os
import socket
import uuid
import yaml
from ansible.plugins.callback import CallbackBase
from config.logger_setting import Logger

# Create a callback plugin so we can capture the output
class ResultsCollectorJSONCallback(CallbackBase):


# class 초기화
    def __init__(self, ansible_handler, rabbit_mq_handler):
       
        super(ResultsCollectorJSONCallback, self).__init__()
 
        self.hosts = {}
        self.task_order = 0

        self.rabbit_mq_handler = rabbit_mq_handler
        self.ansible_handler = ansible_handler
        self.logger = Logger()
 
    # Playbook이 시작될 때 호출됨    
    def v2_playbook_on_play_start(self, play):
        # self.logger.info("## [callback] v2_playbook_on_play_start")
        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_time = datetime.now(korea_timezone)
        current_time = korea_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.playbook_start_time = current_time
        self.playbook_end_time = None

    # Playbook의 끝나면 호출됨
    def v2_playbook_on_stats(self, stats):
        # self.logger.info("## [callback] v2_playbook_on_stats")
        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_time = datetime.now(korea_timezone)
        current_time = korea_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.playbook_end_time = current_time

    # Task가 시작될 때 호출됨    
    def v2_playbook_on_task_start(self, task, is_conditional):
        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_time = datetime.now(korea_timezone)
        current_time = korea_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.tastk_start_time = current_time
 
    # Task 수행 결과가 unreachable일 경우 호출
    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.logger.info("## [callback] v2_playbook_on_unreachable")
        result_code = 'unreachable'
    #    self.host_unreachable[host.get_name()] = result
 
        self.count_task_by_each_host(result, result_code)
 
        retval = self.send_task_result_msg(result, result_code)
        return None
 
    # Task 수행 결과가 ok일 경우 호출
    def v2_runner_on_ok(self, result, *args, **kwargs):
        host = result._host
        self.logger.info("## [callback] v2_playbook_on_ok")
        result_code = 'ok'
 
        self.count_task_by_each_host(result, result_code)
 
        retval = self.send_task_result_msg(result, result_code)
        return None
 
    # Task 수행 결과가 failed일 경우 호출
    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
 
        if True == kwargs["ignore_errors"]:
            self.logger.info("## [callback] v2_playbook_on_failed (ignore_errors=True)")
            result_code = 'ignored'
 
        else:
            self.logger.info("## [callback] v2_playbook_on_failed")
            result_code = 'failed'
       
        self.count_task_by_each_host(result, result_code)
       
        retval = self.send_task_result_msg(result, result_code)
        return None
 
    # Task 수행 결과가 skipped일 경우 호출
    def v2_runner_on_skipped(self, result, *args, **kwargs):
        self.logger.info("## [callback] v2_runner_on_skipped")
        result_code = 'skipped'
        host = result._host
     
        self.count_task_by_each_host(result, result_code)
 
        retval = self.send_task_result_msg(result, result_code)
        return None
 

    # 각 Task 공통 작업 수행
    def count_task_by_each_host(self, result, result_code):
        host = result._host.name
        is_changed = result.is_changed()
 
        # 최종 실행 결과 리포트를 초기화 또는 total 값을 증가
        if host in self.hosts:
            self.hosts[host]['total'] += 1
        else:
            self.hosts[host] = dict(total=1, ok=0, failed=0, skipped=0, unreachable=0, changed=0, passed=False, ignored=0)
 
        # 실행결과가 ignored일 경우에도 ok를 증가
        if result_code == 'ignored':
            self.hosts[host]['ok'] += 1
 
        # 실행결과에 changed가 true이고 실행결과가 failed가 아닐 경우 changed를 증가
        if True == is_changed and result_code != 'failed':
            self.hosts[host]['changed'] += 1
 
        self.hosts[host][result_code] += 1
 
    # 응답 메시지 생성 및 전송
    def send_task_result_msg(self, result, result_code):
 
        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_time = datetime.now(korea_timezone)
        current_time = korea_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        host = result._host.name
        task_name = result._task.name
        try:
            module_name = result._task_fields['action']
        except:
            pass
        is_changed = result.is_changed()
        self.task_order += 1

        header_dict = {}
        header_dict["message_id"] = str(uuid.uuid4())
        header_dict["message_type"] = "ANSIBLE.TASK_RESULT"
        header_dict["req_queue"] = self.ansible_handler.get_request_msg_header_req_queue()
        header_dict["res_queue"] = self.ansible_handler.get_request_msg_header_res_queue()
        header_dict["source_system"] = self.ansible_handler.get_request_msg_header_source_system()
        header_dict["timestamp"] = self.ansible_handler.get_request_msg_header_timestamp()
        header_dict["playbook_name"] = self.ansible_handler.get_request_msg_body_playbook_path()

        # Init Message payload
        body_dict = dict()
        body_dict["parent_id"] = self.ansible_handler.get_request_msg_header_message_id()
        body_dict["work_name"] = socket.gethostname()
        body_dict["start_time"] = self.tastk_start_time
        body_dict["end_time"] = current_time
        body_dict['host'] = host
        body_dict['task_name'] = task_name
        body_dict['module_name'] = module_name
        body_dict['result_code'] = result_code
        body_dict['changed'] = is_changed
        body_dict['result'] = result._result
        body_dict['task_order'] = self.task_order
 
        body_dict = json.dumps(body_dict, indent=4)
        self.logger.info(f" Task Result : {body_dict}")


        self.rabbit_mq_handler.publish_message(
            routing_key=header_dict["res_queue"], 
            header_dict=header_dict, 
            body_dict=body_dict)
 
        return None
    
    def get_summary(self):
        return self.hosts