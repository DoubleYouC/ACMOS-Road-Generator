'''ACMOS Road Generator'''

import tkinter as tk
import json
import logging

from tkinter import ttk
from tkinter.filedialog import askdirectory
from os import listdir, makedirs, remove, walk
from os.path import basename, exists, isdir, join, split
from glob import glob
from subprocess import check_call
from datetime import datetime
from zipfile import ZipFile

from PIL import Image, UnidentifiedImageError

class Lod32:
    def __init__(self, texture, road):
        
        self.diffuse_texture = smart_image_open(f'{texture}{self.season_suffixes[0]}.dds').convert('RGBA')
        if self.diffuse_texture.size[0] < 1024:
            self.diffuse_texture = self.diffuse_texture.resize((1024, 1024), Image.LANCZOS)

        self.normal_texture = smart_image_open(f'{texture}{self.season_suffixes[0]}_n.dds').convert('RGBA')
        if self.normal_texture.size[0] < 1024:
            self.normal_texture = self.normal_texture.resize((1024, 1024), Image.LANCZOS)
              
        if exists(f'{road}.png'):
            road_diffuse_texture = smart_image_open(f'{road}.png').convert('RGBA')
            self.road_diffuse_texture = road_diffuse_texture.resize(self.diffuse_texture.size,
                                                                    Image.LANCZOS)
        else:
            self.road_diffuse_texture = None
            sm(f'Road diffuse texture does not exist for {texture}')

        if exists(f'{road}_d.png'):
            road_diffuse_mask_texture = smart_image_open(f'{self.road}_d.png').convert('RGBA')
        else:
            road_diffuse_mask_texture = smart_image_open('roads\\white.png').convert('RGBA')
            sm(f'Road diffuse mask texture does not exist for {texture}. Using default white mask.')
        self.road_diffuse_mask_texture = road_diffuse_mask_texture.resize(self.diffuse_texture.size,
                                                                          Image.LANCZOS)

        if exists(f'{road}_n.png'):
            road_normal_texture = smart_image_open(f'{road}_n.png').convert('RGBA')
            self.road_normal_texture = road_normal_texture.resize(self.normal_texture.size,
                                                                  Image.LANCZOS)
        else:
            self.road_normal_texture = None
            sm(f'Road normal texture does not exist for {texture}.')

        if exists(f'{road}_m.png'):
            road_normal_mask_texture = smart_image_open(f'{road}_m.png').convert('RGBA')
        else:
            road_normal_mask_texture = smart_image_open('roads\\white.png').convert('RGBA')
            sm(f'Road normal mask texture does not exist for {texture}. Using default white mask.')
        self.road_normal_mask_texture = road_normal_mask_texture.resize(self.normal_texture.size,
                                                                        Image.LANCZOS)

    def new_diffuse(self, original_diffuse):
        new_diffuse_texture = Image.composite(original_diffuse,
                                              self.road_diffuse_texture,
                                              self.road_diffuse_mask_texture)
        new_diffuse_texture.paste(self.road_diffuse_texture, (0,0),
                                  mask = self.road_diffuse_texture)
        return new_diffuse_texture

    def new_normal(self, original_normal):
        new_normal_texture = Image.composite(original_normal,
                                             self.road_normal_texture,
                                             self.road_normal_mask_texture)
        new_normal_texture.paste(self.road_normal_texture, (0,0),
                                 mask = self.road_normal_texture)
        return new_normal_texture

class LodSeasons(Lod32):
    def __init__(self, lod_path, worldspace, lod_position):
        self.texture = f'{lod_path}\\textures\\terrain\\{worldspace}\\{worldspace}.32.{lod_position}'
        sm(f'texture is {self.texture}')
        self.road = f'roads\\{worldspace}\\{worldspace}.32.{lod_position}'
        self.season_suffixes = [fp.replace(self.texture, '').replace('_n.dds', '') for fp in glob(f'{self.texture}*_n.dds')]
        sm(f'seasons are {self.season_suffixes}')
        Lod32.__init__(self, self.texture, self.road)

    def seasonal_diffuse(self, season_suffix):
        seasonal_diffuse_image = smart_image_open(f'{self.texture}{season_suffix}.dds').convert('RGBA')
        if seasonal_diffuse_image.size[0] < 1024:
            seasonal_diffuse_image = seasonal_diffuse_image.resize((1024, 1024), Image.LANCZOS)
        return seasonal_diffuse_image

    def seasonal_normal(self, season_suffix):
        seasonal_normal_image = smart_image_open(f'{self.texture}{season_suffix}_n.dds').convert('RGBA')
        if seasonal_normal_image.size[0] < 1024:
            seasonal_normal_image = seasonal_normal_image.resize((1024, 1024), Image.LANCZOS)
        return seasonal_normal_image

