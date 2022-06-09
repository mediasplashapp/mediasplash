class Subtitle:
    def __init__(self, *args, **kwargs):
        self.title = kwargs.get("title", "")
        self.language = kwargs.get("language", "")
        self.path = kwargs.get("path", "")
        self.external = kwargs.get("external", False)
        self.default = kwargs.get("default", 0)

    def stringify(self):
        text = []
        if self.title:
            text.append(f"Title: {self.title}")
        if self.language:
            text.append(f"Language: {self.language}")
        text.append(f"External: {('Yes' if self.external else 'No')}")
        text.append(f"Default: {('Yes' if self.default else 'No')}")
        if self.path:
            text.append(f"Location: {self.path}")
        return text
