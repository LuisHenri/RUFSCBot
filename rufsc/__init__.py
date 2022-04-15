import os

from boto.s3.connection import S3Connection

try:
    s3 = S3Connection(os.environ["RUFSC_BOT_TOKEN"], os.environ["CHANNEL_ID"])
except KeyError:
    pass
