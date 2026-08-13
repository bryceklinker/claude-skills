# State and modules — where truth lives, and how it's composed

Two questions sit underneath every infrastructure change: where does the tool's record of "what currently exists" live, and how is the code that describes what *should* exist organized? Get the first wrong and two people can apply against different truths without either one knowing. Get the second wrong and staging and production quietly stop being the same infrastructure, one small unreviewed divergence at a time. Neither is exciting to design, and both are exactly where infrastructure quietly stops being trustworthy.

## Table of contents
- State: remote, versioned, locked, isolated, sensitive
- Modules: small, composable, clear inputs and outputs
- Environment parity: same modules, different inputs

## State: remote, versioned, locked, isolated, sensitive

The tool's state file is its record of what it believes exists and how the resources it manages map to real infrastructure. That record needs four properties, and each one is load-bearing on its own:

- **Remote.** State lives in a shared backend (an object store, a managed state service — the category, not a specific product), not on any one person's disk. The reason: a local state file is a single point of failure and a single point of truth that only one machine has — lose the laptop and you've lost the tool's memory of what it manages, even though the real infrastructure is still running.
- **Versioned.** Every change to state is retained, not overwritten in place. The reason: state can get corrupted or a bad apply can leave it out of sync with reality, and the only way back is a prior version of the record — without versioning, "roll back the state" isn't an option, only "reconstruct it by hand from what's actually deployed."
- **Locked.** Only one apply can hold the state at a time. The reason: two applies racing against the same state is how a resource gets created twice, deleted out from under a concurrent change, or left in a state the tool can no longer reconcile — locking isn't a nicety, it's what makes "apply" a safe verb to run from more than one place.
- **Isolated per environment and per component.** Dev, staging, and prod each get their own state, and large systems split state by component rather than one file for everything. The reason: shared state means a plan against dev can enumerate — and a bad apply can touch — resources in prod; isolation makes the blast radius of any one apply match the scope of the change someone actually intended.

On top of all four: state is **treated as sensitive, on the same footing as secrets** — never local, never committed to the repo, access scoped the way access to production credentials is scoped. The reason: state routinely contains resource attributes that are themselves secrets (connection strings, generated passwords, keys) whether or not anyone intended to put them there — the tool's job is tracking real infrastructure, and real infrastructure has real credentials.

## Modules: small, composable, clear inputs and outputs

Organize infrastructure code into small modules, each with a **narrow responsibility and an explicit interface** — declared inputs (variables) and declared outputs (values other modules or environments consume), nothing implicit passed between them. A module should be describable in one sentence: "the module that provisions the app's database," not "the module that provisions everything the app needs."

The reason small and composable beats one large configuration: a monolithic definition means every change — however small — is reviewed, planned, and applied against the whole system, and every author needs to hold the whole system in their head to be confident a change is safe. Small modules with explicit interfaces let a change to one module be reasoned about, reviewed, and applied on its own terms, with the interface as the contract for what the rest of the system can rely on. That composability is also what makes environment parity possible at all — see below.

## Environment parity: same modules, different inputs

Staging and production are built from **the same modules**, invoked with different input values — instance sizes, replica counts, domain names, feature toggles — never from a forked or hand-edited copy of the module for one environment. If production needs something staging doesn't, that need becomes a new input variable the module already knows how to accept, not a divergent branch of the module's code.

The reason forking is the failure to avoid: the moment production's module and staging's module are two different files, every fix, every convention update, every security patch has to be applied twice and can drift the moment someone forgets the second edit. Worse, it means staging no longer actually validates production's infrastructure shape — only a shape that resembles it, which is the same trust gap `build once, promote the same artifact` closes for application code, applied here to the modules that provision it. One module, many inputs, keeps "staging passed" a meaningful statement about what production is about to run.
