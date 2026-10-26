"""Conference room and equipment scheduler.

Books rooms for time slots, allocates equipment such as projectors and
webcams, logs double bookings and exports the schedule to JSON.
"""
import itertools
import json
from datetime import datetime

# Shared state (mutated in place, never rebound, so no `global` is needed)
reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
_RESERVATION_IDS = itertools.count(1)


def schedule_room(room_id, time_slot, equipment_list=None):
    """Book a room for a slot and reserve equipment.

    Returns the new reservation id.
    """
    if equipment_list is None:
        equipment_list = []
    for reservation in reservations.values():
        if reservation["room"] == room_id and reservation["slot"] == time_slot:
            conflicts.append(f"{room_id} double-booked at {time_slot}")
    for e in equipment_list:
        equipment_pool[e] = equipment_pool[e] - 1
    reservation_id = next(_RESERVATION_IDS)
    reservations[reservation_id] = {
        "room": room_id, "slot": time_slot, "equipment": equipment_list}
    return reservation_id


def cancel_reservation(reservation_id):
    """Cancel a reservation and return its equipment to the pool."""
    reservation = reservations.pop(reservation_id, None)
    if reservation is None:
        print(f"No reservation with id {reservation_id} to cancel")
        return
    for e in reservation["equipment"]:
        equipment_pool[e] += 1


def slot_hours(time_slot):
    """Return the length in hours of a slot written like '09-11'."""
    start, end = time_slot.split("-")
    return int(end) - int(start)


def export_schedule(file="schedule.json"):
    """Write all reservations to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(reservations))


def log_conflicts(file="conflicts.log"):
    """Append recorded conflicts to a log file, then print the whole log."""
    with open(file, "a", encoding="utf-8") as f:
        for c in conflicts:
            f.write(f"{datetime.now()} {c}\n")
    with open(file, encoding="utf-8") as f:
        print(f.read(), end="")


def main():
    """Run a short demonstration of the scheduler."""
    schedule_room("Board-1", "09-11")
    schedule_room("Board-1", "09-11")
    b = schedule_room("Huddle-3", "14-12")
    schedule_room("Huddle-3", 1530)
    print("Slot length for b:", slot_hours(reservations[b]["slot"]))
    cancel_reservation(77)
    slot = input("Slot for Board-2, like 10-12 (Enter for 10-12): ") or "10-12"
    schedule_room("Board-2", slot, ["projector", "webcam"])
    export_schedule()
    log_conflicts()
    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)


if __name__ == "__main__":
    main()
