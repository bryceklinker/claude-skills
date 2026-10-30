import { test } from "node:test";
import assert from "node:assert/strict";
import { ApsSender } from "../src/aps/apsSender.js";

class FakeRadio {
  constructor(statuses) {
    this.statuses = [...statuses];
    this.transmitted = [];
  }

  transmit(message) {
    this.transmitted.push(message);
    return this.statuses.shift() ?? "OK";
  }
}

test("given an idle radio, when a message is sent, then it is transmitted", () => {
  const radio = new FakeRadio(["OK"]);

  const result = new ApsSender(radio).send("ping");

  assert.deepEqual(result, { sent: true });
  assert.deepEqual(radio.transmitted, ["ping"]);
});

test("given a busy radio, when a message is sent, then the send throws", () => {
  assert.throws(() => new ApsSender(new FakeRadio(["BUSY"])).send("ping"), /radio busy/);
});
