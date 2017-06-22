#!/bin/env python3
# -*- coding:utf8 -*-
__author__ = 'think'

import datetime
import time
a = datetime.datetime(2017, 6, 19, 20, 36, 1)

print(time.strftime(a.strftime('%Y-%m-%d %H:%M:%S')))