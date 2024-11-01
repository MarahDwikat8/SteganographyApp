import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import os

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography - Hide Secret Text in Image")
        self.root.geometry("1200x600")
        self.root.configure(bg="#f0f0f5")

        self.original_image = None
        self.result_image = None
        self.secret_text = ""
        self.tk_image_original = None
        self.tk_image_result = None

        self.create_widgets()

    def create_widgets(self):
        # Define and configure the styles
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=6)
        style.configure("TLabel", font=("Arial", 14), padding=6)
        style.configure("TFrame", background="#f0f0f5")
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), background="#4a4e69", foreground="white")

        # Original Image Frame
        self.original_frame = ttk.Frame(self.root)
        self.original_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        self.original_label = ttk.Label(self.original_frame, text="Original Image", style="Title.TLabel")
        self.original_label.pack(fill=tk.X)
        self.original_canvas = tk.Canvas(self.original_frame, bg='white', width=400, height=300)
        self.original_canvas.pack(pady=10)
        self.load_image_button = ttk.Button(self.original_frame, text="Load Image", command=self.load_image)
        self.load_image_button.pack(pady=5)
        self.load_hidden_image_button = ttk.Button(self.original_frame, text="Load Image with Hidden Text", command=self.load_image_with_hidden_text)
        self.load_hidden_image_button.pack(pady=5)

        # Secret Text Frame
        self.secret_frame = ttk.Frame(self.root)
        self.secret_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        self.secret_label = ttk.Label(self.secret_frame, text="Secret Text", style="Title.TLabel")
        self.secret_label.pack(fill=tk.X)
        self.secret_textbox = tk.Text(self.secret_frame, width=30, height=15, font=("Arial", 12))
        self.secret_textbox.pack(pady=10)
        self.lsb_option = tk.IntVar(value=1)
        ttk.Radiobutton(self.secret_frame, text="1 LSB", variable=self.lsb_option, value=1).pack(anchor="w")
        ttk.Radiobutton(self.secret_frame, text="2 LSBs", variable=self.lsb_option, value=2).pack(anchor="w")
        ttk.Radiobutton(self.secret_frame, text="3 LSBs", variable=self.lsb_option, value=3).pack(anchor="w")

        # Result Image Frame
        self.result_frame = ttk.Frame(self.root)
        self.result_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        self.result_label = ttk.Label(self.result_frame, text="Result Image", style="Title.TLabel")
        self.result_label.pack(fill=tk.X)
        self.result_canvas = tk.Canvas(self.result_frame, bg='white', width=400, height=300)
        self.result_canvas.pack(pady=10)
        self.hide_button = ttk.Button(self.result_frame, text="Hide Text", command=self.hide_text)
        self.hide_button.pack(pady=5)
        self.save_button = ttk.Button(self.result_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(pady=5)
        self.restore_button = ttk.Button(self.result_frame, text="Restore Text", command=self.restore_text)
        self.restore_button.pack(pady=5)
        self.clear_button = ttk.Button(self.result_frame, text="Clear", command=self.clear)
        self.clear_button.pack(pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.show_image(self.original_canvas, self.original_image)

    def load_image_with_hidden_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        if file_path:
            self.result_image = Image.open(file_path)
            self.show_image(self.result_canvas, self.result_image)
            lsb_count = self.lsb_option.get()
            
            # Attempt to restore the hidden message
            restored_text = self.restore_message(self.result_image, lsb_count)
            
            if restored_text:
                self.secret_textbox.delete("1.0", tk.END)
                self.secret_textbox.insert(tk.END, restored_text)
            else:
                messagebox.showinfo("Info", "No hidden text found.")

    def show_image(self, canvas, image):
        image.thumbnail((400, 300))
        tk_image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        canvas.image = tk_image

    def hide_text(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return
        self.secret_text = self.secret_textbox.get("1.0", tk.END).strip()
        if not self.secret_text:
            messagebox.showerror("Error", "Please enter the secret text.")
            return

        lsb_count = self.lsb_option.get()
        self.result_image = self.hide_message(self.original_image.copy(), self.secret_text, lsb_count)
        self.show_image(self.result_canvas, self.result_image)

        # Clear the secret text box after hiding the text
        self.secret_textbox.delete("1.0", tk.END)

    def hide_message(self, cover_image, secret_text, lsb_count):
        cover_pixels = cover_image.load()
        width, height = cover_image.size
        # Convert secret text to binary and add a null terminator (indicates end of text)
        message_bits = ''.join([f'{ord(char):08b}' for char in secret_text]) + '00000000'
        
        bit_index = 0
        for y in range(height):
            for x in range(width):
                if bit_index < len(message_bits):
                    r, g, b = cover_pixels[x, y]

                    # Modify each color channel based on the LSB depth selected
                    r = (r & ~((1 << lsb_count) - 1)) | int(message_bits[bit_index:bit_index + lsb_count], 2)
                    bit_index += lsb_count
                    if bit_index < len(message_bits):
                        g = (g & ~((1 << lsb_count) - 1)) | int(message_bits[bit_index:bit_index + lsb_count], 2)
                        bit_index += lsb_count
                    if bit_index < len(message_bits):
                        b = (b & ~((1 << lsb_count) - 1)) | int(message_bits[bit_index:bit_index + lsb_count], 2)
                        bit_index += lsb_count

                    cover_pixels[x, y] = (r, g, b)

                # Exit the loop once all message bits are embedded
                if bit_index >= len(message_bits):
                    break
            if bit_index >= len(message_bits):
                break

        return cover_image

    def save_image(self):
        if self.result_image is None:
            messagebox.showerror("Error", "No result image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".bmp", filetypes=[("BMP files", "*.bmp")])
        if file_path:
            self.result_image.save(file_path)

    def restore_text(self):
        if self.result_image is None:
            messagebox.showerror("Error", "Please hide a text first.")
            return
        lsb_count = self.lsb_option.get()
        
        # Attempt to restore the hidden message
        restored_text = self.restore_message(self.result_image, lsb_count)
        
        # Debug output to verify restored text
        print(f"Restored Text: '{restored_text}'")  # Check what is restored
        
        self.secret_textbox.delete("1.0", tk.END)  # Clear the textbox before inserting new text
        if restored_text:
            self.secret_textbox.insert(tk.END, restored_text)
        else:
            messagebox.showinfo("Info", "No hidden text found.")

    def restore_message(self, result_image, lsb_count):
        result_pixels = result_image.load()
        width, height = result_image.size
        message_bits = ""

        for y in range(height):
            for x in range(width):
                r, g, b = result_pixels[x, y]

                # Extract LSBs from each color channel
                message_bits += f'{r & ((1 << lsb_count) - 1):0{lsb_count}b}'
                message_bits += f'{g & ((1 << lsb_count) - 1):0{lsb_count}b}'
                message_bits += f'{b & ((1 << lsb_count) - 1):0{lsb_count}b}'

                # Check for the null terminator in 8-bit blocks
                if len(message_bits) >= 8 and message_bits[-8:] == '00000000':
                    break
            if len(message_bits) >= 8 and message_bits[-8:] == '00000000':
                break

        # Convert binary string back to text
        restored_chars = []
        for i in range(0, len(message_bits) - 8, 8):
            byte = message_bits[i:i + 8]
            if byte == '00000000':  # Null terminator
                break
            restored_chars.append(chr(int(byte, 2)))

        return ''.join(restored_chars)

    def clear(self):
        self.original_canvas.delete("all")
        self.result_canvas.delete("all")
        self.secret_textbox.delete("1.0", tk.END)
        self.original_image = None
        self.result_image = None

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
