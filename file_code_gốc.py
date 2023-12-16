import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk



class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Chỉnh sửa ảnh")

        self.original_image = None
        self.current_image = None
        self.scale_factor = 1.0
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        self.create_menu()
        self.create_canvas()


    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Mở tài liệu", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.root.destroy)

        menu_bar.add_cascade(label="Tài liệu", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="- Điều chỉnh độ sáng ảnh.", command=self.Do_sang)
        menu_bar.add_cascade(label="Chức năng", menu=edit_menu)

        self.root.config(menu=menu_bar)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if file_path:
            try:
                self.original_image = cv2.imread(file_path)
                if self.original_image is None:
                    raise Exception("Lỗi: Tệp đã chọn không phải là hình ảnh hợp lệ!")
                self.current_image = self.original_image.copy()
                self.display_image()
            except Exception as e:
                self.show_error_message(str(e))
                self.original_image = cv2.imread(file_path)

            self.current_image = self.original_image.copy()
            self.display_image()


    def choose_file_path(self):
        self.selected_file_path = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("All files", "*.*")])

    def display_image(self):
        if self.current_image is not None:
            image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            photo = ImageTk.PhotoImage(image)

            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

    def Do_sang(self):
        alpha = 1.25  # Example brightness factor
        beta = 35     # Example contrast factor

        self.current_image = cv2.convertScaleAbs(self.original_image, alpha=alpha, beta=beta)
        self.display_image()


if __name__ == "__main__":
    root  = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()