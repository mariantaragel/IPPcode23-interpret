class Mybool():

    value: bool

    def __init__(self, value) -> None:
        if value == 'true':
            self.value = True
        else:
            self.value = False

    def __repr__(self) -> str:
        if self.value:
            return 'true'
        else:
            return 'false'

    def __str__(self) -> str:
        if self.value:
            return 'true'
        else:
            return 'false'