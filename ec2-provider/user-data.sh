#!/bin/bash
yum update -y
yum upgrade -y

yum install -y \
    python3

echo "export PATH=/usr/local/bin:\$PATH" >> /root/.bashrc

python3 -m pip install \
    boto3 \
    flask \
    flask-restful \
    supervisor

mkdir -p /etc/supervisor/conf.d
mkdir /var/log/supervisor

# supervisor conf file
cat > /etc/supervisor/supervisor.conf<< EOF
[unix_http_server]
file=/var/run/supervisor.sock
chmod=0700

[inet_http_server]
port=127.0.0.1:9001

[supervisord]
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[include]
files = /etc/supervisor/conf.d/*.conf
EOF

# supervisor file for our todo app
cat > /etc/supervisor/conf.d/todo.conf<< EOF
[program:todo_app]
command = python3 todo.py
directory = /home/ec2-user/
autostart = true
autorestart = true
redirect_stderr = true
stdout_logfile = /var/log/todo.txt
environment = AWS_DEFAULT_REGION="__AWS_DEFAULT_REGION_PLACEHOLDER__"
EOF

# enable supervisor as a systemd service
cat > /etc/systemd/system/supervisord.service<< EOF
[Unit]
Description=Supervisor daemon

[Service]
Type=forking
ExecStart=/usr/local/bin/supervisord -c /etc/supervisor/supervisor.conf
ExecStop=/usr/local/bin/supervisorctl $OPTIONS shutdown
ExecReload=/usr/local/bin/supervisorctl $OPTIONS reload
KillMode=process
Restart=on-failure
RestartSec=15s

[Install]
WantedBy=multi-user.target
EOF

cat > /home/ec2-user/todo.py<< EOF
from flask import Flask, request
from flask_restful import Resource, Api, abort
import boto3
import uuid

app = Flask(__name__)
api = Api(app)

client = boto3.client('dynamodb')

PARTITION_KEY = 'id'
TABLE_NAME = 'TodoTable'


def _serialize_item(item):
    if not item:
        return None

    return {PARTITION_KEY: item[PARTITION_KEY]['S'], 'data': item['data']['S']}


def put_item(key, data):
    client.put_item(
        TableName=TABLE_NAME,
        Item={
            PARTITION_KEY: {
                'S': str(key)
            },
            'data': {
                'S': str(data)
            }
        },
    )

    return {PARTITION_KEY: str(key), 'data': data}

def get_item(key):
    row = client.get_item(TableName=TABLE_NAME, Key={PARTITION_KEY: {'S': str(key)}})
    item = row.get('Item')
    return _serialize_item(item)


def get_items():
    items = client.scan(TableName=TABLE_NAME).get('Items', [])
    return [_serialize_item(item) for item in items]


class TodoItem(Resource):

    def get(self, todo_id):
        item = get_item(todo_id)
        if item:
            return item

        abort(404, message=f"Todo {todo_id} doesn't exist")


class TodoList(Resource):

    def get(self):
        return get_items()

    def post(self):
        todo_id = str(uuid.uuid4())[:8]
        data = request.form['data']
        return put_item(todo_id, data)


api.add_resource(TodoItem, '/todo/<string:todo_id>')
api.add_resource(TodoList, '/todo')

if __name__ == '__main__':
    HOST = '0.0.0.0'
    app.run(host=HOST, port=8080)
EOF

# start supervisor, and set it to start on boot
systemctl start supervisord.service
systemctl enable supervisord.service