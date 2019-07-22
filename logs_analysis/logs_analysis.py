#!/usr/bin/env python3

import psycopg2 as psy 
import os


#conn = psy.connect("dbname=news")
#cur = conn.cursor()
#
#cur.execute("""CREATE VIEW _err_daily as 
#				SELECT to_char(time,'DD-MON-YYYY') as Date, count(log.status) as errors
#   					FROM log
#   					WHERE status = '404 NOT FOUND'
#   					GROUP BY 1
#					ORDER BY 1;
#				CREATE VIEW _req_daily as 
#					SELECT to_char(time,'DD-MON-YYYY') as Date, count(log.status) as requests
#    				FROM log
#    				GROUP BY 1
#    				ORDER BY 1;""")
#conn.commit()        
#conn.close()

conn = psy.connect("dbname=news")
cur = conn.cursor()

if "output.txt" in os.listdir("."):
	os.remove("output.txt")

file = open("output.txt","w")

question = "What are the most popular three articles of all time?"
file.write("\n{}\n".format(question))

cur.execute("""SELECT path, count (*) AS num  
			   FROM log 
			   WHERE path LIKE '%/article/%' AND status != '404 NOT FOUND' 
			   GROUP BY path 
			   ORDER BY num DESC 
			   LIMIT 3""")#"select path, count (*) as num from log group by path order by num desc")
rows = cur.fetchall()
for row in rows:
	res = row[0].split("/article/")[1] + " -- {} Views".format(row[1])
	print(res)
	file.write(res+"\n")

question= "Who are the most popular article authors of all time?"
file.write("\n{}\n".format(question))

cur.execute("""SELECT name, count (*) AS num 
			   FROM (log JOIN 
			   		(articles JOIN authors ON articles.author=authors.id) ON log.path LIKE '%' || articles.slug) 
			   GROUP BY 1 
			   ORDER BY 1""")
rows = cur.fetchall()
for row in rows:
	res = row[0] + " -- {} Views".format(row[1])
	print(res)
	file.write(res +"\n")



question= "On which days did more than 1% of requests lead to errors?"
file.write("\n{}\n".format(question))

cur.execute("""SELECT _err_daily.Date, concat(ROUND((100.0 * _err_daily.errors / _req_daily.requests), 2), '%')as perc_err
    			FROM _err_daily, _req_daily
    			WHERE _err_daily.Date = _req_daily.Date
				AND (((100.0 * _err_daily.errors / _req_daily.requests)) > 1)
				ORDER BY perc_err desc;""")#.format(err_daily, req_daily))
rows = cur.fetchall()
for row in rows:
	res = row[0] + " -- {}".format(row[1])
	print(res)
	file.write(res +"\n")

file.close()


        
