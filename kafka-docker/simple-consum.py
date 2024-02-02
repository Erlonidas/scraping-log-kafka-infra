from confluent_kafka import Consumer

c = Consumer({
    #'bootstrap.servers': 'localhost:29092',
    'bootstrap.servers': 'localhost:19092',
    'group.id': 'G1',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['onlyTopicDone'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))

c.close()