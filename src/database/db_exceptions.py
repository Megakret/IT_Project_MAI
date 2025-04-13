class UniqueConstraintError(Exception):
    def __init__(self, column_names: list[str], values: list[str]):
        self.message = f'UniqueConstraint violation in the columns: "{'" "'.join(column_names)}". Invalid values: {' '.join(values)}.'
        super().__init__(self.message)


class ConstraintError(Exception):
    def __init__(self, column_names: list[str], values: list[str]):
        self.message = f'Unknown Constraint violation in the columns: "{'" "'.join(column_names)}". Invalid values: {' '.join(values)}.'
        super().__init__(self.message)

