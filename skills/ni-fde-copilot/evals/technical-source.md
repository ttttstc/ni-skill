# Source

Internal reliability training note for a payment API.

When a client times out, it retries the payment request up to three times. The service stores a request key for 24 hours. Everyone knows the key makes retries safe, so the same payment cannot happen twice. A timeout means the payment failed from the client's point of view, although the processor may already have accepted it. The slide shows requests A, B and C converging on one stored result. Another note says duplicate charges were observed when merchants regenerated the key after every retry.

The team first retried every error. Permanent validation errors then created retry storms, so it changed the policy to retry only timeouts and selected 5xx responses. The material does not say what happens after the 24-hour window or whether all downstream processor calls are idempotent.
