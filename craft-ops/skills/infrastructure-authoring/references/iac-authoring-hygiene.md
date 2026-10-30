# IaC Authoring Hygiene

Each rule, and the failure it prevents.

- **Small composable modules over duplicated resource blocks.** When the same shape is needed more than once — across environments, services, regions — make it a module with explicit inputs and parameterize the differences. A copied block drifts the first time one copy is edited. But a module wrapping a single use is indirection without payoff; extract on the second real use.
- **Never co-locate a durable resource inside a compute unit.** Databases, object stores, queues, topics, and buses get their own unit and lifecycle; an instance, container, function, cluster, or autoscaling group receives their ID, ARN, or endpoint as an input. Compute is destroyed and replaced by design, and to the apply tool anything defined in the same unit shares that lifecycle — so a routine compute change takes the data with it.
- **Network foundation first.** The VPC/VNet, subnets, routing, and base security groups are their own unit, applied first and read by everything above it. Bundling the network with what sits in it causes circular dependencies or reverse-engineered IDs. Co-location separates units by lifecycle; foundation-first orders them by dependency.
- **Durable resources in their own network segment**, accepting connections by default only from the compute network and denying everything else. Every exception — a bastion, a migration or backup runner, a managed-service control plane — is named and justified. On a flat network, anything that reaches compute reaches the data.
- **Lifecycle guards on every durable resource** (deletion and replacement protection, `prevent_destroy` or equivalent), and durable changes migrated in place, never destroy-and-recreate. The guard blocks data loss even when a reviewer misses the destroy in a large plan.
- **Remote, locked state, with no secrets in code or state.** Local state is invisible to everyone else and races under concurrent applies. State also records resolved values, so a password passed as a variable lands in plaintext there; inject secrets from a secret manager at apply time.
- **Pin every provider and module version.** A floating version changes the apply with no commit to explain it.
- **Apply-twice is a no-op.** A second plan against unchanged source that still shows a diff means the definition doesn't converge — fix it before trusting re-applies.
- **No console edits; import instead.** A hand-made change isn't reviewed or recorded, and every later plan has to guess whether a diff is intended or undoing someone's fix.
