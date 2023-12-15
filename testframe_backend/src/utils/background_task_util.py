from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# @TODO 定期删除TestSuiteTaskId表中没有的allure目录
# @scheduler.scheduled_job("interval", id="interval_test", seconds=3)
def tast_test():
    print("hello")
