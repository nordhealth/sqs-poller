import os

import boto3
from moto import mock_sqs
import pytest

from src.sqs_poller import SQSPoller


@pytest.fixture(autouse=True)
def permanent_mock_sqs():
    """Make sure that we don't make requests to real AWS by accident"""
    with mock_sqs():
        yield


@pytest.fixture(autouse=True)
def aws_credentials():
    """Set AWS credentials for testing"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['SQS_POLLER_AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['SQS_POLLER_AWS_SECRET_ACCESS_KEY'] = 'testing'


@pytest.fixture()
def sqs(aws_credentials):
    """Return an SQS resource from boto3"""
    yield boto3.resource('sqs')


@pytest.fixture()
def poller(aws_credentials):
    """Return an SQSPoller instance"""
    yield SQSPoller()


@pytest.fixture
def queue_without_messages(poller):
    """Return an empty SQS queue"""
    queue_name = 'test-queue'
    queue = poller.create_queue(queue_name)
    yield queue, queue_name


@pytest.fixture
def queue_with_one_message(poller):
    """Return an SQS queue which contains a single message"""
    queue_name = 'test-queue'
    queue = poller.create_queue(queue_name)
    message = poller.send_message_to_queue(queue_name, 'message')
    message_id = message.get('MessageId')
    yield queue, queue_name, message_id


@pytest.fixture
def queue_with_messages(poller):
    """Return an SQS queue which contains messages"""
    queue_name = 'test-queue'
    queue = poller.create_queue(queue_name)
    messages = [
        poller.send_message_to_queue(queue_name, 'message-' + str(i))
        for i in range(15)
    ]
    message_ids = [message.get('MessageId') for message in messages]
    yield queue, queue_name, message_ids
