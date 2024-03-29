# ansible_handler.py
from datetime import datetime
import os
import json
import shutil
import socket
import uuid
import pytz

import ansible.constants as C
from ansible.cli import CLI
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import context
from ansible.executor.playbook_executor import PlaybookExecutor
from modules.result_callback import ResultsCollectorJSONCallback
from config.logger_setting import Logger


class AnsibleHandler:

    def __init__(self, rabbit_mq_handler):
        self.logger = Logger()
        self.rabbit_mq_handler = rabbit_mq_handler

    def run_playbook(self, playbook_path, host_list, host_vars, extra_vars, tags, verbosity, credentials):

         # since the API is constructed for CLI it expects certain options to always be set in the context object
        context.CLIARGS = ImmutableDict(connection='smart', module_path="", forks=10, become=False,
                                    become_method='sudo', become_user='root', check=False, diff=False,
                                    verbosity=verbosity, private_key_file=credentials['ssh_key'], remote_user=credentials['username'],
                                    syntax=False, start_at_task=None)
        
        # required for
        # https://github.com/ansible/ansible/blob/devel/lib/ansible/inventory/manager.py#L204
        sources = ','.join(host_list)
        if len(host_list) == 1:
            sources += ','

        # initialize needed objects
        loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files

        # Instantiate our ResultsCollectorJSONCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
        results_callback = ResultsCollectorJSONCallback(self, self.rabbit_mq_handler)

        # create inventory, use path to host config file as source or hosts in a comma separated string
        inventory = InventoryManager(loader=loader, sources=sources)

        # VariableManager 정의
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        # 전역 호스트 변수 처리
        if extra_vars:
            variable_manager._extra_vars.update(extra_vars)
            self.logger.info(f"extra_vars : {variable_manager.extra_vars} ")

        # 호스트 변수 처리
        if host_vars:
            self.logger.info(f"host_vars: {host_vars}")
            for host_name in host_vars:
                host_vars = host_vars[host_name]
                for key, value in host_vars.items():
                    variable_manager.set_host_variable(host_name, key, value)

        pbex = PlaybookExecutor(
            playbooks=[playbook_path],
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords={}
        )

        # 콜백 클래스를 사용하여 출력을 받음
        results_callback = ResultsCollectorJSONCallback(self, self.rabbit_mq_handler)
        pbex._tqm._stdout_callback = results_callback

        try:
            result = pbex.run()
            self.logger.info(f"playbook Run !! : {result}")
        except AnsibleError:
            pbex._tqm.cleanup()
            self.loader.cleanup_all_tmp_files() 
            self.logger.error(f"[Error] except AnsibleError :{result}")


        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

        return results_callback.get_summary()
    
    # 삭제 예정
    def run_playbook_v0(self, playbook_path, host_list, host_vars, extra_vars, tags, verbosity, credentials):

         # since the API is constructed for CLI it expects certain options to always be set in the context object
        context.CLIARGS = ImmutableDict(connection='smart', module_path="", forks=10, become=False,
                                    become_method='sudo', become_user='root', check=False, diff=False,
                                    verbosity=verbosity, syntax=False, start_at_task=None)
        
        # required for
        # https://github.com/ansible/ansible/blob/devel/lib/ansible/inventory/manager.py#L204
        sources = ','.join(host_list)
        if len(host_list) == 1:
            sources += ','

        # initialize needed objects
        loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files

        # Instantiate our ResultsCollectorJSONCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
        results_callback = ResultsCollectorJSONCallback(self, self.rabbit_mq_handler)

        # create inventory, use path to host config file as source or hosts in a comma separated string
        inventory = InventoryManager(loader=loader, sources=sources)

        # VariableManager 정의
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        # 전역 호스트 변수 처리
        if extra_vars:
            variable_manager._extra_vars.update(extra_vars)
            self.logger.info(f"extra_vars : {variable_manager.extra_vars} ")

        # 호스트 변수 처리
        if host_vars:
            self.logger.info(f"host_vars: {host_vars}")
            for host_name in host_vars:
                host_vars = host_vars[host_name]
                for key, value in host_vars.items():
                    variable_manager.set_host_variable(host_name, key, value)

        # ## var1

        tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords={},
        stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
        )
        
        play_source = dict(
            name="Ansible Play",
            hosts=host_list,
            gather_facts='no',
            tasks=[
                dict(action=dict(module='pause', args=dict(seconds=0.1))),
                dict(action=dict(module='debug', args=dict(msg='HI'))),
                dict(action=dict(module='pause', args=dict(seconds=0.1))),
                dict(action=dict(module='debug', args=dict(var='var1'))),
                dict(action=dict(module='pause', args=dict(seconds=0.1))),
                dict(action=dict(module='debug', args=dict(var='ex_var1'))),
            ]
        )



        # Create play object, playbook objects use .load instead of init or new methods,
        # this will also automatically create the task objects from the info provided in play_source
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

        # Actually run it
        try:
            result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
        finally:
            # we always need to cleanup child procs and the structures we use to communicate with them
            tqm.cleanup()
            if loader:
                loader.cleanup_all_tmp_files()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

        return results_callback.get_summary()

    
    def process(self, header_dict, body_dict):

        self.request_msg_header_dict = header_dict
        self.request_msg_body_dict = body_dict
        
        playbook_path = body_dict.get("playbook_path")
        inventory = body_dict.get("inventory")
        host_vars = body_dict.get("host_vars", {})
        extra_vars = body_dict.get("extra_vars", {})
        tags = body_dict.get("tags", [])
        verbosity = body_dict.get("verbosity", 1)
        credentials = body_dict.get("credentials")

        self.send_start_msg()
        
        summary = self.run_playbook(playbook_path, inventory, host_vars, extra_vars, tags, verbosity, credentials)

        self.send_end_msg(summary)

        return "AnsibleHandler"
    
    def get_request_msg_header_dict(self):
        return self.request_msg_header_dict
        
    def get_request_msg_header_message_id(self):
        header = self.get_request_msg_header_dict()
        return header.get("message_id")
    
    def get_request_msg_header_message_type(self):
        header = self.get_request_msg_header_dict()
        return header.get("message_type")

    def get_request_msg_header_req_queue(self):
        header = self.get_request_msg_header_dict()
        return header.get("req_queue")
    
    def get_request_msg_header_res_queue(self):
        header = self.get_request_msg_header_dict()
        return header.get("res_queue")
    
    def get_request_msg_header_source_system(self):
        header = self.get_request_msg_header_dict()
        return header.get("source_system")
    
    def get_request_msg_header_timestamp(self):
        header = self.get_request_msg_header_dict()
        return header.get("timestamp")
    
    def get_request_msg_body_dict(self):
        return self.request_msg_body_dict

    def get_request_msg_body_playbook_path(self):
        body = self.get_request_msg_body_dict()
        return body.get("playbook_path")

    
    def send_start_msg(self):

        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_time = datetime.now(korea_timezone)
        current_time = korea_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        header_dict = {}
        header_dict["message_id"] = str(uuid.uuid4())
        header_dict["message_type"] = "ANSIBLE.EXEC_RES"
        header_dict["req_queue"] = self.get_request_msg_header_req_queue()
        header_dict["res_queue"] = self.get_request_msg_header_res_queue()
        header_dict["source_system"] = self.get_request_msg_header_source_system()
        header_dict["timestamp"] = self.get_request_msg_header_timestamp()
        header_dict["playbook_name"] = self.get_request_msg_body_playbook_path()

        body_dict = {}
        body_dict["parent_id"] = self.get_request_msg_header_message_id()
        body_dict["work_name"] = socket.gethostname()
        body_dict["start_time"] = current_time
        
        self.rabbit_mq_handler.publish_message(
            routing_key=header_dict["res_queue"], 
            header_dict=header_dict, 
            body_dict=body_dict)
        
        # self.logger.info(f"Send start Msg to {header_dict['res_queue']}, header : {header_dict}. body {body_dict}")

    def send_end_msg(self, summary):

        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_time = datetime.now(korea_timezone)
        current_time = korea_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        header_dict = {}
        header_dict["message_id"] = str(uuid.uuid4())
        header_dict["message_type"] = "ANSIBLE.PLAYBOOK_RESULT"
        header_dict["req_queue"] = self.get_request_msg_header_req_queue()
        header_dict["res_queue"] = self.get_request_msg_header_res_queue()
        header_dict["source_system"] = self.get_request_msg_header_source_system()
        header_dict["timestamp"] = self.get_request_msg_header_timestamp()
        header_dict["playbook_name"] = self.get_request_msg_body_playbook_path()

        body_dict = {}
        body_dict["parent_id"] = self.get_request_msg_header_message_id()
        body_dict["work_name"] = socket.gethostname()
        body_dict["end_time"] = current_time
        body_dict["summary"] = summary

        self.rabbit_mq_handler.publish_message(
            routing_key=header_dict["res_queue"], 
            header_dict=header_dict, 
            body_dict=body_dict)