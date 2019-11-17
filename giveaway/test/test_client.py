import h11

from giveaway.http import client


with client.factory("localhost", 8080) as make_request:
    for i in ["/giveaway/warcraft-reforged.png", "/giveaway/warcraft-reforged.png"]:
        events = make_request([
            h11.Request(
                method="GET",
                target=i,
                headers=[
                    ("host", "localhost"),
                ],
            ),
            h11.EndOfMessage(),
        ])
        print(events)
