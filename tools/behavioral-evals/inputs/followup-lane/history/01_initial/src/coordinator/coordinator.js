export class Coordinator {
  #connected = false;

  connect() {
    this.#connected = true;
  }

  disconnect() {
    this.#connected = false;
  }

  get isConnected() {
    return this.#connected;
  }
}
