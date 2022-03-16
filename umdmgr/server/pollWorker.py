#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
import pika
import time
try:
	from  ..helpers import mysql
	from  ..helpers import httpcaller
except ValueError:
	from  helpers import mysql
	from  helpers import httpcaller
from . import equipment
from . import bgtask
gv.sql = mysql.mysql()

# Step #1: Connect to RabbitMQ
connection = pika.BlockingConnection( pika.ConnectionParameters(host='localhost') )
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
def callback(ch, method, properties, body):
		print(" [x] Received %r" % (body,))
		time.sleep( body.count('.') )
		print(" [x] Done")
		
		
ch.basic_ack(delivery_tag = method.delivery_tag)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
						queue='task_queue')
channel.start_consuming()



