# sqs-poller
A wrapper class around boto3's SQS resource.

Please see the official documentation for more detailed information:

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html

# Installation
```shell
pip install sqs-poller
```

# Usage
## Creating a poller object
### Give the AWS credentials as arguments
**Note that the credentials should not be stored directly in the source code.**
Please use some other method for storing them, for example environmental
variables, as described in the next section.
```python
from sqs_poller import SQSPoller

poller = SQSPoller(
    aws_access_key_id='<YOUR-AWS-ACCESS-KEY-ID>',
    aws_secret_access_key='<YOUR-AWS-SECRET-ACCESS-KEY>',
    region_name='<AWS-REGION-NAME>',
)
```

Or if you want to store the credentials in a dict:
```python
aws_credentials = {
    'aws_access_key_id': '<YOUR-AWS-ACCESS-KEY-ID>',
    'aws_secret_access_key': '<YOUR-AWS-SECRET-ACCESS-KEY>',
    'region_name': '<AWS-REGION-NAME>',
}
poller = SQSPoller(**aws_credentials)
```
Note that the arguments given to `SQSPoller` are passed to the underlying boto3
Session. The list of available parameters can be found here:
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html

### Get the AWS credentials from environmental variables
The credentials can also be stored in environmental variables. The following
variables can be used:
- `SQS_POLLER_AWS_ACCESS_KEY_ID`
- `SQS_POLLER_AWS_SECRET_ACCESS_KEY`
- `SQS_POLLER_REGION_NAME`

If all the necessary credentials are given in environmental variables, it's not
necessary to give any arguments to `SQSPoller`:
```python
from sqs_poller import SQSPoller

poller = SQSPoller()
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

# Development
## Set up a virtual environment
Note that while this example uses virtualenvwrapper, other virtualenv tools
should also work.

### Install virtualenvwrapper
https://virtualenvwrapper.readthedocs.io/en/latest/install.html#basic-installation

Remember to run `. .bashrc`, or to restart your terminal before moving to the
next step. Otherwise, `mkvirtualenv` command might not be available.

### Create a virtual environment
```shell
mkvirtualenv sqs-poller
```

## Clone the repository
```shell
git clone https://github.com/nordhealth/sqs-poller.git
cd sqs-poller
```

## Install dependencies
```shell
python -m pip install --upgrade pip
pip install -e .[tests]
```

## Run the tests
```shell
pytest
```

## Publish a new release to PyPI
**Make sure that the tests are passing before creating a release.**
See [this commit](https://github.com/nordhealth/sqs-poller/commit/0f63d94f5c1b46b75329e0763ac96b279f0419b6)
for more information.

```shell
git checkout main
git tag <VERSION-NUMBER>
git push origin <VERSION-NUMBER>
```
 This will create a new git tag for the release, and start the GitHub workflow
 which will create a new release to PyPI with the given version number.
 