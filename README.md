# sqs-poller
A wrapper class around boto3's SQS resource.

Please see the official documentation for more detailed information:

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html

# Usage
## Creating a poller object

```python
from sqs_poller import SQSPoller

poller = SQSPoller(
    aws_access_key_id='<YOUR-AWS-ACCESS-KEY-ID>',
    aws_secret_access_key='<YOUR-AWS-SECRET-ACCESS-KEY>',
)

# Alternatively
aws_credentials = {
    'aws_access_key_id': '<YOUR-AWS-ACCESS-KEY-ID>',
    'aws_secret_access_key': '<YOUR-AWS-SECRET-ACCESS-KEY>',
}
poller = SQSPoller(**aws_credentials)
```

## Getting a queue
### Create a new queue
```python
queue = poller.create_queue('new-queue-name')
print(queue.url)  # Prints the queue's url
```

### Create a new queue with specific attributes and cost allocation tags
```python
attributes = {
    # The messages will be stored for 1 week (4 days by default)
    'MessageRetentionPeriod': 60 * 60 * 24 * 7,  # 1 week
    # Wait new messages for up to 20 seconds (0 by default)
    # This is also known as long polling. More info about long polling can be found here:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-long-polling.html
    'ReceiveMessageWaitTimeSeconds': 20,
}
# A list of all available attributes:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.ServiceResource.create_queue
tags = {
    'some-key': 'some-value',
    'other-key': 'other-value',
}
# More information about cost allocation:
# https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-tags.html
queue = poller.create_queue(
    'new-queue-name',
    attributes=attributes,
    tags=tags,
)
```

### Get an existing queue
```python
queue = poller.get_queue_by_name('an-existing-queue')
```

### Checking if a queue exists
```python
poller.does_queue_exist('an-existing-queue')  # returns True
poller.does_queue_exist('non-existing-queue')  # returns False
```

### About queue names
Note that every queue must have a unique name in your AWS account and region.
When creating a queue with an existing name, the existing queue is returned and
no new queue is created. This means that it's not necessary to check if a queue
name is available before creating it. The following methods are equivalent:
```python
# Longer way
queue_name = 'an-existing-queue'
if not poller.does_queue_exist(queue_name):
    queue = poller.create_queue(queue_name)
else:
    queue = poller.get_queue_by_name(queue_name)
```
```python
# Shorter way
queue_name = 'an-existing-queue'
queue = poller.create_queue(queue_name)
```

## Sending a message
```python
message = 'Hello, world!'
poller.send_message_to_queue('queue-name', message)
```

## Receiving messages
### Receive a single message
```python
message = poller.receive_message_from_queue('queue-name')
print(message.body)  # Prints the message's content
```

### Receive multiple messages
```python
messages = poller.receive_messages_from_queue('queue-name')
print(len(messages))  # Prints the message count
print(messages[0].body)  # Prints the first message's content
```

## Deleting messages
### Delete a single message
```python
message = poller.receive_message_from_queue('queue-name')
message.delete()
```

### Delete all messages from a queue
```python
poller.purge_queue('queue-name')
messages = poller.receive_messages_from_queue('queue-name')
print(len(messages))  # Prints "0"
```
