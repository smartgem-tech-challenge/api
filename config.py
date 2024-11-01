from dotenv import load_dotenv
import json
import os

load_dotenv()

class Config:
    BULBS = json.loads(os.getenv("BULBS"))
    HOUSES = {house["id"]: house["bulbs"] for house in json.loads(os.getenv("HOUSES"))}
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    RABBITMQ_QUEUE_PREFIX = os.getenv("RABBITMQ_QUEUE_PREFIX")