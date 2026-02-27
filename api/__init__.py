"""
Geometry (Art Gallery) API package.

This package is the root of the geometry API backend. It exposes the main Lambda
entry point used by API Gateway. The API handles art gallery and job workflows:
listing and publishing galleries, creating and updating jobs, and authenticating
users via JWT or test token. All HTTP traffic is routed through the api.api
handler, which parses the request, matches routes, and delegates to Query or
Mutation handlers.

Lambda entry point: api.handler (API Gateway).

For example, to invoke the API handler from Lambda:
>>> from api import handler
>>> response = handler(event, context)  # event = API Gateway proxy event
"""
