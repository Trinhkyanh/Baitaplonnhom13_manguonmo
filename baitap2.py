import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

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
        file_menu.add_command(label="Lưu tài liệu", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.root.destroy)
        menu_bar.add_cascade(label="Tài liệu", menu=file_menu)
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="- Điều chỉnh độ sáng ảnh.", command=self.Do_sang)
        edit_menu.add_command(label="- Điều chỉnh làm mịn ảnh.", command=self.Min_anh)
        edit_menu.add_command(label="- Điều chỉnh chuyển sang ảnh đen trắng.", command=self.Anh_denTrang)
        edit_menu.add_command(label="Cài đặt kích thước ảnh", command=self.ask_for_image_size)
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

            # Limit the image size if needed


            self.current_image = self.original_image.copy()
            self.display_image()

    def ask_for_image_size(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Cài đặt kích thước ảnh")

        width_label = tk.Label(dialog, text="Chiều rộng mới:")
        width_entry = tk.Entry(dialog)
        height_label = tk.Label(dialog, text="Chiều cao mới:")
        height_entry = tk.Entry(dialog)
        ok_button = tk.Button(dialog, text="OK", command=lambda: self.set_image_size(dialog, width_entry, height_entry))

        width_label.grid(row=0, column=0, padx=5, pady=5)
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        height_label.grid(row=1, column=0, padx=5, pady=5)
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    def set_image_size(self, dialog, width_entry, height_entry):
        try:
            new_width = int(width_entry.get())
            new_height = int(height_entry.get())

            if new_width > 0 and new_height > 0:
                self.original_image = self.resize_image(self.original_image, new_width, new_height)
                self.current_image = self.original_image.copy()
                self.display_image()

                dialog.destroy()

            else:
                self.show_error_message("Kích thước ảnh phải là số dương.")
        except ValueError as e:
            self.show_error_message("Vui lòng nhập số nguyên")

    def resize_image(self, image, new_width, new_height):
        height, width = image.shape[:2]

        # Resize image to the desired dimensions
        resized_image = cv2.resize(image, (new_width, new_height))

        return resized_image

    def show_error_message(self, message):
        messagebox.showerror("Lỗi", message)

    def display_image(self):
        if self.current_image is not None:
            image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            photo = ImageTk.PhotoImage(image)

            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

    def save_image(self):
        if self.current_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.current_image)



            # Attach the image



    def Do_sang(self):
        alpha = 1.25  # Example brightness factor
        beta = 35     # Example contrast factor

        self.current_image = cv2.convertScaleAbs(self.original_image, alpha=alpha, beta=beta)
        self.display_image()

    def Min_anh(self):
        kernel = np.ones((5, 5), np.float32) / 25  # Example smoothing kernel

        self.current_image = cv2.filter2D(self.original_image, -1, kernel)
        self.display_image()

    def Anh_denTrang(self):
        self.current_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
        self.display_image()

if __name__ == "__main__":
    root  = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()