'''ACMOS Road Generator'''

import sys
import tkinter as tk
import json
import logging
import errno

from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from os import listdir, makedirs, remove, strerror
from os.path import exists, isdir, join, split, abspath
from shutil import make_archive, move, rmtree
from glob import glob, escape
from subprocess import check_call, CalledProcessError
from datetime import datetime
from configparser import ConfigParser

from PIL import Image, UnidentifiedImageError

class Road:
    def __init__(self, texture, road, diffuse_size, normal_size):
        #Import any existing road diffuse.
        if exists(f'{road}.png'):
            road_diffuse_texture = smart_image_open(f'{road}.png').convert('RGBA')
            self.road_diffuse_texture = road_diffuse_texture.resize(diffuse_size, Image.Resampling.LANCZOS)
        else:
            self.road_diffuse_texture = None
            sm(f'Road diffuse texture does not exist for {texture}',0,0)
        #Import any existing road diffuse mask.
        if exists(f'{road}_d.png'):
            road_diffuse_mask_texture = smart_image_open(f'{self.road}_d.png').convert('RGBA')
        else:
            road_diffuse_mask_texture = smart_image_open('white.png').convert('RGBA')
            sm(f'Road diffuse mask texture does not exist for {texture}. Using default white mask.',0,0)
        self.road_diffuse_mask_texture = road_diffuse_mask_texture.resize(diffuse_size, Image.Resampling.LANCZOS)
        #Import any existing road normal.
        if exists(f'{road}_n.png'):
            road_normal_texture = smart_image_open(f'{road}_n.png').convert('RGBA')
            self.road_normal_texture = road_normal_texture.resize(normal_size, Image.Resampling.LANCZOS)
        else:
            self.road_normal_texture = None
            sm(f'Road normal texture does not exist for {texture}.',0,0)
        #Import any existing road normal mask.
        if exists(f'{road}_m.png'):
            road_normal_mask_texture = smart_image_open(f'{road}_m.png').convert('RGBA')
        else:
            road_normal_mask_texture = smart_image_open('white.png').convert('RGBA')
            sm(f'Road normal mask texture does not exist for {texture}. Using default white mask.',0,0)
        self.road_normal_mask_texture = road_normal_mask_texture.resize(normal_size, Image.Resampling.LANCZOS)

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

class Lod(Road):
    def __init__(self, road_path, lod_path, worldspace, lod_position):
        self.texture = f'{lod_path}\\textures\\terrain\\{worldspace}\\{worldspace}.32.{lod_position}'
        sm(f'Processing {self.texture}')
        self.road = f'{road_path}\\{worldspace}\\{worldspace}.32.{lod_position}'
        #return a list of seasons found for the current position
        self.season_suffixes = [fp.replace(self.texture, '').replace('_n.dds', '') for fp in glob(escape(self.texture) + '*_n.dds')]
        sm(f'seasons are {self.season_suffixes}',0,0)
        if '' not in self.season_suffixes:
            sm(f'No default LOD exists for {worldspace} at {lod_position}. Please generate xLODGen with correct settings.', 1)
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    '{lod_path}\\textures\\terrain\\{worldspace}\\{worldspace}.32.{lod_position}_n.dds')

        self.diffuse_texture = smart_image_open(f'{self.texture}{self.season_suffixes[0]}.dds').convert('RGBA')
        if self.diffuse_texture.size[0] < 1024:
            sm(f'{self.texture}{self.season_suffixes[0]}.dds was smaller than 1024 resolution, so it will be upscaled.',0,0)
            self.diffuse_texture = self.diffuse_texture.resize((1024, 1024), Image.Resampling.LANCZOS)

        self.normal_texture = smart_image_open(f'{self.texture}{self.season_suffixes[0]}_n.dds').convert('RGBA')
        if self.normal_texture.size[0] < 1024:
            sm(f'{self.texture}{self.season_suffixes[0]}_n.dds was smaller than 1024 resolution, so it will be upscaled.',0,0)
            self.normal_texture = self.normal_texture.resize((1024, 1024), Image.Resampling.LANCZOS)

        Road.__init__(self, self.texture, self.road, self.diffuse_texture.size, self.normal_texture.size)

    def seasonal_diffuse(self, season_suffix):
        seasonal_diffuse_image = smart_image_open(f'{self.texture}{season_suffix}.dds').convert('RGBA')
        if seasonal_diffuse_image.size[0] < 1024:
            seasonal_diffuse_image = seasonal_diffuse_image.resize((1024, 1024), Image.Resampling.LANCZOS)
        return seasonal_diffuse_image

    def seasonal_normal(self, season_suffix):
        seasonal_normal_image = smart_image_open(f'{self.texture}{season_suffix}_n.dds').convert('RGBA')
        if seasonal_normal_image.size[0] < 1024:
            seasonal_normal_image = seasonal_normal_image.resize((1024, 1024), Image.Resampling.LANCZOS)
        return seasonal_normal_image

