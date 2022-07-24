# ReactiveIRC
## Backend

Gateway that handles PUSH request, translates it to format understandable by IRC server and sends it to the server.

Flask is used to handle HTTPS, and sockets provided by OS are used to establish connection with IRC server.

Proven to work with freenode and libera.
