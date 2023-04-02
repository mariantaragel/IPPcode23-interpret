class Variable:

    name: str
    value: any
    type: str

    def __init__(self, name, value, type) -> None:
        self.name = name
        self.value = value
        self.type = type