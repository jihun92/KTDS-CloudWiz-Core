from ansible.plugins.callback import CallbackBase

class ResultsCollectorJSONCallback(CallbackBase):
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    # # Task 수행 결과가 ok일 경우 호출
    # def v2_runner_on_ok(self, result, *args, **kwargs):
    #     print("## [callback] v2_playbook_on_ok")
    #     result_code = 'ok'
    #     host = result._host
 
    #     self.count_task_by_each_host(result, result_code)
 
    #     retval = self.send_result_msg(result, result_code)
    #     return retval

    def v2_runner_on_start(self, host, task):
        pass
        # self.logger.info(f"Starting task {task} on {host}.")

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host.get_name()
        self.logger.info(f"{host} | SUCCESS => {result._result.get('msg')}")

    def v2_runner_on_failed(self, result, **kwargs):
        host = result._host.get_name()
        self.logger.error(f"{host} | FAILED => {result._result.get('msg')}")

    def v2_runner_on_skipped(self, result):
        host = result._host.get_name()
        self.logger.warning(f"{host} | SKIPPED")

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        self.logger.error(f"{host} | UNREACHABLE => {result._result.get('msg')}")

    def v2_runner_on_no_hosts(self):
        self.logger.warning("No hosts matched")

    def v2_runner_on_async_poll(self, result):
        host = result._host.get_name()
        self.logger.debug(f"{host} | ASYNC POLL => {result._result.get('msg')}")

    def v2_runner_on_async_ok(self, result):
        host = result._host.get_name()
        self.logger.debug(f"{host} | ASYNC OK => {result._result.get('msg')}")

    def v2_runner_on_async_failed(self, result):
        host = result._host.get_name()
        self.logger.error(f"{host} | ASYNC FAILED => {result._result.get('msg')}")
