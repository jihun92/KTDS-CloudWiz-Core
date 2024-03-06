import os
import json
import shutil

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

class AnsibleHandler:

    def __init__(self, logger):
        self.logger = logger

    def run_playbook(self, playbook_path, host_list, host_vars, extra_vars, tags, verbosity, credentials, limit):
        
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

        # create inventory, use path to host config file as source or hosts in a comma separated string
        inventory = InventoryManager(loader=loader, sources=sources)

        # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        pbex = PlaybookExecutor(
            playbooks=[playbook_path],
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords={}
        )

        # 콜백 클래스를 사용하여 출력을 받음
        pbex._tqm._stdout_callback = ResultsCollectorJSONCallback(self.logger)

        try:
            result = pbex.run()
        except AnsibleError:
            pbex._tqm.cleanup()
            self.loader.cleanup_all_tmp_files() 

        self.logger.debug(f"## playbook result :{result}")

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

        return result

    
    def process(self, message_data):

        playbook_path = message_data.get("playbook_path")
        inventory = message_data.get("inventory")
        host_vars = message_data.get("host_vars", {})
        extra_vars = message_data.get("extra_vars", {})
        tags = message_data.get("tags", [])
        verbosity = message_data.get("verbosity", 1)
        credentials = message_data.get("credentials")
        limit = message_data.get("limit", 0)

        self.run_playbook(playbook_path, inventory, host_vars, extra_vars, tags, verbosity, credentials, limit)
        return "AnsibleHandler"