class World:
    def __init__(self, lod_path, worldspace):
        path_to_lod32 = f'{lod_path}\\textures\\terrain\\{worldspace}\\{worldspace}.32.'

        #Finds all the textures in the worldspace
        self.textures = [fp.replace(path_to_lod32, '') for fp in glob(f'{path_to_lod32}*.dds')]
        sm(f'textures at {worldspace}: {self.textures}')

        #Finds all covered coordinates
        coordinates = []
        for texture in self.textures:
            split_texture = texture.split('.', 2)
            xy = split_texture[0] + '.' + split_texture[1]
            if xy not in coordinates and '_n' not in xy:
                coordinates.append(xy)
        self.lod_coordinates = coordinates
        sm(f'coordinates: {coordinates}')


def zip_dir(dir_name, zip_file):
    # Zips the files in directory
    with ZipFile(zip_file, 'w') as zip_object:
        for directory, subdirectories, files in walk(dir_name):
            for file in files:
                # Recreate path of the file in the zip
                file_path = join(directory, file)
                # Add file to zip
                zip_object.write(file_path, basename(file_path))

def smart_image_open(texture):
    #First attempt to open the texture
    try:
        return Image.open(texture)
    except FileNotFoundError as fnfe:
        sm(f'Error! File Not Found: {texture}. {fnfe}', 1)
    except UnidentifiedImageError:
        #if the file is not able to be read by built-in DDS plugin, convert the file using texconv.
        read_texconv(texture)
        return smart_image_open_last(texture)
    except ValueError as ve:
        sm(f'Error! Value Error: {texture}. {ve}', 1)
    except TypeError as te:
        sm(f'Error! Type Error: {texture}. {te}', 1)

def smart_image_open_last(texture):
    #Final attempt to open the texture following conversion through texconv
    try:
        return Image.open(texture)
    except FileNotFoundError as fnfe:
        sm(f'Error! File Not Found: {texture}. {fnfe}', 1)
    except UnidentifiedImageError as uie:
        sm(f'Error! Unidentified Image: {texture}. {uie}', 1)
    except ValueError as ve:
        sm(f'Error! Value Error: {texture}. {ve}', 1)
    except TypeError as te:
        sm(f'Error! Type Error: {texture}. {te}', 1)

def sm(message, error_message = False, update_status = True):
    #My standard Error message, statusbar update, and logging function
    logging.info(message)
    if error_message:
        tk.messagebox.showerror('Error', message)
    if update_status:
        statusbar['text'] = message
        window.update()

def run_texconv(args, input_file):
    #Converts png file to DDS and removes the temporary png file
    try:
        arguments = " ".join(["\"" + x + "\"" for x in args])
        sm(f'executing: {arguments}')
        sm('Saving ' + input_file.replace('.png','.dds'))
        check_call(args, shell=True)
        if exists(input_file) and exists(input_file.replace('.png','.dds')):
            sm(f'Removing {input_file}')
            remove(input_file)
    except Exception as ex:
        sm("Error: " + str(ex), 1)

def read_texconv(input_file):
    #Attemps to convert with texconv
    texconv = 'texconv\\texconv.exe'
    try:
        sm(f'Attempting to convert {input_file} with texconv')
        directory, filename = split(input_file)
        check_call([texconv, "-y", "-ft", "DDS", "-f", "BC7_UNORM", "-m", "1", "-bc", "x", "-o", directory, input_file], shell=True)
    except Exception as ex:
        sm("Error: " + str(ex), 1)

