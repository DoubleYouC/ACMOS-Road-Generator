import tkinter as tk
import logging

from os import listdir, makedirs, remove
from os.path import exists, isdir, join
from glob import glob
from subprocess import check_call
from tkinter.filedialog import askdirectory
from datetime import datetime

from PIL import Image


class Lod32:
    def __init__(self, texture, road):
        self.original_diffuse_texture = Image.open(f'{texture}.dds').convert('RGBA')
        self.original_normal_texture = Image.open(f'{texture}_n.dds').convert('RGBA')

        if exists(f'{road}.png'):
            road_diffuse_texture = Image.open(f'{road}.png').convert('RGBA')
            self.road_diffuse_texture = road_diffuse_texture.resize(self.original_diffuse_texture.size,
                                                                    Image.LANCZOS)
        else:
            self.road_diffuse_texture = None
            sm(f'Road diffuse texture does not exist for {texture}')

        if exists(f'{road}_d.png'):
            road_diffuse_mask_texture = Image.open(f'{self.road}_d.png').convert('RGBA')
        else:
            road_diffuse_mask_texture = Image.open('roads\\white.png').convert('RGBA')
            sm(f'Road diffuse mask texture does not exist for {texture}. Using default white mask.')
        self.road_diffuse_mask_texture = road_diffuse_mask_texture.resize(self.original_diffuse_texture.size,
                                                                          Image.LANCZOS)

        if exists(f'{road}_n.png'):
            road_normal_texture = Image.open(f'{road}_n.png').convert('RGBA')
            self.road_normal_texture = road_normal_texture.resize(self.original_normal_texture.size,
                                                                  Image.LANCZOS)
        else:
            self.road_normal_texture = None
            sm(f'Road normal texture does not exist for {texture}.')

        if exists(f'{road}_m.png'):
            road_normal_mask_texture = Image.open(f'{road}_m.png').convert('RGBA')
        else:
            road_normal_mask_texture = Image.open('roads\\white.png').convert('RGBA')
            sm(f'Road normal mask texture does not exist for {texture}. Using default white mask.')
        self.road_normal_mask_texture = road_normal_mask_texture.resize(self.original_normal_texture.size,
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
        return Image.open(f'{self.texture}{season_suffix}.dds').convert('RGBA')

    def seasonal_normal(self, season_suffix):
        return Image.open(f'{self.texture}{season_suffix}_n.dds').convert('RGBA')

class World:
    def __init__(self, lod_path, worldspace):
        path_to_lod32 = f'{lod_path}\\textures\\terrain\\{worldspace}\\{worldspace}.32.'
        textures = [fp.replace(path_to_lod32, '') for fp in glob(f'{path_to_lod32}*.dds')]
        sm(f'textures at {worldspace}: {textures}')
        coordinates = []
        for texture in textures:
            split_texture = texture.split('.', 2)
            xy = split_texture[0] + '.' + split_texture[1]
            if xy not in coordinates and '_n' not in xy:
                coordinates.append(xy)
        self.lod_coordinates = coordinates
        sm(f'coordinates: {coordinates}')

def run_texconv(args, input_file):
    try:
        arguments = " ".join(["\"" + x + "\"" for x in args])
        sm(f'executing: {arguments}')
        sm('Saving ' + input_file.replace('.png','.dds'))
        check_call(args, shell=True)
        if exists(input_file) and exists(input_file.replace('.png','.dds')):
            sm(f'Removing {input_file}')
            remove(input_file)
    except Exception as ex:
        sm("Error: " + str(ex))
        tk.messagebox.showerror("Error: " + str(ex))
        window.update()

def generate(worldspaces, output_path, lod_path, texconv):
    world_dict = {}

    for n in range(len(worldspaces)):
        if not exists(f'{output_path}\\textures\\terrain\\{worldspaces[n]}'):
            makedirs(f'{output_path}\\textures\\terrain\\{worldspaces[n]}')
        world_dict[f'{n} world'] = World(lod_path, worldspaces[n])
        for coordinates in world_dict[f'{n} world'].lod_coordinates:
            world_dict[f'{n} lod'] = LodSeasons(lod_path, worldspaces[n], coordinates)
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

def set_lod_path():
    directory = askdirectory(title='Please select the folder containing the unmodified terrain LOD...')
    if directory == '':
        return
    btn_lod_path['text'] = directory
    sm(f'LOD Path set to {directory}')
    btn_generate['text'] = 'Generate'
    if btn_output_path['text'] == 'Browse...':
        btn_output_path['text'] = directory
        sm(f'Output Path set to {directory}')

def set_output_path():
    directory = askdirectory(title='Please choose an Output folder...')
    if directory == '':
        return
    btn_output_path['text'] = directory
    sm(f'Output Path set to {directory}')

def generate_button():
    if btn_lod_path['text'] == 'Browse...':
        sm('Please specify an LOD Path.')
        btn_generate['text'] = 'Please specify an LOD Path.'
        return
    if btn_output_path['text'] == 'Browse...':
        sm('Please specify an Output Path.')
        btn_generate['text'] = 'Please specify an Output Path.'
        return
    if btn_output_path['text'] == btn_lod_path['text']:
        answer = tk.messagebox.askyesno('Overwrite LOD textures?','Are you sure you want to overwrite the LOD textures directly? If not, click no and specify a custom Output Path.')
        if not answer:
            set_output_path()
            return
    btn_generate['text'] = 'Please wait...'
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

        generate(worldspaces, output_path, lod_path, texconv)
        sm('All done!')
        btn_generate['text'] = 'Generate'
        tk.messagebox.showinfo("All Done!","All Done!")
    else:
        sm('Invalid Path to LOD... Please set the Path to LOD first!')

def sm(message):
    statusbar['text'] = message
    logging.info(message)
    window.update()
    
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

    window = tk.Tk()
    window.iconbitmap(default='Icon.ico')
    window.wm_title('ACMOS Road Generator')
    window.minsize(500, 100)

    frame1 = tk.Frame(window, width=500)
    lbl_lod_path_label = tk.Label(frame1, text="Path to LOD:")
    lbl_lod_path_label.pack(anchor=tk.NW, padx=5, pady=15, side=tk.LEFT)
    btn_lod_path = tk.Button(frame1, text='Browse...', command=set_lod_path)
    btn_lod_path.pack(anchor=tk.NW, padx=5, pady=10)
    frame1.pack()

    frame_output = tk.Frame(window)
    lbl_output_path_label = tk.Label(frame_output, text="Output Path:")
    lbl_output_path_label.pack(anchor=tk.NW, padx=5, pady=15, side=tk.LEFT)
    btn_output_path = tk.Button(frame_output, text='Browse...', command=set_output_path)
    btn_output_path.pack(anchor=tk.NW, padx=5, pady=10)
    frame_output.pack()
    
    frame2 = tk.Frame(window)
    btn_generate = tk.Button(frame2, text='Generate', command=generate_button)
    btn_generate.pack(anchor=tk.CENTER, padx=10, pady=10)
    
    statusbar = tk.Label(frame2, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W, wraplength=500)
    statusbar.pack(side=tk.BOTTOM, padx=3, fill=tk.X)

    frame2.pack(expand=True, fill=tk.X)
    
    window.mainloop()
