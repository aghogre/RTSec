# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 19:31:01 2018

@author: RAVITHEJA
"""

sql_db_queries = [
    {
        "query_template": """SELECT * FROM samp2
                where CurrentDate = '{fetch_date}'""",
        "reduceDateByDays": [1],
        "Title": "Selects on prev date",
        "paramTypes": "single date",
        "postgresTable": "samp2"
    },
    {
        "query_template": """SELECT * FROM samp2
                where CurrentDate = '{fetch_date1}'
                or CurrentDate = '{fetch_date2}'  """,
        "reduceDateByDays": [2, 3],
        "Title": "Selects on prev dates",
        "paramTypes": "two dates",
        "postgresTable": "samp2"
    }
]
