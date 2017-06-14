# Create your tasks here
from __future__ import absolute_import, unicode_literals
from aquila_v2.celery import app


@app.task()
def add(x, y):
    return x + y


@app.task()
def mul(x, y):
    return x * y


@app.task()
def xsum(numbers):
    return sum(numbers)