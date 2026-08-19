# Direct raw HTTP provider

Conditionally executable for read-classified public IP-literal HTTP(S) targets only.

- the starting URL must use a public IP literal;
- every redirect must use a public IP literal;
- loopback, private, link-local, reserved, multicast, and unspecified addresses are blocked;
- hostname targets and hostname redirects are non-executable;
- caller-supplied and operator/environment proxy routes are non-executable;
- no provider credential is consumed.

Exact loopback fixture URLs require explicit process-level test mode and an exact URL JSON allowlist.