class World:
    def __init__(self, lod_path, worldspace):
        path_to_lod32 = f'{lod_path}\\textures\\terrain\\{worldspace}\\{worldspace}.32.'

        #Finds all the textures in the worldspace
        self.textures = [fp.replace(path_to_lod32, '') for fp in glob(escape(path_to_lod32) + '*.dds')]
        sm(f'textures at {worldspace}: {self.textures}')
        if self.textures == []:
            raise NoLodError(worldspace)

        #Finds all covered coordinates
        coordinates = []
        for texture in self.textures:
            split_texture = texture.split('.', 2)
            xy = split_texture[0] + '.' + split_texture[1]
            if xy not in coordinates and '_n' not in xy:
                coordinates.append(xy)
        self.lod_coordinates = coordinates
        sm(f'coordinates: {coordinates}')

class NoLodError(Exception):
    """Exception to raise when no lod is found for processing."""
    def __init__(self, worldspace):
        self.message = text['no lod32 textures found for worldspace message'][language.get()] + worldspace + '.'
        super().__init__(self.message)

def smart_image_open(texture):
    #First attempt to open the texture
    try:
        return Image.open(texture)
    except FileNotFoundError as fnfe:
        sm(f'Error! File Not Found: {texture}. {fnfe}', 1)
    except UnidentifiedImageError:
        #if the file is not able to be read by built-in DDS plugin, convert the file using texconv.
        return smart_image_open_last(read_texconv(texture))
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
    except AttributeError as ae:
        sm(f'Error! Attribute Error: {texture}. {ae}', 1)

def sm(message, error_message = False, update_status = True):
    #My standard Error message, statusbar update, and logging function
    logging.info(message)
    if error_message:
        messagebox.showerror('Error', message)
    if update_status:
        statusbar['text'] = message
    window.update()

def run_texconv(args, input_file):
    #Converts png file to DDS
    try:
        arguments = " ".join(["\"" + x + "\"" for x in args])
        sm(f'executing: {arguments}',0,0)
        sm('Saving ' + input_file.replace('.png','.dds'),0,0)
        check_call(args, shell=True)
    except CalledProcessError as ex:
        sm("Error: " + str(ex), 1)

def read_texconv(input_file):
    #Attemps to convert with texconv
    texconv = 'texconv\\texconv.exe'
    try:
        sm(f'Attempting to convert {input_file} with texconv',0,0)
        filename = split(input_file)[1]
        if not exists(f'{my_app_log_directory}\\tmp'):
            makedirs(f'{my_app_log_directory}\\tmp')
        check_call([texconv, "-y", "-ft", "DDS", "-f", "BC7_UNORM", "-m", "1", "-bc", "x", "-o", f'{my_app_log_directory}\\tmp', input_file], shell=True)
        temp_file_list.append(f'{my_app_log_directory}\\tmp\\{filename}')
        return f'{my_app_log_directory}\\tmp\\{filename}'
    except CalledProcessError as ex:
        sm("Error: " + str(ex), 1)

