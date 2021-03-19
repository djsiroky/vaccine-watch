import os

from apscheduler.schedulers.blocking import BlockingScheduler

from vaccine import check_for_appointments
from notify.twilio import send_message_to_twilio

sched = BlockingScheduler()
print("starting")
if "TWILIO_AUTH_TOKEN" in os.environ:
    send_message_to_twilio('Vaccine Watch server starting up')

# Ideally we would have one process schedule the jobs
# and another process run the jobs, but this is fine for now.
@sched.scheduled_job("interval", seconds=int(os.environ["VACCINE_CHECK_INTERVAL"]))
def vaccine_checker():
    check_for_appointments()


sched.start()
