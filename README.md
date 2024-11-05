https://www.canva.com/design/DAGTq3BIlkM/VO9UWLM_uv-B7PDZZMcbEg/edit?utm_content=DAGTq3BIlkM&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

# API

This application is a Flask-based API that sends messages to RabbitMQ queues. The API accepts `id`, `state`, `brightness`, and `color` as inputs and sends them as a JSON message to RabbitMQ.

## Installation and Setup

### Requirements

- Python 3.7+
- RabbitMQ server

### Step-by-Step Setup

1. **Clone the repository**:

```bash
git clone https://github.com/smartgem-tech-challenge/api.git
cd api
```

2. **Create and activate a virtual environment**:

```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. **Install required dependencies**:

```bash
pip3 install -r requirements.txt
```

4. **Configure environment variables**:

Create a `.env` file in the project root and add your configuration:

```makefile
BULBS=
HOUSES=
RABBITMQ_HOST=
RABBITMQ_USERNAME=
RABBITMQ_PASSWORD=
RABBITMQ_QUEUE_PREFIX=
```

5. **Run the application**:

To start the Flask server:

```bash
python3 app.py
```
