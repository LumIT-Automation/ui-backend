class CustomException(Exception):
    def __init__(self, status: int, payload: dict):
        self.status = int(status)
        self.payload = payload



    def status(self) -> int:
        return self.status



    def __str__(self) -> str:
        if "UI-BACKEND" in self.payload:
            r = str(self.payload["UI-BACKEND"])
        else:
            r = str(self.payload)

        return r
