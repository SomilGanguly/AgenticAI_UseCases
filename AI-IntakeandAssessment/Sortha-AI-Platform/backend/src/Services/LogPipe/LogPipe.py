class LogLevel:
    DEBUG = 0b00001
    INFO = 0b00010
    WARNING = 0b00100
    ERROR = 0b01000
    CRITICAL = 0b10000
    ALL = DEBUG | INFO | WARNING | ERROR | CRITICAL

    def __str__(self):
        return self.name

class LogPipe:
    _instance = None

    def __init__(self):
        if LogPipe._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            LogPipe._instance = self
            self.logLevel = LogLevel.ALL

    @staticmethod
    def get_instance():
        if LogPipe._instance is None:
            LogPipe()
        return LogPipe._instance
    
    def set_log_level(self, level: LogLevel):
        self.logLevel = level

    def get_log_level(self) -> LogLevel:
        return self.logLevel
    
    def log_debug(self, *args):
        if (self.logLevel & LogLevel.DEBUG):
            print(f"[DEBUG] {' '.join(map(str, args))}")

    def log_info(self, *args):
        if (self.logLevel & LogLevel.INFO):
            print(f"[INFO] {' '.join(map(str, args))}")

    def log_warn(self, *args):
        if (self.logLevel & LogLevel.WARNING):
            print(f"[WARN] {' '.join(map(str, args))}")

    def log_error(self, *args):
        if (self.logLevel & LogLevel.ERROR):
            print(f"[ERROR] {' '.join(map(str, args))}")

    def log_critical(self, *args):
        if (self.logLevel & LogLevel.CRITICAL):
            # In a real application, you might want to log to stderr or a file
            # Here we just print to stdout for simplicity
            print(f"[CRITICAL] {' '.join(map(str, args))}")

    def debug(*args):
        LogPipe.get_instance().log_debug(*args)
    
    def info(*args):
        LogPipe.get_instance().log_info(*args)
    
    def warn(*args):
        LogPipe.get_instance().log_warn(*args)
    
    def error(*args):
        LogPipe.get_instance().log_error(*args)
    
    def critical(*args):
        LogPipe.get_instance().log_critical(*args)