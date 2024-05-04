import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_environment():
    try:
        os.environ.pop("OPENAI_API_KEY")
        os.environ.pop("TG_BOT_TOKEN")
    except:
        logger.info("env is already clear")
    load_dotenv()