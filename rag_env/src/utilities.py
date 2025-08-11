import time
import functools
from .logger_config import logger

class Decorators:
    @staticmethod
    def time_it(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = int((time.time() - start_time) * 1000)  # ms
            logger.info(f"Function {func.__name__} executed in {elapsed_time} ms")

            if isinstance(result, dict):
                result["processingTimeMs"] = elapsed_time
            elif hasattr(result, "dict"):
                data = result.dict()
                data["processingTimeMs"] = elapsed_time
                return type(result)(**data)

            return result
        return wrapper



class Strings:
    max_content_length=500
    chunk_size=250
    chunk_overlap=50