def generate(worldspaces, output_path, lod_path, texconv):
    #Generate roads
    world_dict = {}

    for n in range(len(worldspaces)):
        if not exists(f'{output_path}\\textures\\terrain\\{worldspaces[n]}'):
            makedirs(f'{output_path}\\textures\\terrain\\{worldspaces[n]}')
        world_dict[f'{n} world'] = World(lod_path, worldspaces[n])
        for coordinates in world_dict[f'{n} world'].lod_coordinates:
            try:
                world_dict[f'{n} lod'] = LodSeasons(lod_path, worldspaces[n], coordinates)
            except AttributeError as ae:
                sm(f'Error: AttributeError processing {worldspaces[n]} at {coordinates}. {ae}', 1)
                return text['Unsuccessful completion message'][language.get()]
            for season in world_dict[f'{n} lod'].season_suffixes:
                if world_dict[f'{n} lod'].road_diffuse_texture:
                    output_png = f'{output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}.png'
                    output_dir = f'{output_path}\\textures\\terrain\\{worldspaces[n]}'
                    world_dict[f'{n} lod'].new_diffuse(world_dict[f'{n} lod'].seasonal_diffuse(season)).save(output_png,'png')
                    sm(f'Processing {output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}.dds...')
                    run_texconv([texconv, "-y", "-ft", "DDS", "-f", "BC7_UNORM", "-m", "1", "-bc", "x", "-o", output_dir, output_png], output_png)
                if world_dict[f'{n} lod'].road_normal_texture:
                    output_png = f'{output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}_n.png'
                    output_dir = f'{output_path}\\textures\\terrain\\{worldspaces[n]}'
                    world_dict[f'{n} lod'].new_normal(world_dict[f'{n} lod'].seasonal_normal(season)).save(output_png,'png')
                    sm(f'Processing {output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}_n.dds...')
                    run_texconv([texconv, "-y", "-ft", "DDS", "-f", "BC7_UNORM", "-m", "1", "-bc", "x", "-o", output_dir, output_png], output_png)
    return text['Successful completion message'][language.get()]

def set_lod_path():
    #Sets the LOD Path
    directory = askdirectory(title=text['Select LOD Path window'][language.get()])
    if directory == '':
        return
    if '/textures/terrain' in directory:
        answer = tk.messagebox.askyesno(text['textures terrain in path prompt title'][language.get()],text['textures terrain in path prompt message'][language.get()])
        if answer:
            directory = directory.replace('/textures/terrain', '')
    btn_lod_path['text'] = directory
    sm(f'LOD Path set to {directory}')
    btn_generate['text'] = text['btn_generate'][language.get()]
    if btn_output_path['text'] == text['btn_lod_path'][language.get()]:
        btn_output_path['text'] = directory
        sm(f'Output Path set to {directory}')

def set_output_path():
    #Sets the Output Path
    directory = askdirectory(title=text['Select Output Path window'][language.get()])
    if directory == '':
        return
    if '/textures/terrain' in directory:
        answer = tk.messagebox.askyesno(text['textures terrain in path prompt title'][language.get()],text['textures terrain in path prompt message'][language.get()])
        if answer:
            directory = directory.replace('/textures/terrain', '')
    btn_output_path['text'] = directory
    sm(f'Output Path set to {directory}')

