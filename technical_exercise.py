import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageChops, ImageDraw 
        
class Frame1(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        # Set the background color
        self.configure(bg="#FFD700")
        # Welcome message 
        self.message_label = tk.Label(self, text="Welcome to Happy Badge", font=("Helvetica", 18), bg="#FFD700")
        self.message_label.pack(pady=10)
        self.furry_image = tk.Label(self)
        self.furry_image.pack()
        furry = ImageTk.PhotoImage(file="furry.png")
        self.furry_image.config(image=furry,bg="#FFD700")
        self.furry_image.image = furry
        # Upload image button
        self.upload_button = tk.Button(self, text="Upload Image", command=self.upload_image, bg="#3498db", fg="white")
        self.upload_button.pack(pady=10, anchor="center")

    def upload_image(self):
        file_path = filedialog.askopenfilename(title='Select Photo', filetypes=[("Image files", "*.png *.jpg *.jpeg")])  
        if file_path:
            try:
                # Test if it's actually a png image
                with Image.open(file_path) as img:
                    if img.format in ["PNG", "JPEG"]:
                        self.parent.show_frame2(file_path)
                    else:
                        tk.messagebox.showwarning(title=None, message="Selected file is not a supported image.")
            except Exception as e:
                tk.messagebox.showwarning(title=None, message=e)
            
            
class Frame2(tk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        # Set the background color
        self.configure(bg="#FFD700")
        self.current_image_path = None
        self.displayed_image = None
        # Display badge widget
        self.badge_image = tk.Label(self)
        self.badge_image.pack()
        # Add a label to display complaints
        self.complaint_label = tk.Label(self, text="", fg="red", bg="#FFD700")
        self.complaint_label.pack()
        # button container
        self.container = tk.Frame(self)
        self.container.config(bg="#FFD700")
        self.container.pack(side="bottom", pady=30)
        # Re-upload button
        self.start_over_button = tk.Button(self, text="Start Over", command=self.parent.show_frame1, bg="#3498db", fg="white")
        self.start_over_button.pack(in_=self.container, anchor="center", side="left")
        # Autofix button
        self.autofix_button = tk.Button(self, text="Hotfix", command=self.hotfix_image, bg="#FF5733", fg="white")
        self.autofix_button.pack(in_=self.container, anchor="center", side="left")
        
################################# Upload and display image methods ################################# 

    def upload_image(self, image_path):
        self.displayed_image = Image.open(image_path)
        self.displayed_image.thumbnail((512, 512))
        self.displayed_image = self.displayed_image.convert('RGBA')
        self.display_image()
        
    def display_image(self):
        badge = ImageTk.PhotoImage(self.displayed_image)
        self.badge_image.config(image=badge,bg="#FFD700")
        self.badge_image.image = badge
        self.image_validation(self.displayed_image)

###################################### Hotfix image methods #######################################        

    def hotfix_image(self):
        self.displayed_image = self.hotfix_image_dimensions(self.displayed_image)
        self.displayed_image = self.hotfix_image_trancparency(self.displayed_image)
        self.display_image()
        
    def hotfix_image_dimensions(self,image):
        image=image.resize((512, 512))
        return image
        
    def hotfix_image_trancparency(self,image):
        width, height = image.size
        # Create a mask
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0,width,height), fill=255)
        # Apply the mask to the image to make pixels outside the circle transparent
        image.putalpha(mask)
        return image
    
    
###################################### Check image methods #######################################

    def image_validation(self, image):
        complaints = []
        # Check if the image size is different from 512x512 and add to complaints
        if not self.check_image_dimensions(image):
            complaints.append("Image size is not 512x512 pixels")  
        # Check if the only non-transparent pixels are within a circle and add to complaints
        if not self.check_image_transparency(image):
            complaints.append("Non-transparent pixels are not within a circle") 
        # Check if image color has happy vibes
        if not self.check_image_feelings(image):
            complaints.append("The dominant colors in the image do not evoke a happy feeling as intended. :( You can do better!")
        # Print complaints
        if complaints:
            self.complaint_label.config(text="\n".join(complaints), fg="red")
        else:
            self.complaint_label.config(text="Perfect!")   
        # Hide & Show autofix button    
        if self.check_image_dimensions(image) and self.check_image_transparency(image):
            self.autofix_button.pack_forget()
        else:
            self.autofix_button.pack(in_=self.container, anchor="center", side="left")
        

    def check_image_dimensions(self, image):
        if image.size != (512, 512):
            return False
        else:
            return True
            
    def check_image_transparency(self, image):
        width, height = image.size
        # Create mask
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0,width,height), fill=255)
        # Compare the mask with the alpha channel of the image
        diff = ImageChops.difference(image.split()[3], mask).getextrema()
        # If the diff is (0, 0), it means all non-transparent pixels are within the circle
        if diff == (0, 0):
            return True
        else:
            return False
        
    def check_image_feelings(self, image):
        # Convert the image to an NumPy array
        image_array = np.array(self.displayed_image)
        # Convert the image to the HSV color space
        hsv_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        lower_happy_color = (20, 40, 40)  
        upper_happy_color = (50, 255, 255)
        mask = cv2.inRange(hsv_image, lower_happy_color, upper_happy_color)
        num_happy_pixels = cv2.countNonZero(mask)
        total_pixels = image_array.shape[0] * image_array.shape[1]
        happy_percentage = (num_happy_pixels / total_pixels) * 100
        if happy_percentage > 50:
            return True
        else:
            return False

class HappyBadge(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Happy Badge")
        # Set the initial window size
        self.geometry("700x700")  
        # Create the frames
        self.frame1 = Frame1(self)
        self.frame2 = Frame2(self)
        # Start with frame1
        self.show_frame1()
        
    def show_frame1(self):
        self.frame2.pack_forget()
        self.frame1.pack(fill="both", expand=True)

    def show_frame2(self, image_path):
        self.frame1.pack_forget()
        self.frame2.pack(fill="both", expand=True)
        self.frame2.upload_image(image_path)
        

if __name__ == "__main__":
    app = HappyBadge()
    app.mainloop()