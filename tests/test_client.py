from giveaway import client


with client.factory("httpbin.org", 443) as make_request:
    for i in range(10):
        events = make_request([
            h11.Request(
                method="GET",
                target=f"/get?foo={i}",
                headers=[
                    ("host", "httpbin.org"),
                    ("content-type", "application/json"),
                ],
            ),
            h11.EndOfMessage(),
        ])
        print(events)
