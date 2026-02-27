"""
SQS message format and queue operations for the geometry API.

Title
-----
Messages Package (SQS)

Context
-------
This package defines the SQS message format and queue client for the
geometry API. Message carries action (START/REPORT), job_id, user_email,
and optional receipt_handle. Queue uses QUEUE_NAME env, provides put(),
receive(), delete(), and commit(message). Workers receive messages,
parse with Message.unserialize, run the task, and commit to remove from
queue. Used by JobMutation (put START), StartTask (put REPORT), ReportTask
(put REPORT for parent), and workers.handler (receive, commit).

Examples:
>>> queue.put(Message(action=Action.START, job_id=id, user_email=email))
>>> for raw in queue.receive(max_messages=5):
>>> msg = Message.unserialize({**json.loads(raw["body"]), "receipt_handle": raw["receiptHandle"]})
>>> ...
>>> queue.commit(msg)
"""

from .message import Message
from .queue import Queue

__all__ = [
    "Message",
    "Queue",
]
