from confluent_kafka import Producer, Consumer, KafkaException
import sys
import json
import logging
from pprint import pformat
import time


class Producer_kaf:
    
    def run(self, broker: str, topic: str):

        self.broker = broker
        self.topic = topic

        # Producer configuration
        
        conf = {'bootstrap.servers': self.broker}

        # Create Producer instance
        p = Producer(**conf)

        # Optional per-message delivery callback (triggered by poll() or flush())
        # when a message has been successfully delivered or permanently
        # failed delivery (after retries).
        def delivery_callback(err, msg):
            if err:
                sys.stderr.write('%% Message failed delivery: %s\n' % err)
            else:
                sys.stderr.write('%% Message delivered to %s [%d] @ %d\n' %
                                 (msg.topic(), msg.partition(), msg.offset()))

        # Read lines from stdin, produce each line to Kafka
        link_to_log = "../../log-string.txt"

        with open(link_to_log, 'r') as fhandle:
            content_log = fhandle.read()
        try:
            p.produce(self.topic, content_log, callback=delivery_callback)

        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                                len(p))

        p.poll(0)

        # Wait until all messages have been delivered
        sys.stderr.write('%% Waiting for %d deliveries\n' % len(p))
        p.flush()
        

        
class Consumer_kaf:
    """
    Class to consume events send by producer.
    All logs will be consumed since when Kafka started running.
    """
    
    def segregation_log(self, content_log: list) -> list:
        endGame_sight = '-----'
        endGame = False
        start_position = 0
        splitted_game = []

        for slot, line in enumerate(content_log):
            if (endGame_sight in line) and (endGame == False):
                splitted_game.append(content_log[start_position:slot])
                start_position = slot + 1
                endGame = True
            elif (endGame_sight in line) and (endGame == True):
                endGame = False
                continue
        return splitted_game

        
    def run(self, broker: str, topic: str, group = 'group_1'):

        self.broker = broker
        self.group = group
        self.topics = [topic]
        self.splitted = {}
        
        # Consumer configuration
        conf = {'bootstrap.servers': self.broker, 'group.id': self.group, 'session.timeout.ms': 6000,
                'auto.offset.reset': 'latest', 'enable.auto.offset.store': False}

        # Create logger for consumer (logs will be emitted when poll() is called)
        logger = logging.getLogger('consumer')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)

        # Create Consumer instance
        # Hint: try debug='fetch' to generate some log messages
        c = Consumer(conf, logger = logger)

        def print_assignment(consumer, partitions):
            print('Assignment:', partitions)

        # Subscribe to topics
        c.subscribe(self.topics, on_assign=print_assignment)

        # Read messages from Kafka, print to stdout
        try:
            while True:
                msg = c.poll(timeout = 1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                else:
                    string = msg.value().decode('utf-8')
                    
                    # splitted isinstace(dict) of game's catalog from Log string
                    self.splitted[msg.offset()] = self.segregation_log(string.split('\n'))
                    # Proper message
                    sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                     (msg.topic(), msg.partition(), msg.offset(),
                                      str(msg.key())))
                    print(f"Message Log successfully received.")
                    c.store_offsets(msg)
                    print('waiting timeout...')
                    time.sleep(1)    
                    break
            c.close()

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')

        finally:
            c.close()
        
        
    def get_event(self) -> dict:
        return self.splitted