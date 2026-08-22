# Runtime Failure Modes — what breaks when nobody is waiting

Read this before writing any call site that starts work without waiting for it, subscribes to an event, or runs a loop in the background. It expands the craft-code principle *failure is a value, and every failure has an owner* (`PRINCIPLES.md` at the plugin root) into the constructs that quietly have no owner. The rules are language-agnostic; each carries per-language instances of the same shape.

## The question to ask at every call site

> **If this throws, who finds out?**

There are only four honest answers, and one of them is a bug:

| Answer | Verdict |
|---|---|
| "The caller — it's awaited and the failure is in the signature" | Fine. This is the default. |
| "The body itself — it catches, logs, and decides what to do" | Fine, with a *why*-comment naming that it's self-owned. |
| "The lifecycle — the handle is kept and observed when the component shuts down" | Fine, if something actually observes it. |
| "Nobody / the runtime" | **Defect.** Either it vanishes silently or it kills the process. |

A fifth answer — "it can't throw" — is almost never true for anything that touches I/O, a network, a UI thread, cancellation, or a dependency you don't own. Cancellation in particular surfaces as an exception in most runtimes, so "this only cancels" is still a throw.

## The constructs

### Discarded async work

Starting an operation that returns a handle and throwing the handle away. The work continues; its failure has nowhere to go.

```csharp
_ = PollContinuouslyAsync(token);          // C#: discard
```
```ts
doWorkAsync();                              // TS/JS: floating promise
```
```python
asyncio.create_task(poll())                 // Python: unreferenced task
```
```go
go poll()                                   // Go: panic in a goroutine kills the process
```

What actually happens varies and none of it is good: an unobserved rejection warning that nobody reads, a silently dead background loop that stops doing its job while the app looks healthy, or process termination. **Which one you get is a runtime detail; that you can't see it happen is the constant.**

Legal shapes:

```csharp
// self-guarding: the body owns its own failure, and says so
_ = PollSafelyAsync(token);

private async Task PollSafelyAsync(CancellationToken token)
{
    try { await PollContinuouslyAsync(token); }
    catch (OperationCanceledException) { }
    catch (Exception e) { _logger.LogError(e, "Polling stopped unexpectedly"); }
}
```
```csharp
// observed at shutdown: the handle is kept and awaited where the lifecycle ends
_pollTask = PollContinuouslyAsync(_cts.Token);
// ...
public async ValueTask DisposeAsync()
{
    _cts.Cancel();
    try { await _pollTask; } catch (Exception e) { _logger.LogError(e, "Poll faulted"); }
}
```

Storing the handle in a field is **not by itself** ownership. A field that nothing ever awaits is a discard with extra steps — the failure is just as invisible. Ownership means something observes it.

### Async event handlers with no return path

An event signature that returns nothing forces the handler to be fire-and-forget: the framework invokes it, ignores what it started, and any failure after the first suspension point escapes onto a thread with no handler. In .NET, `async void` throws on the thread pool and **crashes the process by default**; in the browser, the rejection is reported to an unhandled-rejection hook nobody wired up.

```csharp
private async void OnDeviceJoined(object? sender, DeviceJoined e)   // crashes the process
```

The whole body must be inside a guard, or it must delegate to a self-guarding method. Treat `async void` (and its equivalents) as a **shape that must be total** — no path out of it may throw.

### Background loops and timers

A loop whose iteration can throw ends the whole loop the first time it does. The component then looks alive and quietly does nothing — the worst failure mode, because there's no error and no signal.

Guard **inside** the loop, so one bad iteration doesn't end all of them:

```csharp
while (await timer.WaitForNextTickAsync(token))
{
    try { await RefreshAsync(); }
    catch (Exception e) { _logger.LogError(e, "Refresh failed"); }   // this tick only
}
```

Then check the loop condition itself: anything in the `while` — the wait, the read, the dequeue — sits *outside* that guard and will still end the loop if it throws. Decide deliberately whether ending is correct there (usually yes for cancellation, no for a transient read error) rather than inheriting it by accident.

Also decide what happens when the loop *does* end: a background worker that exits without saying so is invisible. Log the exit, or surface it as unhealthy.

### Subscriptions, callbacks, and lifecycle hooks

Anything the framework calls back into — a subscription callback, a message handler, a UI lifecycle hook, a signal handler — has the same shape: the caller is a framework that will do something unhelpful with your exception. Find out what it actually does (does it retry, drop the message, tear down the connection, log at debug?) before deciding the failure is handled. **Assume nothing about a framework's error behavior without reading it.**

And unsubscribe. A subscription outliving the object it calls into is a failure that fires long after the code that caused it has left the stack.

### Disposal and cleanup paths

Cleanup runs on the failure path, which is exactly when the system is already unhappy — a `finally`, a dispose, a teardown that throws will mask the original error with its own. Cleanup should be total: it must not throw, and it must not block forever.

## Applying it

- **While writing** (`strict-tdd`'s refactor step): every new call site that starts work without waiting for it gets an owner *before* the increment is done, and the failure path gets a test — the loop keeps running after a bad iteration, the handler logs instead of escaping.
- **Design time** (`architecture-design`): a design that introduces background work names the owner and the shutdown story up front.
- **Review** (`self-review`): a mechanical scan of the diff for discards, `async void`, floating promises, bare `go`/`create_task`, subscriptions, and loops — each one either has an owner or is a must-fix finding.
