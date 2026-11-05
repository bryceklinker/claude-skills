export class ApsSender {
  #radio;

  constructor(radio) {
    this.#radio = radio;
  }

  send(message) {
    const status = this.#radio.transmit(message);
    if (status === "BUSY") {
      throw new Error("radio busy");
    }
    return { sent: true };
  }
}