def generate(worldspaces, road_path, output_path, lod_path, texconv):
    #Clear output directory, if argument is given
    if '-clear-output-on-generate' in sys.argv and exists(output_path):
        rmtree(output_path)

    #Generate roads
    world_dict = {}
    progress_bar.start()
    for n in range(len(worldspaces)):
        if not exists(f'{output_path}\\textures\\terrain\\{worldspaces[n]}'):
            makedirs(f'{output_path}\\textures\\terrain\\{worldspaces[n]}')
        try:
            world_dict[f'{n} world'] = World(lod_path, worldspaces[n])
        except NoLodError as nle:
            sm(f'Error: {nle}', 1)
            progress_bar.stop()
            return text['Unsuccessful completion message'][language.get()]
        for coordinates in world_dict[f'{n} world'].lod_coordinates:
            try:
                world_dict[f'{n} lod'] = Lod(road_path, lod_path, worldspaces[n], coordinates)
            except AttributeError as ae:
                sm(f'Error: AttributeError processing {worldspaces[n]} at {coordinates}. {ae}', 1)
                progress_bar.stop()
                return text['Unsuccessful completion message'][language.get()]
            except FileNotFoundError as fnfe:
                sm(f'Error: FileNotFoundError processing {worldspaces[n]} at {coordinates}. {fnfe}', 1)
                progress_bar.stop()
                return text['Unsuccessful completion message'][language.get()]
            for season in world_dict[f'{n} lod'].season_suffixes:
                if world_dict[f'{n} lod'].road_diffuse_texture:
                    output_png = f'{output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}.png'
                    output_dir = f'{output_path}\\textures\\terrain\\{worldspaces[n]}'
                    world_dict[f'{n} lod'].new_diffuse(world_dict[f'{n} lod'].seasonal_diffuse(season)).save(output_png,'png')
                    temp_file_list.append(output_png)
                    sm(f'Processing {output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}.dds through texconv.',0,0)
                    run_texconv([texconv, "-y", "-ft", "DDS", "-f", "BC7_UNORM", "-m", "1", "-bc", "x", "-o", output_dir, output_png], output_png)
                if world_dict[f'{n} lod'].road_normal_texture:
                    output_png = f'{output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}_n.png'
                    output_dir = f'{output_path}\\textures\\terrain\\{worldspaces[n]}'
                    world_dict[f'{n} lod'].new_normal(world_dict[f'{n} lod'].seasonal_normal(season)).save(output_png,'png')
                    temp_file_list.append(output_png)
                    sm(f'Processing {output_path}\\textures\\terrain\\{worldspaces[n]}\\{worldspaces[n]}.32.{coordinates}{season}_n.dds through texconv.',0,0)
                    run_texconv([texconv, "-y", "-ft", "DDS", "-f", "BC7_UNORM", "-m", "1", "-bc", "x", "-o", output_dir, output_png], output_png)
    #remove temporary files
    sm('Removing temporary files...')
    sm(temp_file_list,0,0)
    for file in temp_file_list:
        if exists(file):
            try:
                remove(file)
            except OSError as ex:
                sm(f'Error: OSError removing {file}: {ex}')
    sm(text['Zip contents prompt title'][language.get()])
    
    if '-zip' in sys.argv:
        #If -zip argument is provided, zip output
        answer = True
    else:
        if '-autorun' in sys.argv:
            answer = False #Autorunning and no -zip argument provided. Don't zip
        else:
            #Not autorunning, ask the user
            answer = messagebox.askyesno(text['Zip contents prompt title'][language.get()],text['Zip contents prompt message'][language.get()])
    
    if answer:
        sm(f'Please wait... This could take a while... Zipping {output_path} to {output_path}\\Terrain LOD.zip')
        make_archive('Terrain LOD', 'zip', output_path)
        move('Terrain LOD.zip', f'{output_path}\\Terrain LOD.zip')
    progress_bar.stop()
    return text['Successful completion message'][language.get()]

def set_lod_path():
    #Sets the LOD Path
    directory = askdirectory(title=text['Select LOD Path window'][language.get()])
    if directory == '':
        return
    if '/textures/terrain' in directory:
        answer = messagebox.askyesno(text['textures terrain in path prompt title'][language.get()],text['textures terrain in path prompt message'][language.get()])
        if answer:
            directory = directory.replace('/textures/terrain', '')
    btn_lod_path['text'] = directory
    sm(f'LOD Path set to {directory}')
    config['DEFAULT']['lod_path'] = directory
    btn_generate['text'] = text['btn_generate'][language.get()]
    if btn_output_path['text'] == text['btn_lod_path'][language.get()]:
        btn_output_path['text'] = directory
        sm(f'Output Path set to {directory}')
        config['DEFAULT']['output'] = directory

