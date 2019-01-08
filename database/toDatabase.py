#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# TgBot - toDatabase.py
# 2019/1/7 17:17
# Author:Kencin <myzincx@gmail.com>

from database import config
import pymysql


class Monitor(object):
    table_name = 'monistorQueue'
    db = pymysql.connect(config.HOST, config.Username, config.Password, config.Database_name)
    cursor = db.cursor()

    def __init__(self, from_city=None, to_city=None, date=None):
        self.from_city = from_city
        self.to_city = to_city
        self.date = date

    def check_exits(self):
        sql = "SELECT price FROM %s WHERE fromArea = '%s' AND toArea = '%s' AND depTime = '%s'" % (self.table_name,
                                                                                                   self.from_city,
                                                                                             self.to_city, self.date)
        try:
            self.cursor.execute(sql)
            price = self.cursor.fetchone()  # 加快效率，获取一条就行
            if price:
                return price
            else:
                return False
        except Exception as e:  # 出现错误，则返回已存在，以便退出监控进程
            print(e)
            return True

    def insert(self):
        sql = "INSERT INTO %s VALUES ('%s', '%s,' '%s', '%d')" % (self.table_name, self.from_city, self.to_city, self.date, 0)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)

    def update(self, price):
        price = int(price)
        sql = "UPDATE %s SET price = %d WHERE fromArea = '%s' AND toArea = '%s' AND depTime = '%s'" % (self.table_name,
                                                                                             price, self.from_city,
                                                                                             self.to_city, self.date)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)

    def get_info(self):
        sql ="SELECT flight,depTime FROM %s" % (self.table_name)
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print(e)

    def select_all(self):
        sql ="SELECT * FROM %s" % (self.table_name)
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print("se;ect_all 函数出错！")
            print(e)
