from config import Config
import json
import pika
import logging

class RabbitHandler:
    def __init__(self):
        # Declare queues for each house based on configuration.
        self.house_queues = {house: f"{Config.RABBITMQ_QUEUE_PREFIX}_house_{house}" for house in Config.HOUSES.keys()}
        
        self.connection = None
        self.channel = None

        # Create the connection to RabbitMQ.
        self.create_connection()
        # Declare the required RabbitMQ queues.
        self.declare_queues()

    def create_connection(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = Config.RABBITMQ_HOST,
                    credentials = pika.PlainCredentials(
                        username = Config.RABBITMQ_USERNAME,
                        password = Config.RABBITMQ_PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()

            logging.info("Connected to RabbitMQ.")
        except Exception as error:
            logging.error(f"Error connecting to RabbitMQ: {error}")

    def declare_queues(self):
        for house_queue in self.house_queues.values():
            self.channel.queue_declare(queue = house_queue)

            logging.info(f"Declared '{house_queue}' RabbitMQ queue.")

    def send_message(self, message, house):
        queue = self.house_queues.get(house)

        try:
            self.channel.basic_publish(
                exchange = "",
                routing_key = queue,
                body = json.dumps(message)
            )
        except pika.exceptions.AMQPConnectionError:
            logging.error("Connection to RabbitMQ lost, attempting to reconnect...")

            self.create_connection()
            self.send_message(message, house)
        except Exception as error:
            logging.error(f"Error sending RabbitMQ message: {error}")