def set_output_path():
    #Sets the Output Path
    directory = askdirectory(title=text['Select Output Path window'][language.get()])
    if directory == '':
        return
    if '/textures/terrain' in directory:
        answer = messagebox.askyesno(text['textures terrain in path prompt title'][language.get()],text['textures terrain in path prompt message'][language.get()])
        if answer:
            directory = directory.replace('/textures/terrain', '')
    btn_output_path['text'] = directory
    config['DEFAULT']['output'] = directory
    sm(f'Output Path set to {directory}')

def generate_button():
    #Update configuration file before starting the process
    config['DEFAULT']['roads'] = road_selection.get()
    config.write(open(config_file, 'w'))
    #What the generate button does
    btn_generate['state'] = 'disabled'
    if btn_lod_path['text'] == text['btn_lod_path'][language.get()]:
        sm(text['LOD path not set message'][language.get()])
        btn_generate['text'] = text['LOD path not set message'][language.get()]
        btn_generate['state'] = 'normal'
        return
    if btn_output_path['text'] == text['btn_output_path'][language.get()]:
        sm(text['Output path not set message'][language.get()])
        btn_generate['text'] = text['Output path not set message'][language.get()]
        btn_generate['state'] = 'normal'
        return
    if btn_output_path['text'] == btn_lod_path['text']:
        answer = messagebox.askyesno(text['Overwrite LOD Textures prompt title'][language.get()],text['Overwrite LOD Textures prompt message'][language.get()])
        if not answer:
            set_output_path()
            btn_generate['state'] = 'normal'
            return
    btn_generate['text'] = text['Please wait message'][language.get()]
    window.update()
    lod_path = btn_lod_path['text'].replace('/','\\')
    lod_path_terrain = f'{lod_path}\\textures\\terrain'
    sm(f'LOD Path set to {lod_path}')
    if exists(lod_path) and exists(lod_path_terrain):
        road_path = 'roads\\' + road_selection.get()
        sm(f'Road Path set to {road_path}')
        output_path = btn_output_path['text'].replace('/','\\')
        sm(f'Output Path set to {output_path}')
        texconv = 'texconv\\texconv.exe'
        sm(f'Texconv Path set to {texconv}',0,0)
        road_worldspaces = [f.lower() for f in listdir(road_path) if isdir(join(road_path, f))]
        sm(f'road_worldspaces: {road_worldspaces}',0,0)
        worldspaces = [f.lower() for f in listdir(lod_path_terrain) if isdir(join(lod_path_terrain, f)) and f.lower() in road_worldspaces]
        sm(f'worldspaces: {worldspaces}',0,0)

        #### TEMPORARY OVERRIDE ####
        #worldspaces = ['blackreach']
        ############################
        
        message = generate(worldspaces, road_path, output_path, lod_path, texconv)
        #send all done message
        sm(message)
        btn_generate['text'] = text['btn_generate'][language.get()]

        #Show all done message, if not auto-running.
        if '-autorun' not in sys.argv:
            messagebox.showinfo(message, message)
        btn_generate['state'] = 'normal'
    else:
        sm(text['Invalid LOD path message'][language.get()])
        btn_generate['state'] = 'normal'

