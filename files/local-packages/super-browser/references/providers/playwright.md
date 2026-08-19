# Local Playwright provider

Conditionally executable for read-classified, unauthenticated public targets only.

- no task/operator proxy may resolve;
- the initial hostname must resolve exclusively to public addresses;
- at least one public IPv4 address must be available;
- Chromium maps the hostname to one validated address and maps every other hostname to `~NOTFOUND` before construction;
- normal requests are guarded to the original host and rechecked for sensitive DNS evidence;
- service workers are blocked; WebSockets are closed before connection; WebRTC and WebTransport are removed from page globals; QUIC and non-proxied WebRTC UDP are disabled;
- cross-host redirects and subresources are aborted;
- later private, loopback, link-local, reserved, multicast, unspecified, or unresolved evidence is blocked.

Loopback/local-file execution is limited to explicit process-level test mode and an exact URL JSON allowlist. This mechanism is not production approval.
