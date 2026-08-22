import { test } from "node:test";
import assert from "node:assert/strict";
import { SignupService } from "../src/signup/signup.js";
import { AccountStore } from "../src/signup/accountStore.js";
import { WelcomeNotifier } from "../src/signup/welcomeNotifier.js";

test("given a valid email, when signing up, then the account is stored", () => {
  const accounts = new AccountStore();
  const service = new SignupService(accounts, new WelcomeNotifier());

  service.signUp("someone@example.com", "hunter2");

  assert.equal(accounts.findByEmail("someone@example.com").email, "someone@example.com");
});
