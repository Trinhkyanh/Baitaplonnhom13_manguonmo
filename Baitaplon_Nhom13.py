import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
from tkinter import messagebox


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

        self.cropped_images = []

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
        edit_menu.add_command(label="- Cài đặt kích thước ảnh", command=self.ask_for_image_size)
        edit_menu.add_command(label="- Cắt ảnh", command=self.start_crop)
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

    #Hàm bắt đầu quá trình cắt ảnh khi người dùng nhấn nút
    def start_crop(self):
        self.cropping = True
        self.canvas.bind("<Button-1>", self.crop_start)

    #Hàm xử lý sự kiện bắt đầu cắt khi người dùng nhấn chuột
    def crop_start(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        self.canvas.bind("<B1-Motion>", self.crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.crop_end)

    #Hàm xử lý sự kiện kéo chuột khi đang cắt
    def crop_drag(self, event):
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        self.canvas.delete("crop_rectangle")
        self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y,
            outline="red", tags="crop_rectangle")

    #Hàm xử lý sự kiện kết thúc cắt khi người dùng nhả chuột
    def crop_end(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.cropping = False

        # Lưu vùng đã cắt
        cropped_image = self.current_image[
                        int(self.crop_start_y / self.scale_factor):int(self.crop_end_y / self.scale_factor),
                        int(self.crop_start_x / self.scale_factor):int(self.crop_end_x / self.scale_factor)]

        # Thêm ảnh đã cắt vào danh sách
        self.cropped_images.append(cropped_image.copy())

        # Hiển thị ảnh cắt trong cửa sổ mới và lưu ảnh
        self.display_and_save_cropped_image(cropped_image)

    # Hàm mới để hiển thị và lưu ảnh cắt trong cửa sổ mới
    def display_and_save_cropped_image(self, cropped_image):
        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        cropped_image = Image.fromarray(cropped_image)
        cropped_photo = ImageTk.PhotoImage(cropped_image)

        cropped_window = tk.Toplevel(self.root)
        cropped_window.title("Ảnh đã cắt")

        # Tạo thanh menu mới cho cửa sổ đã cắt
        cropped_menu_bar = tk.Menu(cropped_window)
        cropped_window.config(menu=cropped_menu_bar)

        # Thêm lựa chọn "Lưu ảnh đã cắt" vào thanh menu
        cropped_menu = tk.Menu(cropped_menu_bar, tearoff=0)
        cropped_menu_bar.add_cascade(label="Lưu ảnh đã cắt",command=lambda: self.save_cropped_image_from_menu(cropped_image))

        cropped_canvas = tk.Canvas(cropped_window)
        cropped_canvas.pack(expand=tk.YES, fill=tk.BOTH)

        cropped_canvas.config(width=cropped_photo.width(), height=cropped_photo.height())
        cropped_canvas.create_image(0, 0, anchor=tk.NW, image=cropped_photo)
        cropped_canvas.image = cropped_photo

    # Hàm mới để lưu ảnh từ thanh menu của cửa sổ đã cắt
    def save_cropped_image_from_menu(self, cropped_image):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("All files", "*.*")],initialfile=f"cropped_image_{len(self.cropped_images)}")
        if file_path:
            try:
                # Chuyển ảnh từ định dạng PIL Image sang NumPy array
                cropped_image_np = np.array(cropped_image)
                # Chuyển ảnh về định dạng BGR để sử dụng OpenCV
                cropped_image_np = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)
                # Lưu ảnh đã cắt
                cv2.imwrite(file_path, cropped_image_np)
                messagebox.showinfo("Thông báo", "Lưu ảnh đã cắt thành công!")
            except Exception as e:
                self.show_error_message(f"Lỗi khi lưu ảnh đã cắt: {str(e)}")

    def choose_file_path(self):
        self.selected_file_path = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("All files", "*.*")])

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
              self.show_error_message("Kích thước không hợp lệ. Vui lòng nhập lại.")
        except ValueError:
            self.show_error_message("Vui lòng nhập số nguyên cho chiều rộng và chiều dài.")

    def resize_image(self, image, new_width, new_height):
        height, width = image.shape[:2]

        # Thay đổi kích thước hình ảnh theo kích thước mong muốn
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

    def Do_sang(self):
        alpha = 1.25  # hệ số độ sáng
        beta = 35     # hệ số tương phản

        self.current_image = cv2.convertScaleAbs(self.original_image, alpha=alpha, beta=beta)
        self.display_image()

    def Min_anh(self):
        kernel = np.ones((5, 5), np.float32) / 25  # làm mịn

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