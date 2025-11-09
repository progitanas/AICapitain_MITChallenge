import logging
import json
try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    # Fallback simple JSON formatter if python-json-logger is not installed
    class jsonlogger:
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                record_dict = {
                    "name": record.name,
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "pathname": record.pathname,
                    "lineno": record.lineno,
                    "exc_info": None
                }
                if record.exc_info:
                    record_dict["exc_info"] = self.formatException(record.exc_info)
                return json.dumps(record_dict)

def setup_logging(log_level: str = "INFO"):
    """Configure le logging au format JSON"""
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Handler console
    console_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
