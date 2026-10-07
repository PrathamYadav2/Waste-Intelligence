import json, logging, sys, uuid
class JsonFormatter(logging.Formatter):
    def format(self, r):
        return json.dumps({"ts": self.formatTime(r), "level": r.levelname, "logger": r.name, "msg": r.getMessage(), **getattr(r, "extra_fields", {})})
def setup_logging(level: str = "INFO"):
    h = logging.StreamHandler(sys.stdout); h.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[h], force=True)
def new_request_id() -> str: return uuid.uuid4().hex
