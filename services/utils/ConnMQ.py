import json
import pika

from config.config import Config as cfg

def send2MQ(pQueue, pExchange, pRoutingKey, pData):
    # Get the details of MQ
    credentials = pika.PlainCredentials(cfg.RABBITMQUSER, cfg.RABBITMQPWD)
    # Create Connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.RABBITMQIP,credentials=credentials,virtual_host=cfg.RABBITMQVHOST))
    # Create Channel
    channel = connection.channel()
    # decalre queue
    channel.queue_declare(queue=pQueue, durable=True)
    # publish data to the queue
    channel.basic_publish(exchange=pExchange, routing_key=pRoutingKey, body=pData)
    #print('Pushed Data to ESB')
    # close the connection
    connection.close()
    return {'result': 'success', 'data': 'Successfully pushed data to ESB'}