# Logs Analysis Project
## DESCRIPTION

The project is about building a reporting tool for a newspaper. The tool has to use information from the database to discover what kind of articles the site's readers like.

We will work with data that could have come from a real-world web application, with fields representing information that a web server would record, such as HTTP status codes and URL paths. The web server and the reporting tool both connect to the same database, allowing information to flow from the web server into the report.



The program you write in this project will run from the command line. It won't take any input from the user. Instead, it will connect to that database, use SQL queries to analyze the log data, and print out the answers to some questions.
For this project, my task was to create a reporting tool that prints out reports( in plain text) based on the data in the given database. This reporting tool is a Python program using the psycopg2 module to connect to the database. This project sets up a mock PostgreSQL database for a fictional news website. 

Here are the questions the reporting tool should answer.

What are the most popular three articles of all time?
Who are the most popular article authors of all time?
On which days did more than 1% of requests lead to errors?

## RUNNING THE PROGRAM
To get started, I recommend the user use a virtual machine to ensure they are using the same environment that this project was developed on, running on your computer. You can download Vagrant and VirtualBox to install and manage your virtual machine. Use vagrant up to bring the virtual machine online and vagrant ssh to login.


Next, download the data [here]((https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip). You will need to unzip this file after downloading it. The file inside is called newsdata.sql. Put this file into the vagrant directory, which is shared with your virtual machine.
Load the database using psql -d news -f newsdata.sql.

Connect to the database using psql -d news.

Create the Views given below. Then exit psql.

Now execute the Python file - python logs_analysis.py.

CREATE THE FOLLOWING VIEWS FOR QUESTION 2 AND QUESTION 3:

Views for Question 3
'''
CREATE VIEW _err_daily as 
	SELECT to_char(time,'DD-MON-YYYY') as Date, count(log.status) as errors
	FROM log
   	WHERE status = '404 NOT FOUND'
   	GROUP BY 1
	ORDER BY 1;
'''

'''
CREATE VIEW _req_daily as 
	SELECT to_char(time,'DD-MON-YYYY') as Date, count(log.status) as requests
	FROM log
	GROUP BY 1
	ORDER BY 1;
'''
