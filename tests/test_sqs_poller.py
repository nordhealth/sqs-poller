import pytest


class TestCreateQueue:
    def test_new_queue(self, sqs, poller):
        queue_name = 'test-queue'
        created_queue = poller.create_queue(queue_name)
        retrieved_queue = sqs.get_queue_by_name(QueueName=queue_name)
        assert created_queue.url == retrieved_queue.url

    def test_existing_queue(self, sqs, poller):
        queue_name = 'test-queue'
        created_queue = sqs.create_queue(QueueName=queue_name)
        recreated_queue = poller.create_queue(queue_name)
        assert created_queue.url == recreated_queue.url


class TestGetQueueByName:
    def test_get_queue_by_name_success(self, sqs, poller):
        queue_name = 'test-queue'
        created_queue = sqs.create_queue(QueueName=queue_name)
        retrieved_queue = poller.get_queue_by_name(queue_name)
        assert retrieved_queue.url == created_queue.url

    def test_get_queue_by_name_fail(self, poller):
        with pytest.raises(poller.sqs.meta.client.exceptions.QueueDoesNotExist):
            poller.get_queue_by_name('test-queue')


class TestDoesQueueExist:
    def test_existing_queue(self, sqs, poller):
        queue_name = 'test-queue'
        sqs.create_queue(QueueName=queue_name)
        assert poller.does_queue_exist(queue_name)

    def test_non_existing_queue(self, poller):
        assert not poller.does_queue_exist('test-queue')


class TestSendMessageToQueue:
    def test_success(self, poller, queue_without_messages):
        queue, queue_name = queue_without_messages
        response = poller.send_message_to_queue(queue_name, 'message')
        message_id = response.get('MessageId')

        retrieved_message = poller.receive_message_from_queue(queue_name)
        assert retrieved_message.message_id == message_id
        assert retrieved_message.queue_url == queue.url

    def test_non_existing_queue(self, poller):
        queue_name = 'test-queue'
        with pytest.raises(poller.sqs.meta.client.exceptions.QueueDoesNotExist):
            poller.send_message_to_queue(queue_name, 'message')


class TestReceiveMessagesFromQueue:
    def test_without_messages(self, poller, queue_without_messages):
        queue, queue_name = queue_without_messages
        messages = poller.receive_messages_from_queue(queue_name)
        assert not messages
        message = poller.receive_message_from_queue(queue_name)
        assert message is None

    def test_one_message(self, poller, queue_without_messages):
        queue, queue_name = queue_without_messages
        response = poller.send_message_to_queue(queue_name, 'message')
        message_id = response.get('MessageId')

        message = poller.receive_message_from_queue(queue_name, VisibilityTimeout=0)
        assert message.message_id == message_id
        messages = poller.receive_messages_from_queue(queue_name)
        assert messages[0].message_id == message_id

    def test_multiple_messages(self, poller, queue_with_messages):
        queue, queue_name, message_ids = queue_with_messages
        messages = poller.receive_messages_from_queue(queue_name, max_count=10)
        for message in messages:
            assert message.message_id in message_ids
        message = poller.receive_message_from_queue(queue_name)
        assert message.message_id in message_ids


class TestPurgeQueue:
    def test_empty_queue(self, poller, queue_without_messages):
        queue, queue_name = queue_without_messages
        poller.purge_queue(queue_name)
        messages = poller.receive_messages_from_queue(queue_name)
        assert not messages

    def test_queue_with_messages(self, poller, queue_with_messages):
        queue, queue_name, message_ids = queue_with_messages
        poller.purge_queue(queue_name)
        messages = poller.receive_messages_from_queue(queue_name)
        assert not messages

