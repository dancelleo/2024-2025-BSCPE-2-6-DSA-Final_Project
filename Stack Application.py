import pygame
import sys

class ParkingLot:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up screen and background
        self.screen = pygame.display.set_mode((800, 600))
        self.bg = pygame.image.load('bg.png')
        self.bg = pygame.transform.scale(self.bg, (int(self.screen.get_width() * 1), int(self.screen.get_height() * 1)))

        # Set up sprite groups
        self.all_sprites = pygame.sprite.Group()

        # List of car images (im1, im2, im3, ..., im10)
        self.car_images = ['im1.png', 'im2.png', 'im3.png', 'im4.png', 'im5.png', 'im6.png', 'im7.png', 'im8.png', 'im9.png', 'im10.png']

        # Increase the scale width and height of the car images to make them bigger
        self.scale_width = 20
        self.scale_height = 50

        # Create vertical queue positions for the cars
        self.car_positions = []

        # Set initial positions and target positions for cars
        self.base_y = -self.scale_height  # Starting position off-screen at the top
        self.queue_spacing = 55  # Vertical spacing between cars (with more margin for bigger cars)

        # Create more space at the bottom for the first car by shifting it down slightly
        self.max_target_y = self.screen.get_height() - self.scale_height - 15  # Start the first car 30px from the bottom side

        # Calculate the center position for the cars horizontally
        self.center_x = (self.screen.get_width() - self.scale_width) // 1.87  # Center of the screen minus half the car's width

        # Create cars' target positions starting from the bottom and stacking upwards
        for i in range(10):  # Create 10 cars
            target_y = self.max_target_y - i * self.queue_spacing  # Decrease target_y for each car to stack them
            self.car_positions.append((self.center_x, self.base_y, target_y))  # Center cars horizontally, start off-screen vertically

        # Initialize cars
        self.cars_objects = []
        self.plate_numbers = []  # List to hold plate numbers
        self.parked_cars = []  # List to hold parked cars

        self.clock = pygame.time.Clock()
        self.current_car = -1  # Index of the car currently moving (-1 means no car moving yet)
        self.waiting_for_input = True
        self.arrived_count = 0  # Counter for the number of cars that have arrived

        # Buttons
        self.show_license_plate_button = pygame.Rect(10, 540, 200, 50)
        self.show_parked_cars_button = pygame.Rect(590, 540, 200, 50)

    def get_plate_number(self, arrived_count, is_departure=False, message=None):
        font = pygame.font.SysFont(None, 48)
        font_message = pygame.font.SysFont(None, 36)
        input_box = pygame.Rect(250, 250, 300, 50)
        text = ''
        active = True
        clock = pygame.time.Clock()
        cursor_visible = True
        cursor_timer = 0
        message_timer = pygame.time.get_ticks() if message else None

        button_rect_arrival = pygame.Rect(300, 390, 200, 50)  # Arrival button
        button_rect_departure = pygame.Rect(300, 460, 200, 50)  # Departure button
        button_color = (0, 128, 0)  # Green button for arrival
        button_hover_color = (0, 255, 0)  # Lighter green for hover effect
        departure_button_color = (255, 0, 0)  # Red button for departure
        departure_button_hover_color = (255, 50, 50)  # Lighter red for hover effect

        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect_arrival.collidepoint(event.pos) and arrived_count < 10:  # Arrival button clicked
                        return text, 'arrival'
                    if button_rect_departure.collidepoint(event.pos):  # Departure button clicked
                        return text, 'departure'
                    if self.show_license_plate_button.collidepoint(event.pos):
                        self.show_license_plates()
                    if self.show_parked_cars_button.collidepoint(event.pos):
                        self.show_parked_cars()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]  # Remove last character on backspace
                    elif arrived_count < 10 or is_departure:  # Allow input if not full or if departure
                        text += event.unicode  # Add typed character

            # Draw background and text input box
            self.screen.fill((255, 255, 255))  # White background for the input screen

            # Display the message if there is one
            if message and pygame.time.get_ticks() - message_timer < 2000:  # Display message for 2 seconds
                message_surface = font_message.render(message, True, (255, 0, 0))
                message_rect = message_surface.get_rect(center=(self.screen.get_width() // 2, 50))
                self.screen.blit(message_surface, message_rect)
            else:
                message = None

            # Display the message "Please enter your plate number" centered above the input box
            prompt_message = font_message.render("Please enter your plate number", True, (0, 0, 0))
            prompt_message_x = input_box.x + (input_box.width - prompt_message.get_width()) // 2  # Center horizontally
            self.screen.blit(prompt_message, (prompt_message_x, input_box.y - 40))  # Position the message above the input box

            # Display the message "Cars parked: n" below the input box, or "Parking full" if max cars reached
            arrived_message = font_message.render(f"Cars parked: {arrived_count}" if arrived_count < 10 else "Parking full", True, (0, 0, 0))
            self.screen.blit(arrived_message, (input_box.x + (input_box.width - arrived_message.get_width()) // 2, input_box.y + input_box.height + 10))

            # Draw the input box and the text inside
            pygame.draw.rect(self.screen, (0, 0, 0), input_box, 2)  # Input box outline
            txt_surface = font.render(text, True, (0, 0, 0))
            self.screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

            # Blinking cursor
            cursor_timer += clock.get_time()
            if cursor_timer >= 500:
                cursor_visible = not cursor_visible
                cursor_timer = 0
            if cursor_visible:
                cursor_rect = pygame.Rect(input_box.x + 10 + txt_surface.get_width(), input_box.y + 10, 2, font.get_height())
                pygame.draw.rect(self.screen, (0, 0, 0), cursor_rect)

            # Draw the "Arrival" button
            if button_rect_arrival.collidepoint(pygame.mouse.get_pos()):  # Hover effect
                pygame.draw.rect(self.screen, button_hover_color, button_rect_arrival)
            else:
                pygame.draw.rect(self.screen, button_color, button_rect_arrival)

            button_text_arrival = font_message.render("Arrival", True, (255, 255, 255))
            self.screen.blit(button_text_arrival, (button_rect_arrival.x + (button_rect_arrival.width - button_text_arrival.get_width()) // 2, 
                                             button_rect_arrival.y + (button_rect_arrival.height - button_text_arrival.get_height()) // 2))

            # Draw the "Departure" button
            if button_rect_departure.collidepoint(pygame.mouse.get_pos()):  # Hover effect
                pygame.draw.rect(self.screen, departure_button_hover_color, button_rect_departure)
            else:
                pygame.draw.rect(self.screen, departure_button_color, button_rect_departure)

            button_text_departure = font_message.render("Departure", True, (255, 255, 255))
            self.screen.blit(button_text_departure, (button_rect_departure.x + (button_rect_departure.width - button_text_departure.get_width()) // 2, 
                                               button_rect_departure.y + (button_rect_departure.height - button_text_departure.get_height()) // 2))

            # Draw the "Show License Plates" button
            pygame.draw.rect(self.screen, (0, 0, 255), self.show_license_plate_button)
            show_license_plate_text = pygame.font.SysFont(None, 24).render("Show License Plates", True, (255, 255, 255))
            self.screen.blit(show_license_plate_text, (self.show_license_plate_button.x + 10, self.show_license_plate_button.y + 15))

            # Draw the "Show Parked Cars" button
            pygame.draw.rect(self.screen, (0, 0, 255), self.show_parked_cars_button)
            show_parked_cars_text = pygame.font.SysFont(None, 24).render("Show Parked Cars", True, (255, 255, 255))
            self.screen.blit(show_parked_cars_text, (self.show_parked_cars_button.x + 10, self.show_parked_cars_button.y + 15))

            pygame.display.flip()
            clock.tick(30)

    def run(self):
        while True:
            # Step 1: Get plate number for the current car using the "Arrival" button
            plate_number, action = self.get_plate_number(self.arrived_count)

            if action == 'arrival':
                # Check if the car with the plate number already exists
                existing_car = None
                for car in self.cars_objects:
                    if car.plate_number == plate_number:
                        existing_car = car
                        break

                if plate_number.strip().upper() in [car.plate_number.strip().upper() for car in self.cars_objects]:
                    # Display a message if the car is already parked
                    self.get_plate_number(self.arrived_count, message="Car is already parked.")
                else:
                    # Proceed with parking logic
                    self.arrived_count += 1  # Increment the arrived count

                    # Step 2: Animate the car
                    self.current_car += 1  # Move to the next car
                    self.waiting_for_input = False  # Allow the car to start moving

                    # Create a new car object and add it to the sprite group
                    x, y, target_y = self.car_positions[self.current_car]
                    car = Car(x, y, self.car_images[self.current_car % len(self.car_images)], self.scale_width, self.scale_height, target_y, plate_number, self.car_images[self.current_car % len(self.car_images)])
                    self.all_sprites.add(car)
                    self.cars_objects.append(car)
                    self.parked_cars.append(plate_number)  # Add the plate number to the parked cars list

            elif action == 'departure':
                # Strip spaces and make case-insensitive comparison
                plate_number_cleaned = plate_number.strip().upper()
                found_car = None
                for car in self.cars_objects:
                    if car.plate_number.strip().upper() == plate_number_cleaned:
                        found_car = car
                        break

                if not found_car:
                    # Display an error if the car is not found
                    self.get_plate_number(self.arrived_count, is_departure=True, message="Car cannot be found.")
                else:
                    # Check if there are any cars above the found car
                    car_index = self.cars_objects.index(found_car)
                    if car_index < len(self.cars_objects) - 1:
                        # There are cars above the found car
                        self.get_plate_number(self.arrived_count, is_departure=True, message="You cannot depart this car. There is a car parked above it.")
                    else:
                        found_car.is_departing = True  # Mark the car as departing
                        self.waiting_for_input = False  # Allow the car to start moving

            # Step 2: Animate the car if there are still cars
            while not self.waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Update car position for the car that is currently moving
                if self.current_car >= 0 and self.current_car < len(self.cars_objects):
                    self.cars_objects[self.current_car].update()

                    # If the car has reached its target position, wait for 1 second before allowing input
                    if self.cars_objects[self.current_car].rect.y == self.cars_objects[self.current_car].target_y:
                        # Wait for 1 second before showing the next input box
                        pygame.time.delay(1000)  # 1000 milliseconds = 1 second
                        self.waiting_for_input = True

                # Update car position for departing cars
                for car in self.cars_objects:
                    if car.is_departing:
                        car.update()
                        if car.rect.y <= -car.rect.height:
                            self.all_sprites.remove(car)
                            self.cars_objects.remove(car)
                            self.parked_cars.remove(car.plate_number)
                            self.arrived_count -= 1  # Decrement the arrived count
                            self.current_car -= 1  # Adjust the current car index
                            self.waiting_for_input = True  # Allow input after car departs

                # Draw background and sprites
                self.screen.blit(self.bg, (0, 0))
                self.all_sprites.draw(self.screen)

                pygame.display.flip()
                self.clock.tick(60)

    def show_license_plates(self):
        self.screen.fill((255, 255, 255))  # Clear the screen with a white background
        font = pygame.font.SysFont(None, 36)
        y_offset = 50
        for plate in self.parked_cars:
            text_surface = font.render(plate, True, (0, 0, 0))
            self.screen.blit(text_surface, (50, y_offset))
            y_offset += 40
        pygame.display.flip()
        pygame.time.wait(2000)  # Display for 2 seconds

    def show_parked_cars(self):
        self.screen.fill((255, 255, 255))  # Clear the screen with a white background
        y_offset = 50
        for car in self.cars_objects:
            car_image = pygame.image.load(car.image_path)
            car_image = pygame.transform.scale(car_image, (self.scale_width, self.scale_height))
            self.screen.blit(car_image, (50, y_offset))
            y_offset += self.scale_height + 10
        pygame.display.flip()
        pygame.time.wait(2000)  # Display for 2 seconds

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, image, scale_width, scale_height, target_y, plate_number=None, image_path=None):
        super().__init__()
        self.image = pygame.image.load(image)  # Load specific car image
        self.image = pygame.transform.scale(self.image, (scale_width, scale_height))  # Scale the image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 5
        self.target_y = target_y  # Target position for car to move to
        self.plate_number = plate_number  # Store the plate number
        self.is_departing = False  # Flag to indicate if the car is departing
        self.image_path = image_path  # Store the image path

    def update(self):
        if not self.is_departing:
            # Move the car toward its target (downwards)
            if self.rect.y < self.target_y:  # Move down
                self.rect.y += self.speed
            elif self.rect.y > self.target_y:  # Move up (in case of slight overshooting)
                self.rect.y -= self.speed
        else:
            # Move the car upward for departure animation
            if self.rect.y > -self.rect.height:  # If the car has not moved out of the screen yet
                self.rect.y -= self.speed  # Move the car up
            else:
                self.kill()  # Remove the car from the sprite group once it goes off the screen

if __name__ == "__main__":
    parking_lot = ParkingLot()
    parking_lot.run()
