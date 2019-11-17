import contextvars
from uuid import UUID
from importlib.metadata import version

from lxml.builder import E
from lxml import html


_version = version("giveaway")
prizes = contextvars.ContextVar("prizes")
fields = contextvars.ContextVar("fields")
title = contextvars.ContextVar("title")
giveaway_id = contextvars.ContextVar("giveaway_id")


def html_boilerplate(head, body):
    document = (
        E.html(
            {"lang": "en"},
            E.head(
                E.meta(
                    {"charset": "utf-8"}
                ),
                E.meta({
                    "name": "viewport",
                    "content": "width=device-width, initial-scale=1, maximum-scale=1",
                }),
                *head,
            ),
            E.body(
                *body,
            ),
            E.footer(
                E.code(f"version {_version}"),
                E.a({"class": "reference", "href": "https://github.com/blue-span/giveaway"}, "source code"),
            )
        )
    )
    return document


def text_field(field_id, label, **kwargs):
    return (
        E.label(
            {"for": field_id},
            *label,
        ),
        E.input(
            {"id": field_id, "type": "text", "name": field_id, **kwargs},
        ),
    )


def prize_toggle(id, value, title, theme, image_src, featured):
    return E.prize(
        {"class": featured},
        E.input({
            "type": "checkbox",
            "class": "indicated",
            "id": f"{id}:{value}",
            "value": value,
            "name": id,
            **inject_checked(id, value),
        }),
        E.label(
            {
                "for": f"{id}:{value}",
                "class": " ".join([
                    "checkbox-indicator",
                    theme,
                ])
            },
            E.img({"src": image_src, "class": f"{theme}"}),
            E.prizetitle(title),
        ),
    )


def inject_error(name):
    if name in fields.get():
        _, explain = fields.get()[name]
        if explain is not None:
            return tuple(error(explain), )
        else:
            return tuple()
    else:
        return tuple()


def inject_last_value(name):
    if name in fields.get():
        values, _ = fields.get()[name]
        if values:
            return {"value": values[0]}
    return {}


def inject_checked(name, value):
    if name in fields.get():
        values, _ = fields.get()[name]
        if value in values:
            return {"checked": "checked"}
    return {}



def prize_fieldset():
    return E.fieldset(
        E.legend("Which giveaway prizes are you interested in winning?"),
        *inject_error("giveaway-prize:id"),
        E.prizelist(
            *prizes.get(),
        ),
        note(
            """

            Each prize is selected independently; selecting multiple prizes does
            not increase or decrease your chances of winning each type of prize
            (but does increase your overall chance of winning any prize).

            """
        ),
    )


def error(*error_text, title="Error"):
    return E.div(
        {"class": "admonition error"},
        E.p(
            {"class": "admonition-title"},
            title
        ),
        E.p(*error_text),
    ),


def note(*note_text, title="Note"):
    return E.div(
        {"class": "admonition note"},
        E.p(
            {"class": "admonition-title"},
            title
        ),
        E.p(*note_text),
    )

def success(*note_text, title="Success"):
    return E.div(
        {"class": "admonition success"},
        E.p(
            {"class": "admonition-title"},
            title
        ),
        E.p(*note_text),
    )


def external_link(text, href):
    return E.a({"class": "reference", "href": href, "target": "_blank"}, text)


