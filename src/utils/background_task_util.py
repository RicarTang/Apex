from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


# @scheduler.scheduled_job("interval", id="interval_test", seconds=3)
def tast_test():
    print("hello")
