from itertools import starmap
import re
from uuid import UUID

from giveaway import database
from giveaway import model


def starfilter(pred, it):
    for i in it:
        if pred(*i):
            yield i


_youtube = re.compile("^https:\/\/www.youtube.com\/(channel|user)\/[a-zA-Z0-9~._-]+\/?$")
_discord = re.compile("^.+#[0-9]{4}$")


def looks_like_youtube_url(values):
    """This does not look like a youtube channel or user URL. Please compare the value you are entering with the appearance of the example value.
    """
    return all(_youtube.match(value) for value in values)

def looks_like_discord_user(values):
    """This does not look like a complete discord username. Please compare the value you are entering with the appearance of the example value.
    """
    return all(_discord.match(value) for value in values)


def bytes_from_uuid(value):
    try:
        return UUID(value).bytes
    except ValueError:
        return b""


def exists_in_database(query, key, cursor, value_translator=bytes_from_uuid):
    def p(v):
        return v
    def validator(values):
        """selected value is either not available or does not exist
        """
        return all(
            p(next(cursor.execute(query, {key: value_translator(value)}), None)) is not None
            for value in values
        )
    return validator


def validator_factory(required, multiple, value):
    def validator(values):
        if required and not values:
            return "required field" if not multiple else "you must select at least one"
        elif not multiple and len(values) > 1:
            return "too many values submitted for field"
        elif not value(values):
            assert value.__doc__ is not None
            return value.__doc__.strip()
        else:
            return None
    return validator


def validate(qsl):
    cursor = database.connection.cursor()
    schema = {
        'giveaway:id': validator_factory(
            required=True,
            multiple=False,
            value=exists_in_database(
                query=model.get_current_giveaway_by_id,
                key="giveaway_id",
                cursor=cursor,
            ),
        ),
        'giveaway-prize:id': validator_factory(
            required=True,
            multiple=True,
            value=exists_in_database(
                query=model.get_current_giveaway_prizes_by_id,
                key="giveaway_prize_id",
                cursor=cursor,
            ),
        ),
        'youtube:url': validator_factory(
            required=True,
            multiple=False,
            value=looks_like_youtube_url,
        ),
        'discord:username': validator_factory(
            required=True,
            multiple=False,
            value=looks_like_discord_user,
        )
    }

    def evaluate_rule(name, validator):
        kvl = list(starfilter(lambda k, _v: k == name, qsl))
        if not kvl:
            values = tuple()
        else:
            _, values = zip(*kvl)
        return name, values, validator(values)

    return starmap(evaluate_rule, schema.items())
