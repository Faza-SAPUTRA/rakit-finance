from app.parsers import BcaParser, GopayParser


class ImportService:
    """Selects a parser, then calls parse() polymorphically."""

    parsers = {
        "bca": BcaParser,
        "gopay": GopayParser,
    }

    @classmethod
    def parser_for(cls, source: str):
        parser_class = cls.parsers.get((source or "").lower())
        if not parser_class:
            raise ValueError(f"Unsupported import source: {source}")
        return parser_class()

    @classmethod
    def parse(cls, source: str, file_storage, user_id: int):
        parser = cls.parser_for(source)
        return parser.parse(file_storage, user_id=user_id)