def change_language(lingo):
    #Language handling
    sm(f'Using {lingo}.', update_status = False)
    config['DEFAULT']['language'] = lingo
    config.write(open(config_file, 'w'))
    window.wm_title(text['title'][language.get()])
    lbl_roads_label['text'] = text['lbl_roads_label'][language.get()]
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

    #Temp file list
    temp_file_list = []

    #translation json
    with open('translate.json', encoding='utf-8') as translate_json:
        text = json.load(translate_json)

    #Remember last used options or create a new config file
    config_file = 'config.ini'
    config = ConfigParser()
    if exists(config_file):
        config.read_file(open(config_file))
    else:
        config['DEFAULT'] = {'language': text['languages'][0],
                             'roads': listdir('roads')[0],
                             'lod_path': text['btn_lod_path'][text['languages'][0]],
                             'output': text['btn_output_path'][text['languages'][0]]}
        config.write(open(config_file, 'x'))

    #Create base app window
    window = tk.Tk()
    icon = tk.PhotoImage(file='Icon.gif')
    window.tk.call('wm','iconphoto',window._w, icon)

    window.wm_title('ACMOS Road Generator')
    window.minsize(500, 100)

    #Four frames on top of each other to place widgets in
    frame_roads = tk.Frame(window)
    frame_lod = tk.Frame(window)
    frame_output = tk.Frame(window)
    frame_generate = tk.Frame(window)

    #Language dropdown
    options = text['languages']
    language = tk.StringVar(window)
    language.set(config['DEFAULT']['language'])
    optm_language = ttk.OptionMenu(window, language, config['DEFAULT']['language'], *text['languages'], command=change_language)
    optm_language.pack(padx=5, pady=5)

    #Get CLI argument for output path
    out_path_arg = next((s for s in sys.argv if s.startswith("-o:")), None)
    if out_path_arg == None:
        out_path_arg = config['DEFAULT']['output']
    else:
        out_path_arg = abspath(out_path_arg[3:].strip('"\''))

    #Get CLI argument for LOD path
    lod_path_arg = next((s for s in sys.argv if s.startswith("-l:")), None)
    if lod_path_arg == None:
        lod_path_arg = config['DEFAULT']['lod_path']
    else:
        lod_path_arg = abspath(lod_path_arg[3:].strip('"\''))

    #Road selection dropdown
    lbl_roads_label = tk.Label(frame_roads, text=text['lbl_roads_label'][language.get()])
    lbl_roads_label.pack(anchor=tk.NW, padx=5, pady=10, side=tk.LEFT)
    road_dirs = listdir(f'roads')
    
    #Get CLI argument for road selection
    type_arg = next((s for s in sys.argv if s.startswith("-t:")), None)

    if type_arg != None:
        type_arg = type_arg[3:].strip('"\'')
        if road_dirs.index(type_arg) > -1:
            selected_roads = type_arg
    else:
        selected_roads = config['DEFAULT']['roads']

    road_selection = tk.StringVar(window)
    road_selection.set(selected_roads)
    optm_roads = ttk.OptionMenu(frame_roads, road_selection, selected_roads, *road_dirs)
    optm_roads.pack(anchor=tk.NW, padx=5, pady=9)
    
    #LOD Path widgets
    lbl_lod_path_label = tk.Label(frame_lod, text=text['lbl_lod_path_label'][language.get()])
    lbl_lod_path_label.pack(anchor=tk.NW, padx=5, pady=15, side=tk.LEFT)
    btn_lod_path = tk.Button(frame_lod, text=lod_path_arg, command=set_lod_path)
    btn_lod_path.pack(anchor=tk.NW, padx=5, pady=10)
    
    #Output Path widgets
    lbl_output_path_label = tk.Label(frame_output, text=text['lbl_output_path_label'][language.get()])
    lbl_output_path_label.pack(anchor=tk.NW, padx=5, pady=15, side=tk.LEFT)
    btn_output_path = tk.Button(frame_output, text=out_path_arg, command=set_output_path)
    btn_output_path.pack(anchor=tk.NW, padx=5, pady=10)
    
    #Generate button
    btn_generate = tk.Button(frame_generate, text=text['btn_generate'][language.get()], command=generate_button)
    btn_generate.pack(anchor=tk.CENTER, padx=10, pady=10)
    
    #Statusbar
    statusbar = tk.Label(frame_generate, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W, wraplength=500)
    statusbar.pack(side=tk.BOTTOM, padx=3, fill=tk.X)

    #Progressbar
    progress_bar = ttk.Progressbar(frame_generate, orient=tk.HORIZONTAL, length=100, mode='determinate')
    progress_bar.pack(side=tk.BOTTOM, padx=3, fill=tk.X)

    #Pack frames
    frame_roads.pack()
    frame_lod.pack()
    frame_output.pack()
    frame_generate.pack(expand=True, fill=tk.X)
    
    #Get autorun CLI argument
    if '-autorun' in sys.argv:
        generate_button()
    else:
        #Start app
        window.mainloop()
