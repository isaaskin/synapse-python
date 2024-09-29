class AdapterPublishError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TopicAlreadySubscribedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ConnectionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
