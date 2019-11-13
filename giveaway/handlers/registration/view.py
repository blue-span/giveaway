from lxml.builder import E
from lxml import html


def html_boilerplate(head, body):
    document = (
        E.html(
            {'lang': 'en'},
            E.head(
                E.meta(
                    {'charset': 'utf-8'}
                ),
                *head,
            ),
            E.body(
                *body,
            ),
        )
    )
    return document


def text_field(field_id, label, **kwargs):
    return (
        E.label(
            {'for': field_id},
            *label,
        ),
        E.input(
            {'id': field_id, 'type': 'text', 'name': field_id, **kwargs},
        ),
    )


document = html_boilerplate(
    head=(
        E.title("bluespan.gg giveaway registration"),
        E.link(
            dict(
                rel="stylesheet",
                href="/static/css/bluespan-normalize.css"
            ),
        )
    ),
    body=(
        E.span(
            E.h1({'class': 'title'}, "bluespan.gg"),
            E.h1(
                "Giveaway Registration: ",
                E.span({"class": "literal"}, "Nov\u00A024"),
            ),
        ),
        E.div(
            {'class': 'admonition note'},
            E.p(
                {'class': 'admonition-title'},
                "Note"
            ),
            E.p(
                """Please enter all required fields carefully and accurately; while this
registration form attempts to perform some basic validation checks, entering
inaccurate information could result in your registration becoming silently discarded."""
            ),
        ),
        E.form(
            dict(
                action="/register",
                method="post",
            ),
            E.fieldset(
                E.legend("How can we identify you?"),
                *text_field("youtube:channel-display-name", (
                    "Youtube Channel URL ",
                    E.small(E.code("(required)")),
                ), placeholder="https://www.youtube.com/channel/UCpOkbe8JBvSHIEQn5D0V3tQ"),
                E.small(
                    """The channel URL you enter here should be the same channel/user you regularly
use in live stream chat during Blue Span's streams. This will be used to
determine """,
                    E.a({'class': 'reference', 'href': 'https://bluespan.gg/giveaway/#who-is-eligible', 'target': '_blank'}, "basic eligibility"),
                    """ for the giveaway.""",
                ),
                *text_field("discord:channel-display-name", (
                    "Discord Username ",
                    E.small(E.code("(required)")),
                ), placeholder="Lulu-chan#4513"),
                E.small(
                    "You should already be a member of the ",
                    E.a({'class': 'reference', 'href': 'https://discord.gg/2nhPhsN', 'target': '_blank'}, "Blue Span"),
                    " discord server. You will need to use Discord via this user to ",
                    E.a({'class': 'reference', 'href': 'https://bluespan.gg/giveaway/#i-am-a-winner-how-do-i-claim-my-prize', 'target': '_blank'}, "claim your prize"),
                    "  if you are selected.",
                ),
            ),
            E.fieldset(
                E.legend("Which giveaway prizes are you interested in winning?"),
                E.small(
                    """Each prize is selected independently; selecting multiple prizes does not
increase or decrease your chances of winning."""
                ),
                E.div(
                    {'class': 'table-cell'},
                    E.input(
                        {'type': 'checkbox', 'class': 'indicated', 'id': 'prize:gaming-computer', 'name': 'prize:gaming-computer'},
                    ),
                    E.label(
                        {'for': 'prize:gaming-computer', 'class': 'checkbox-indicator amd-red'},
                        E.img({'src': '/static/images/amd-ryzen-radeon.png', 'class': 'checkbox-invert'}),
                        E.h2("Gaming Computer"),
                    ),
                ),
                E.div(
                    {'class': 'table-cell'},
                    E.input(
                        {'type': 'checkbox', 'class': 'indicated', 'id': 'prize:warcraft-3-reforged', 'name': 'prize:warcraft-3-reforged'},
                    ),
                    E.label(
                        {'for': 'prize:warcraft-3-reforged', 'class': 'checkbox-indicator warcraft-yellow'},
                        E.img({'src': '/static/images/warcraft-reforged.png'}),
                        E.h2("Warcraft\u00A03: Reforged"),
                    ),
                ),
            ),
            E.button(
                {'class': 'submit', 'disabled': 'disabled'},
                "Enter Giveaway"
            ),
        )
    )
)


def render():
    return html.tostring(document, pretty_print=True, doctype="<!doctype html>")