def generate_button():
    #What the generate button does
    if btn_lod_path['text'] == text['btn_lod_path'][language.get()]:
        sm(text['LOD path not set message'][language.get()])
        btn_generate['text'] = text['LOD path not set message'][language.get()]
        return
    if btn_output_path['text'] == text['btn_output_path'][language.get()]:
        sm(text['Output path not set message'][language.get()])
        btn_generate['text'] = text['Output path not set message'][language.get()]
        return
    if btn_output_path['text'] == btn_lod_path['text']:
        answer = tk.messagebox.askyesno(text['Overwrite LOD Textures prompt title'][language.get()],text['Overwrite LOD Textures prompt message'][language.get()])
        if not answer:
            set_output_path()
            return
    btn_generate['text'] = text['Please wait message'][language.get()]
    window.update()
    lod_path = btn_lod_path['text'].replace('/','\\')
    lod_path_terrain = f'{lod_path}\\textures\\terrain'
    sm(f'LOD Path set to {lod_path}')
    if exists(lod_path) and exists(lod_path_terrain):
        road_path = 'roads'
        sm(f'Road Path set to {road_path}')
        output_path = btn_output_path['text'].replace('/','\\')
        sm(f'Output Path set to {output_path}')
        texconv = 'texconv\\texconv.exe'
        sm(f'Texconv Path set to {texconv}')
        road_worldspaces = [f.lower() for f in listdir(road_path) if isdir(join(road_path, f))]
        sm(f'road_worldspaces: {road_worldspaces}')
        worldspaces = [f.lower() for f in listdir(lod_path_terrain) if isdir(join(lod_path_terrain, f)) and f.lower() in road_worldspaces]
        sm(f'worldspaces: {worldspaces}')

        #### TEMPORARY OVERRIDE ####
        #worldspaces = ['blackreach']
        ############################

        message = generate(worldspaces, output_path, lod_path, texconv)
        sm(message)
        btn_generate['text'] = text['btn_generate'][language.get()]
        tk.messagebox.showinfo(message, message)
    else:
        sm(text['Invalid LOD path message'][language.get()])

def change_language(lingo):
    #Language handling
    sm(f'Using {lingo}.', update_status = False)
    window.wm_title(text['title'][language.get()])
    lbl_lod_path_label['text'] = text['lbl_lod_path_label'][language.get()]
    btn_lod_path['text'] = text['btn_lod_path'][language.get()]
    lbl_output_path_label['text'] = text['lbl_output_path_label'][language.get()]
    btn_output_path['text'] = text['btn_output_path'][language.get()]
    btn_generate['text'] = text['btn_generate'][language.get()]
    
if __name__ == '__main__':
    #Make logs.
    today = datetime.now()
    log_directory_date = today.strftime("%Y %b %d %a - %H.%M.%S")
    my_app_log_directory = f'logs\\{log_directory_date}'
    my_app_log = f'{my_app_log_directory}\\log.log'
    makedirs(my_app_log_directory)
    logging.basicConfig(filename=my_app_log, filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    #translation json
    with open('translate.json') as translate_json:
        text = json.load(translate_json)

    #Create base app window
    window = tk.Tk()
    window.iconbitmap(default='Icon.ico')
    window.wm_title('Language')
    window.minsize(500, 100)

    #Three frames on top of each other to place widgets in
    frame_lod = tk.Frame(window)
    frame_output = tk.Frame(window)
    frame_generate = tk.Frame(window)

    #Language dropdown
    options = text['languages']
    language = tk.StringVar(window)
    language.set(text['languages'][0])
    optm_language = ttk.OptionMenu(window, language, text['languages'][0], *text['languages'], command=change_language)
    optm_language.pack(padx=5, pady=5)

    #LOD Path widgets
    lbl_lod_path_label = tk.Label(frame_lod, text=text['lbl_lod_path_label'][language.get()])
    lbl_lod_path_label.pack(anchor=tk.NW, padx=5, pady=15, side=tk.LEFT)
    btn_lod_path = tk.Button(frame_lod, text=text['btn_lod_path'][language.get()], command=set_lod_path)
    btn_lod_path.pack(anchor=tk.NW, padx=5, pady=10)
    
    #Output Path widgets
    lbl_output_path_label = tk.Label(frame_output, text=text['lbl_output_path_label'][language.get()])
    lbl_output_path_label.pack(anchor=tk.NW, padx=5, pady=15, side=tk.LEFT)
    btn_output_path = tk.Button(frame_output, text=text['btn_output_path'][language.get()], command=set_output_path)
    btn_output_path.pack(anchor=tk.NW, padx=5, pady=10)
    
    #Generate button
    btn_generate = tk.Button(frame_generate, text=text['btn_generate'][language.get()], command=generate_button)
    btn_generate.pack(anchor=tk.CENTER, padx=10, pady=10)
    
    #Statusbar
    statusbar = tk.Label(frame_generate, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W, wraplength=500)
    statusbar.pack(side=tk.BOTTOM, padx=3, fill=tk.X)

    #Pack frames
    frame_lod.pack()
    frame_output.pack()
    frame_generate.pack(expand=True, fill=tk.X)
    
    #Start app
    window.mainloop()
