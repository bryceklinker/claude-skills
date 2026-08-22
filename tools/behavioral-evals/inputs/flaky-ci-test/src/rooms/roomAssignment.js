export class RoomAssignment {
  constructor(api) {
    this.api = api;
    this.draggedDeviceId = null;
  }

  startDrag(deviceId) {
    this.draggedDeviceId = deviceId;
  }

  // The drop handler clears the drag state as soon as the request is sent so the
  // UI feels responsive; the list re-renders when the assignment call resolves.
  async dropOnRoom(roomId) {
    const deviceId = this.draggedDeviceId;
    this.draggedDeviceId = null;
    await this.api.assignDeviceToRoom(deviceId, roomId);
  }
}
