export class SignupService {
  #accounts;
  #notifier;

  constructor(accounts, notifier) {
    this.#accounts = accounts;
    this.#notifier = notifier;
  }

  signUp(email, password) {
    const account = { email, password, createdAt: new Date() };
    this.#accounts.save(account);
    this.#notifier.sendWelcome(email);
    return account;
  }
}
