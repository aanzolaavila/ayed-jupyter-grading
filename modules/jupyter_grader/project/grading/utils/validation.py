class ValidationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def validate_student(name: str, code: int):
    assert isinstance(name, str), f"nombre de estudiante no es valido"
    assert isinstance(code, int), f"codigo de estudiante no es valido"

    if len(name) == 0:
        raise ValidationException("nombre de estudiante no debe ser vacio")
    if code == 0:
        raise ValidationException("codigo de estudiante debe ser un numero de carnet")
