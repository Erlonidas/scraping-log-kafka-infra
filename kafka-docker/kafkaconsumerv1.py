from confluent_kafka import Consumer

conf = {'bootstrap.servers': 'localhost:29092',
        'group.id': 'foo',
        'enable.auto.commit': 'false',
        'auto.offset.reset': 'earliest'}

consumer = Consumer(conf)
topics = ["topicHello_world"]
running = True

def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                msg_process(msg)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False
    
if __name__ == '__main__':
    basic_consume_loop(consumer, topics)