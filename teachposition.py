from armcontoller import move_servo, position_save

angle = [90, 90, 90, 90, 90, 90]
picked_servo = 0
step_length = 5

print("Choose a servo to move (0-5)")

move_servo(angle)

while True: 
    input = input(f"Current servo: {picked_servo}, Current angle: {angle[picked_servo]}.)")
    if input == "q":
        break
    elif input in "012345":
        picked_servo = int(input)
    elif input == "+":
        angle[picked_servo] = min(180, angle[picked_servo] + step_length)
        move_servo(angle)
    elif input == "-":
        angle[picked_servo] = max(0, angle[picked_servo] - step_length)
        move_servo(angle)
    elif input.startswith("s "):
        name = input[2:].strip()
        position_save(name, angle[:])
        print(f"Saved position '{name}' with angles: {angle}")
    else:
        print("Invalid input.")