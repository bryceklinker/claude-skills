export class AccountStore {
  #accounts = [];

  save(account) {
    this.#accounts = [...this.#accounts, account];
  }

  findByEmail(email) {
    return this.#accounts.find((account) => account.email === email) ?? null;
  }
}
