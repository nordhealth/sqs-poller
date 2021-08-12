import os

import boto3


class SQSPoller:
    """A wrapper class around boto3's SQS resource.

    Please see the official documentation for more detailed information:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html"""
    # TODO: how long does an AWS session last? Should it be refreshed?
    def __init__(self, **session_kwargs):
        session_kwargs.setdefault(
            'aws_access_key_id',
            os.environ.get('POLLER_AWS_ACCESS_KEY_ID'),
        )
        session_kwargs.setdefault(
            'aws_secret_access_key',
            os.environ.get('POLLER_AWS_SECRET_ACCESS_KEY'),
        )
        self.session = boto3.Session(**session_kwargs)
        self.sqs = self.session.resource('sqs')
        self.queue_cache = {}

    def get_queue_by_name(self, queue_name, skip_cache=False):
        """Return a queue named `queue_name`.

        :param str queue_name: Name of the queue.
        :param boolean skip_cache: Whether to skip the queue cache.
        :raise QueueDoesNotExist: When the queue is not found, this exception is raised.
        :return: A `Queue` object.
        """
        if skip_cache:
            queue = self.sqs.get_queue_by_name(QueueName=queue_name)
            self.queue_cache[queue_name] = queue
            return queue
        return self.queue_cache.setdefault(
            queue_name,
            self.sqs.get_queue_by_name(QueueName=queue_name),
        )

    def does_queue_exist(self, queue_name):
        """Return `True` if a queue named `queue_name` exists.

        :param str queue_name: Name of the queue.
        :return: Whether a queue named `queue_name` exists.
        :rtype: boolean
        """
        try:
            self.get_queue_by_name(queue_name, skip_cache=True)
        except self.sqs.meta.client.exceptions.QueueDoesNotExist:
            return False
        return True

    def create_queue(self, queue_name, attributes=None, tags=None):
        """Create a queue named `queue_name` using the given `attributes` and `tags`.

        :param str queue_name: Name of the queue.
        :param dict attributes: Attributes that will be set for the queue.
        :param dict tags: Queue cost allocation tags that will be set for the queue.
        :return: A Queue object. If a queue with the given name already exists,
         the existing queue will be returned.
        :rtype: Queue
        """
        if attributes is None:
            attributes = {}
        if tags is None:
            tags = {}
        queue = self.sqs.create_queue(
            QueueName=queue_name,
            Attributes=attributes,
            tags=tags,
        )
        self.queue_cache[queue_name] = queue
        return queue

    def purge_queue(self, queue_name):
        """Delete all messages from a queue named `queue_name`.

        :param str queue_name: Name of the queue.
        :raise QueueDoesNotExist: When the queue is not found, this exception is raised.
        :rtype: None
        """
        queue = self.get_queue_by_name(queue_name)
        return queue.purge()

    def get_messages_from_queue(self, queue_name, max_count=1, **receive_kwargs):
        """Return maximum of `max_count` messages from a queue named `queue_name`.

        :param str queue_name: Name of the queue.
        :param int max_count: Maximum number of messages to receive.
        :param receive_kwargs: Arguments that will be passed to the underlying
         `receive_messages` call.
        :raise QueueDoesNotExist: When the queue is not found, this exception is raised.
        :return: List of `Message` objects.
        :rtype: list[Message`]
        """
        queue = self.get_queue_by_name(queue_name)
        receive_kwargs['MaxNumberOfMessages'] = max_count
        return queue.receive_messages(**receive_kwargs)

    def get_message_from_queue(self, queue_name, **receive_kwargs):
        """Return a single message from a queue named `queue_name`.

        `receive_kwargs` are passed to the underlying receive_messages call.

        :param str queue_name: Name of the queue.
        :param receive_kwargs: Arguments that will be passed to the underlying
         `receive_messages` call.
        :raise QueueDoesNotExist: When the queue is not found, this exception is raised.
        :return: `Message` object or None, when no message was received.
        :rtype: Message, None
        """
        messages = self.get_messages_from_queue(queue_name, **receive_kwargs)
        try:
            return messages[0]
        except IndexError:
            return None

    def delete_messages_from_queue(self, queue_name, entries):
        """Delete maximum of 10 messages from a queue named `queue_name`.

        Messages from SQS are deleted using receipt handles. `entries`
        is a list of all messages that should be deleted. Every item
        in `entries` should be a dictionary with 2 keys: 'Id' and
        'ReceiptHandle'.

        [
            {
                'Id': '<a unique ID (string)>',

                'ReceiptHandle': '<a receipt handle (string)>',
            },
        ]

        If multiple messages are deleted simultaneously, every message's
        `Id` should be unique. The `Id` will be used to identify the
        messages on the response.

        :param str queue_name: Name of the queue.
        :param entries: List of entries as described above.
        :raise QueueDoesNotExist: When the queue is not found, this exception is raised.
        :return: The API response.
        :rtype: dict
        """
        queue = self.get_queue_by_name(queue_name)
        return queue.delete_messages(Entries=entries)

    def send_message_to_queue(self, queue_name, message_body, **send_kwargs):
        """Send a message `message_body` to a queue named `queue_name`.

        :param str queue_name: Name of the queue.
        :param str message_body: The body of the message that will be sent.
        :param send_kwargs: Arguments that will be passed to the underlying
         `send_message` call.
        :raise QueueDoesNotExist: When the queue is not found, this exception is raised.
        :return: The API response.
        :rtype: dict
        """
        queue = self.get_queue_by_name(queue_name)
        send_kwargs['MessageBody'] = message_body
        return queue.send_message(**send_kwargs)

