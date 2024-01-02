import tkinter as tk
from PIL import Image, ImageTk  # Importing Image and ImageTk from PIL

# Initialize success status
success = False

# Global button initialization
option1_button = None
option2_button = None
other_option_button = None

# Function to update the interface based on different options
def update_interface(option=None):
    global success
    if success:
        # Already succeeded, no need to choose options
        show_success_image("success_image_option2.png")
        return
    else:
        if option == 1:
            # Implement logic for Option 1 here
            update_left_with_new_image("test_images/dog.jpg")
        elif option == 2:
            # Implement logic for Option 2 here
            update_left_with_new_image("test_images/cat.jpg")
        else:
            # Implement logic for other options here
            update_left_with_new_image("test_images/rabbit.jpg")

# Function to show success image
def show_success_image(image_path):
    global success
    success = True  # Update success status
    success_image = Image.open(image_path)
    success_image = success_image.resize((100, 100))  # Resize success image
    success_image = ImageTk.PhotoImage(success_image)
    success_image_label.configure(image=success_image)
    success_image_label.image = success_image
    success_image_label.pack()
    # Hide the other image label
    image_label.pack_forget()


# Function to update the left side with a new image
def update_left_with_new_image(image_path):
    # Load and display a new image
    image = Image.open(image_path)
    image = image.resize((desired_width, desired_height))  # Resize the image
    resized_image = ImageTk.PhotoImage(image)
    image_label.configure(image=resized_image)
    image_label.image = resized_image
    image_label.pack(side=tk.LEFT)


# Function to reset the interface to the initial state
def reset_interface():
    global success
    success = False  # Reset success status
    # Display the initial image and hide the success image label
    image_label.pack()
    success_image_label.pack_forget()
    # Destroy existing buttons if present
    destroy_option_buttons()
    # Recreate buttons for options
    create_option_buttons()

# Function to destroy existing option buttons
def destroy_option_buttons():
    global option1_button, option2_button, other_option_button
    if option1_button:
        option1_button.destroy()
    if option2_button:
        option2_button.destroy()
    if other_option_button:
        other_option_button.destroy()

# Function to create buttons for different options
def create_option_buttons():
    global option1_button, option2_button, other_option_button
    # Creating buttons for different options
    option1_button = tk.Button(main_frame, text="Option 1", command=lambda: update_interface(1))
    option1_button.pack(pady=5)
    option2_button = tk.Button(main_frame, text="Option 2", command=lambda: update_interface(2))
    option2_button.pack(pady=5)
    other_option_button = tk.Button(main_frame, text="Other Option", command=lambda: update_interface(3))
    other_option_button.pack(pady=5)

if __name__ == '__main__':
    # Creating the main window
    root = tk.Tk()
    root.title("Multiple Options")

    # Creating a frame for the image and buttons
    main_frame = tk.Frame(root)
    main_frame.pack()

    # Desired width and height for the displayed image
    desired_width = 300
    desired_height = 300

    # Displaying the initial PNG image
    initial_image_path = "test_images/dog.jpg"  # Change this to your initial PNG file path
    initial_image = Image.open(initial_image_path)
    initial_image = initial_image.resize((desired_width, desired_height))
    resized_initial_image = ImageTk.PhotoImage(initial_image)
    image_label = tk.Label(main_frame, image=resized_initial_image)
    image_label.pack(side=tk.LEFT)

    # Creating labels for the success image and hint
    success_image_label = tk.Label(main_frame)
    success_label = tk.Label(main_frame, text="")

    # Button to reset the interface
    reset_button = tk.Button(main_frame, text="Reset", command=reset_interface)
    reset_button.pack(pady=10)

    root.mainloop()
