class IndexableTool:
    def __init__(self):
        pass

    def get_last_occurrence(self, obj: list | str, occurrence):
        try:
            return obj.rindex(occurrence)
        except ValueError:
            return None
