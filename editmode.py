import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw


class EditMode:
    def __init__(self, tab, original_image=None, inpainted_image=None):
        self.tab = tab
        self.original_image = original_image
        self.inpainted_image = inpainted_image

        self.sidebar = tk.Frame(self.tab, width=200)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_orig_button = tk.Button(self.sidebar, text="Load Original Image", command=self.load_original_image)
        self.load_orig_button.pack(padx=10, pady=10)

        self.load_inpainted_button = tk.Button(self.sidebar, text="Load Inpainted Image",
                                               command=self.load_inpainted_image)
        self.load_inpainted_button.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(self.tab, width=800, height=600)  # Adjust the size of the canvas as needed
        self.canvas.pack()

        if self.inpainted_image:
            self.overlay_image = Image.new("RGBA", self.inpainted_image.size, (0, 0, 0, 0))
            self.overlay_draw = ImageDraw.Draw(self.overlay_image)
            self.display_image_on_canvas(self.inpainted_image)
        else:
            self.display_placeholder_text()

        self.canvas.bind("<B1-Motion>", self.draw_original_on_inpainted)
        self.canvas.bind("<ButtonRelease-1>",
                         lambda event: (setattr(event.widget, "last_x", None), setattr(event.widget, "last_y", None)))

    def display_image_on_canvas(self, img):
        canvas_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=canvas_image)
        self.canvas.image = canvas_image

    def display_placeholder_text(self):
        self.canvas.create_text(400, 300, text="No Image Loaded", font=("Arial", 20, "bold"))

    def draw_original_on_inpainted(self, event):
        if not self.original_image or not self.inpainted_image:
            return

        x, y = event.x, event.y
        brush_size = 10

        x_offset, y_offset = self.center_image_on_canvas(self.inpainted_image)
        x_rel = x - x_offset
        y_rel = y - y_offset

        if 0 <= x_rel < self.inpainted_image.width and 0 <= y_rel < self.inpainted_image.height:
            x1, y1, x2, y2 = x_rel - brush_size, y_rel - brush_size, x_rel + brush_size, y_rel + brush_size
            original_patch = self.original_image.crop((x1, y1, x2, y2))

            self.overlay_image.paste(original_patch, (x1, y1), original_patch)
            temp_img = self.inpainted_image.copy()
            temp_img.alpha_composite(self.overlay_image)

            self.display_image_on_canvas(temp_img)

    def center_image_on_canvas(self, img):
        width, height = img.size
        x_offset = (self.canvas.winfo_width() - width) // 2
        y_offset = (self.canvas.winfo_height() - height) // 2
        return x_offset, y_offset

    def load_original_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".jpg .jpeg .png .bmp")])
        if file_path:
            self.original_image = Image.open(file_path).convert("RGBA")

    def load_inpainted_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".jpg .jpeg .png .bmp")])
        if file_path:
            self.inpainted_image = Image.open(file_path).convert("RGBA")
            self.overlay_image = Image.new("RGBA", self.inpainted_image.size, (0, 0, 0, 0))
            self.overlay_draw = ImageDraw.Draw(self.overlay_image)
            self.display_image_on_canvas(self.inpainted_image)
            self.canvas.delete("all")  # Remove the placeholder text
        else:
            self.display_placeholder_text()  # Display the placeholder text if no image is loaded