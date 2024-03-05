import logging
import os
import sys
from aws_xray_sdk.core import patch_all

patch_all()

logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

logger = logging.getLogger("queue-agent")
logger.propagate = False
logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)