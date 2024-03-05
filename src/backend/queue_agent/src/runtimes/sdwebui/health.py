import logging
import time

logger = logging.getLogger("queue-agent")

def check_readiness(url, dynamic_sd_model):
    while True:
        try:
            logger.info('Checking service readiness...')
            # checking with options "sd_model_checkpoint" also for caching current model
            opts = invoke_get_options()
            logger.info('Service is ready.')
            global current_model_name
            if "sd_model_checkpoint" in opts:
                if opts['sd_model_checkpoint'] != None:
                    current_model_name = opts['sd_model_checkpoint']
                    logger.info(f'Init model is: {current_model_name}.')
                else:
                    current_model_name = ''
                    if dynamic_sd_model:
                        logger.info(f'Dynamic SD model is enabled, init model is not loaded.')
                    else:
                        logger.error(f'Init model {current_model_name} failed to load.')
            break
        except Exception as e:
            logger.debug(repr(e))
            time.sleep(1)