#!/bin/env python3
# -*- coding:utf8 -*-
__author__ = 'think'

# import numpy as np
#
# c = np.array([[1, 2, 3, 4],
#               [4, 5, 6, 7],
#               [7, 8, 9, 10]])
# print(c[:, 2])


import sqlparse
sql = """
SELECT mi.id,
	       ifnull(mi.name, '') as name,
	       mi.longitude,
	       mi.latitude,
	       mi.province,
	       mi.city,
	       mi.app_type as appType,
	       mi.king_status as kingStatus,
	       (if(mi.app_type = 'gxfw',
	           if(mi.user_auth =1 OR mi.auth_status = 1,
	              1,
	              (SELECT a.auth_status
	               FROM merchant_auth a
	               WHERE a.merchant_id = mi.id AND a.auth_status = 1
	               ORDER BY a.join_time DESC
	               LIMIT 1)),
	           (SELECT a.auth_status
	            FROM merchant_auth a
	            WHERE a.merchant_id = mi.id AND a.auth_status = 1
	            ORDER BY a.join_time DESC
	            LIMIT 1)))
	          auth_status,
	       (SELECT GROUP_CONCAT(service_type_id)
	        FROM merchant_service_type t
	        WHERE t.merchant_id = mi.id)
	          serviceTypeIds,
	       (SELECT group_concat(t.service_type_name)
	        FROM service_type t
	        WHERE t.id IN (SELECT m.service_type_id
	                       FROM merchant_service_type m
	                       WHERE m.merchant_id = mi.id))
	          serviceTypeNames,
	       ifnull(
	          (SELECT u.nickname
	           FROM user_info u
	           WHERE u.id IN
	                    ((SELECT t.user_id
	                      FROM merchant_employees t
	                      WHERE     t.is_del = 0
	                            AND t.verification_status = 1
	                            AND t.employees_type = 1
	                            AND t.merchant_id = mi.id))
	           ORDER BY u.id
	           LIMIT 1),
	          '')
	          nickname,
	       ifnull((SELECT service_frequency
	               FROM merchant_statistics t
	               WHERE t.merchant_id = mi.id
	               LIMIT 1),
	              0)
	          AS serviceFrequency
		FROM merchant_info mi
		WHERE mi.is_del = 0 AND (mi.app_type = 'gxfw' OR (mi.NAME IS NOT NULL AND mi.NAME != ""))
		ORDER BY mi.id
		LIMIT 1120000, 10000
"""
# print(sqlparse.format(sql, reindent=True))

b = """/*master*/ \
SELECT cast(oi.id AS CHAR )AS orderId,
      cast(oi.user_id AS CHAR )AS userId
FROM order_info oi
WHERE flag =1
 AND is_immediate=0
 AND service_time < 2017-07-21 01:50:04'
 LIMIT 100 """

import re
for item in b.split(' '):
    if re.search('\'', item):
        print(item)