class CheckRegistry:
    _instance = None
    _checks: dict[str, callable] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, name: str, check_func: callable):
        self._checks[name] = check_func

    def get(self, name: str) -> callable | None:
        return self._checks.get(name)

    def list_checks(self) -> list[str]:
        return list(self._checks.keys())

    def has(self, name: str) -> bool:
        return name in self._checks


registry = CheckRegistry()
