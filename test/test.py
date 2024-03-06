import json
import pika

# RabbitMQ 서버 연결 설정
connection = pika.BlockingConnection(pika.ConnectionParameters('cloudwiz-mq'))
channel = connection.channel()

# 메시지를 보낼 큐의 이름
queue_name = 'TEST.REQ'

# 큐가 존재하지 않는 경우 생성합니다.
channel.queue_declare(queue=queue_name, durable=True)

# 헤더와 페이로드에 추가할 변수
message_header = {
    'message_id': '12345',
    'timestamp': '2024-03-01T09:00:00Z',
    'source_system': 'cloudwizwas01'
}

message_body = {
    'playbook_path': '/app/playbook/get_hostname.yaml',
    'inventory': ["localhost"],
    'host_vars': {
        "localhost": {"var1": "value1", "var2": "value2"},
    },
    'extra_vars': {"var1": "value1", "var2": "value2"},
    'limit': "host_group",
    'tags': ["tag1", "tag2"],
    'verbosity': 4,
    'credentials': {
        "ssh_key": "/path/to/your/private_key.pem",
        "username": "your_username"
    }
}

# JSON 형식으로 변환할 메시지
json_message_header = json.dumps(message_header)
json_message_body = json.dumps(message_body)

# 메시지를 퍼블리시합니다. JSON 형식의 메시지는 바이트 형태로 인코딩해야 합니다.
channel.basic_publish(exchange='',
                      routing_key=queue_name,
                      body=json_message_body.encode(),  # JSON 형식의 메시지를 바이트 형태로 인코딩합니다.
                      properties=pika.BasicProperties(
                          headers=json.loads(json_message_header),  # 헤더를 딕셔너리 형태로 전달합니다.
                          delivery_mode=2,  # 메시지를 영속적으로 설정 (durable)
                      )   
)

print(" [x] Sent JSON Message:", json_message_header)
print(" [x] Sent JSON Message:", json_message_body)

# 연결을 닫습니다.
connection.close()
