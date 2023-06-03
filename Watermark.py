#coding=utf-8

from PIL import Image, ImageDraw, ImageFont
import os
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.colorchooser as tkc
import shutil
from tkinter import messagebox as mb
from chardet.universaldetector import UniversalDetector
from inspect import getsourcefile



class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.grid()
        
        self.begin_tk()
    
    def begin_tk(self):
        self.pict_path_label = tk.Label(text="Выбрать картинки для наложения водяного знака (в формате .jpg или .png):")
        self.pict_path_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.path_entry = tk.Text(width=100, height=10)
        self.path_entry.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.path_button = tk.Button(text="Обзор", command=self.get_pict_button_func)
        self.path_button.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        self.pict_path_label = tk.Label(text="Текст водяного знака:")
        self.pict_path_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.mark_entry = tk.Entry(width=100)
        self.mark_entry.insert(0, "Sample")
        self.mark_entry.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        
        self.visibility = 0.4
        self.offset = 50
        self.color_code = ((255, 255, 255), "#ffffff")
        
        
        self.visib_label = tk.Label(text="Прозрачность водяного знака:")
        self.visib_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.visib_scale = tk.Scale(from_=0, to=100, length=800, orient=tk.HORIZONTAL,
                                    tickinterval=10, command=self.set_visibility)
        self.visib_scale.set(40)
        self.visib_scale.grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.visib_var = tk.IntVar()
        self.visib_value = tk.Label(text=0, textvariable=self.visib_var)
        self.visib_value.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        
        
        self.offset_label = tk.Label(text="Отступы водяных знаков друг от друга:")
        self.offset_label.grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.offset_scale = tk.Scale(from_=0, to=1000, length=800, orient=tk.HORIZONTAL,
                                     tickinterval=50, command=self.set_offset)
        self.offset_scale.set(50)
        self.offset_scale.grid(row=7, column=0, padx=5, pady=5, sticky='w')
        self.offset_var = tk.IntVar()
        self.offset_value = tk.Label(text=0, textvariable=self.offset_var)
        self.offset_value.grid(row=7, column=1, padx=5, pady=5, sticky='w')
        
        
        self.color_button = tk.Button(text="Выбрать цвет водяного знака", command=self.choose_color)
        self.color_button.grid(row=8, column=0, padx=5, pady=5, sticky='w')
        self.color_label = tk.Label(text="Текущий цвет: " + self.color_code[1], bg=self.color_code[1])
        self.color_label.grid(row=9, column=0, padx=5, pady=5, sticky='w')
        
        
        self.end_button = tk.Button(text="Выход", command=self.master.destroy)
        self.end_button.grid(row=10, column=0, padx=5, pady=5, sticky='w')
        
        self.start_button = tk.Button(text="Старт", command=self.start_button_func)
        self.start_button.grid(row=10, column=1, padx=5, pady=5, sticky='e')
    
    def get_pict_button_func(self):
        self.pict_filetypes = (
            ('All files', '*.*'),
            ('Jpg files', '*.jpg'),
            ('Png files', '*.png')
        )
        self.pict_path_names = fd.askopenfilenames(filetypes=self.pict_filetypes)
        
        self.pict_path_names = tuple(x for x in self.pict_path_names if ('.' in x and (x[x.rfind('.'):] == '.jpg' or x[x.rfind('.'):] == '.png')))
        
        if self.pict_path_names == tuple():
            mb.showerror("Ошибка!", "Нет подходящих файлов среди выбранных для наложения водяного знака.")
            return 0
        
        self.path_entry.delete(1.0, tk.END)
        self.path_entry.insert(1.0, '\n'.join(self.pict_path_names))
    
    def set_visibility(self, new_val):
        self.visibility = float(new_val) / 100
        self.visib_var.set(new_val)
    
    def set_offset(self, new_val):
        self.offset = int(new_val)
        self.offset_var.set(new_val)
    
    def choose_color(self):
        temp_color = tkc.askcolor(title ="Выберите цвет")
        if temp_color != (None, None):
            self.color_code = temp_color
            self.color_label.configure(text="Текущий цвет: " + self.color_code[1], bg=self.color_code[1])
            if int(self.color_code[0][0]*0.299 + self.color_code[0][1]*0.587 + self.color_code[0][2]*0.114) > 186:
                self.color_label.configure(fg="black")
            else:
                self.color_label.configure(fg="white")
    
    def start_button_func(self):
        if self.mark_entry.get() == "":
            mb.showerror("Ошибка!", "Текст водяного знака отсутствует.")
            return 0
        self.mark_txt = self.mark_entry.get()
        
        self.pict_path_names = tuple(self.path_entry.get(1.0, tk.END).split('\n'))
        if self.pict_path_names == tuple():
            mb.showerror("Ошибка!", "Нет подходящих файлов среди выбранных для наложения водяного знака.")
            return 0
        
        for image_name in self.pict_path_names:
            if image_name == "":
                continue
                
            self.mode = "RGB"
            if image_name[image_name.rfind('.'):] == ".png":
                self.mode += "A"
            
            # print(image_name)
            self.base = Image.open(image_name).convert("RGBA")
            self.im_width, self.im_height = self.base.size
            # print(self.im_width, self.im_height)
            
            self.mark_font = ImageFont.truetype('arial.ttf', 40)
            self.font_size = self.mark_font.getsize(self.mark_txt)
            self.txt_img = Image.new('RGBA', self.font_size, (255,255,255,0))
            self.draw_content = ImageDraw.Draw(self.txt_img)
            
            self.draw_content.text((0, 0), self.mark_txt, font=self.mark_font, 
                                   fill=(self.color_code[0][0],self.color_code[0][1],
                                         self.color_code[0][2],int(255 * self.visibility)))
            self.rotated_txt = self.txt_img.rotate(45, expand=True, fillcolor=(0, 0, 0, 0))
            self.rotated_size = self.rotated_txt.size
            
            self.out_img = self.base
            for x in range(-(self.rotated_size[0] >> 1), self.im_width, self.rotated_size[0] + self.offset):
                for y in range(-(self.rotated_size[1] >> 1), self.im_height, self.rotated_size[1] + self.offset):
                    self.watermark_img = Image.new('RGBA', self.base.size, (255,255,255,0))
                    self.watermark_img.paste(self.rotated_txt, (x, y))
                    self.out_img = Image.alpha_composite(self.out_img, self.watermark_img)
            
            self.out_img = self.out_img.convert(self.mode)
            self.out_img.save(image_name[:image_name.rfind('.')] + "_Watermarked" + image_name[image_name.rfind('.'):])
        
        # Exiting the program after Start button: must be, probably...
        # self.master.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Водяной Знак")
    root.geometry("+300+300")
    app = Application(master=root)
    root.resizable(width=False, height=False)
    app.mainloop()