def identification_fieldset():
    return E.fieldset(
        E.legend("How can we identify you?"),
        *inject_error("youtube:url"),
        *text_field(
            "youtube:url", (
                "Youtube Channel ID or URL ",
                E.small(E.code("(required)")),
            ),
            placeholder="UCpOkbe8JBvSHIEQn5D0V3tQ",
            pattern="^(?:https:\/\/www.youtube.com\/channel\/|)(UC[a-zA-Z0-9~._-]{22})\/?$",
            required="required",
            **inject_last_value("youtube:url"),
        ),
        note(
            """The """,
            E.a({"class": "reference", "href": "https://www.youtube.com/account_advanced", "target": "_blank"}, "channel ID"),
            """ or URL you enter here should be for the same channel
            you regularly use in live stream chat during Blue Span's
            streams. This will be used to determine

            """,
            external_link("basic eligibility", "https://bluespan.gg/giveaway/#who-is-eligible"),
            " for the giveaway.",
        ),
        *inject_error("discord:username"),
        *text_field(
            "discord:username", (
                "Discord Username ",
                E.small(E.code("(required)")),
            ),
            placeholder="Lulu-chan#4513",
            pattern="^.+#[0-9]{4}$",
            required="required",
            **inject_last_value("discord:username"),
        ),
        note(
            "You should already be a member of the ",
            external_link("Blue Span", "https://discord.gg/2nhPhsN"),
            " discord server. You will need to use Discord via this user to ",
            external_link("claim your prize", "https://bluespan.gg/giveaway/#i-am-a-winner-how-do-i-claim-my-prize"),
            "  if you are selected.",
        ),
    )


document = lambda subtitle, *content: html_boilerplate(
    head=(
        E.title("bluespan.gg giveaway registration"),
        E.link(
            dict(
                rel="stylesheet",
                href="/static/css/bluespan.css"
            ),
        )
    ),
    body=(
        E.h1({'class': 'title'}, "bluespan.gg"),
        E.h1({'class': 'subtitle'},
             subtitle,
             E.span({"class": "literal"}, title.get()),
        ),
        *content,
    )
)


def giveaway_form():
    return [
        note(
            """
            Please enter all required fields carefully and accurately; while
            this registration form attempts to perform some basic validation,
            registrations with inaccurate information may be silently ignored.
            """
        ),
        E.form(
            {
                "action": "/giveaway/register",
                "method": "post",
                "enctype": "application/x-www-form-urlencoded",
            },
            *inject_error("giveaway:id"),
            E.input({
                "type": "hidden",
                "id": "giveaway:id",
                "name": "giveaway:id",
                "value": giveaway_id.get(),
            }),
            identification_fieldset(),
            prize_fieldset(),
            E.button(
                {"class": "submit"},
                "Enter Giveaway"
            ),
        )
    ]


def status_section(status, message, registration_id):
    if status == "accepted":
        return [
            success(
                message,
                title=status.upper()
            ),
            E.small(
                E.p("You don't need to keep this anywhere or show this to anyone, but in case you are paranoid, your registration ID is: "),
                E.span({"class": "literal"}, str(registration_id))
            )
        ]
    elif status == "rejected":
        return [
            *error(
                message,
                title=status.upper()
            )
        ]
    return ["this should never happen"]


def render_form(giveaway_view, prize_view, field_state):
    def build_state():
        fields.set(field_state)
        giveaway_id.set(f"{UUID(bytes=giveaway_view[0])}")
        title.set("\u00A0".join(giveaway_view[1].split()))

        prizes.set([
            prize_toggle(
                id="giveaway-prize:id",
                value=f"{UUID(bytes=id)}",
                title=title,
                theme=theme,
                image_src=image_src,
                featured="featured" if int(featured) == 1 else "",
            )
            for title, image_src, theme, id, _giveaway_id, _quantity, featured
            in prize_view
        ])

    ctx = contextvars.Context()
    ctx.run(build_state)

    return ctx.run(
        lambda: html.tostring(
            document(
                "Giveaway Registration: ",
                *giveaway_form()
            ),
            pretty_print=True,
            doctype="<!doctype html>"
        )
    )


def render_status(status, message, giveaway_title, registration_id=None, **kwargs):
    def build_state():
        title.set("\u00A0".join(giveaway_title.split()))

    ctx = contextvars.Context()
    ctx.run(build_state)

    return ctx.run(
        lambda: html.tostring(
            document(
                "Registration Status: ",
                *status_section(status, message, registration_id)
            ),
            pretty_print=True,
            doctype="<!doctype html>"
        )
    )
