# Create your tasks here
from __future__ import absolute_import, unicode_literals
from aquila_v2.celery import app
from scripts import Inception
from scripts import functions


@app.task()
def add(x, y):
    return x + y


@app.task()
def mul(x, y):
    return x * y


@app.task()
def xsum(numbers):
    return sum(numbers)


@app.task()
def work_run_task(ince, flag):
    ret = ince.run_sql(flag)
    print(ret)

