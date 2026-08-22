export class WelcomeNotifier {
  #sent = [];

  sendWelcome(email) {
    if (!email.includes("@")) {
      throw new Error(`cannot deliver welcome mail to ${email}`);
    }
    this.#sent = [...this.#sent, email];
  }

  sent() {
    return [...this.#sent];
  }
}
