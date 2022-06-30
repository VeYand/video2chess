'''
Copyright 2022 VeYand inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import os
import shutil
import time
import threading

from moviepy.editor import *
from rembg import remove
from PIL import Image
import cv2
from art import *

def avarage(picture):
    img = picture
    obj_for_count = img.load()

    img_for_size = img
    sq = [0, 0, 0]
    count = img_for_size.size[0] * img_for_size.size[1]
    width = img_for_size.size[0]
    height = img_for_size.size[1]

    for i in range(width):
        for j in range(height):
            sq[0] += obj_for_count[i, j][0]
            sq[1] += obj_for_count[i, j][1]
            sq[2] += obj_for_count[i, j][2]

    rgb = list(map(int, [sq[0] / count, sq[1] / count, sq[2] / count]))
    return rgb

def clear():
    path_list = [
        'board_frames',
        'frames',
        'new_frames',
        'audio.mp3',
        'work.mp4',
        'output_video.avi'
    ]
    for name in path_list:
        try:
            os.remove(name)
        except Exception:
            try:
                shutil.rmtree(name)
            except Exception:
                pass
def make_chess(size=1024, col = 128, black_cell_color = '#b38864', white_cell_color = '#f2d5b2'):
    b = Image.open('black.png')
    b = b.convert('RGBA')
    w = Image.open('white.png')
    w = w.convert('RGBA')

    s = max(b.size+w.size)
    b = b.resize((s, s))
    w = w.resize((s, s))

    b_bg = Image.new('RGBA', (s, s), color=black_cell_color)
    b_b = Image.new('RGBA', (s, s), color=black_cell_color)
    b_w = Image.new('RGBA', (s, s), color=black_cell_color)
    w_bg = Image.new('RGBA', (s, s), color=white_cell_color)
    w_b = Image.new('RGBA', (s, s), color=white_cell_color)
    w_w = Image.new('RGBA', (s, s), color=white_cell_color)

    w_b.paste(b, (0, 0), b)
    w_w.paste(w, (0, 0), w)
    b_b.paste(b, (0, 0), b)
    b_w.paste(w, (0, 0), w)

    pix = int(size/col)
    w_b = w_b.resize((pix, pix))
    w_w = w_w.resize((pix, pix))
    b_b = b_b.resize((pix, pix))
    b_w = b_w.resize((pix, pix))
    w_bg = w_bg.resize((pix, pix))
    b_bg = b_bg.resize((pix, pix))

    colors = [[w_b, w_w], [b_b, b_w], [b_bg, w_bg]]
    return colors
def convert_video(video_input_path='video.mp4', video_output_path='work.mp4', fps=20):
    clip = VideoFileClip(video_input_path)
    clip.audio.write_audiofile(r"audio.mp3", logger=None)
    if round(clip.fps) == fps:
        shutil.copy(video_input_path, video_output_path)
        return video_output_path
    clip.write_videofile(video_output_path, fps=fps, logger=None)
    return video_output_path

def get_frames(video_path='', remove_background=False, size=1024, col=128, colors=[], fps=20):
    try:
        avarage_list = [avarage(colors[0][0]), avarage(colors[0][1]), avarage(colors[1][0]), avarage(colors[1][1])]

        video = cv2.VideoCapture(video_path)
        max_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT)/video.get(cv2.CAP_PROP_FPS)*fps+1)
        currentframe = 0
        thread_count = 0

        if remove_background:
            threads = 3
        else:
            if fps // 2>=5:
                threads = fps // 2
            else:
                threads=5
        while True:
            ret, frame = video.read()
            if ret:
                name = f'./frames/frame{currentframe}.jpg'
                print(f'\rConverting frames to a chessboard...  ~[{currentframe}\{max_frames}]' , end='')
                cv2.imwrite(name, frame)

                thread_count += 1
                if thread_count % threads != 0:
                    threading.Thread(target=convert_frame, args=(name, remove_background, size, col, colors, avarage_list)).start()
                else:
                    convert_frame(name, remove_background, size, col, colors, avarage_list)
                last_frame = currentframe
                currentframe += 1
            else:
                break
        video.release()
        cv2.destroyAllWindows()
    except Exception:
        print('\rError...', end='')
        time.sleep(10)
        last_frame-=threads
    finally:
        return last_frame
def crop(old_path, max_size=512):
    old_img = Image.open(old_path)
    o_x, o_y = old_img.size
    if o_x>512 or o_y>512:
        k = max(o_x, o_y)/512
        old_img = old_img.resize((int(o_x/k), int(o_y/k)))
    size = (min(max_size, max(old_img.size)),) * 2
    if size[0] < old_img.size[0] or size[1] < old_img.size[1]:
        old_img.thumbnail(size)
    new_img = Image.new(old_img.mode, size, (0, 0, 0))
    x = (new_img.size[0] - old_img.size[0]) // 2
    y = (new_img.size[1] - old_img.size[1]) // 2
    new_img.paste(old_img, (x, y))
    old_img.close()
    os.remove(old_path)
    new_img = new_img.resize((512, 512))
    new_img.save(old_path)

def remove_bg(img_path=''):
    output = remove(Image.open(img_path))
    os.remove(img_path)
    output.save(img_path.replace('.jpeg', '.png').replace('.jpg', '.png'))
    return img_path.replace('.jpeg', '.png').replace('.jpg', '.png')

def comparsion(rgb1, rgb2):
    return ((rgb1[0] - rgb2[0])**2 + (rgb1[1] - rgb2[1])**2 + (rgb1[2] - rgb2[2])**2)

def chessing(img_path='', size=1024, col=128, colors=(), avarage_list=()):
    my_board = Image.new('RGBA', (size, size), color='#f2d5b2')

    im = Image.open(img_path)
    im = im.convert('RGB')
    im = im.resize((col, col))
    pixels = im.load()

    offset = size / col
    y_goast = -offset
    b_w = 1
    for y in range(0, col):
        y_goast+=offset
        offset_y = int(y_goast)
        x_goast = 0
        offset_x = 0
        b_w -= 1
        for x in range(0, col):
            color_cur = pixels[x, y]
            if b_w%2==0:
                color_list = colors[0]
                color1 = avarage_list[0]
                color2 = avarage_list[1]
            else:
                color_list = colors[1]
                color1 = avarage_list[2]
                color2 = avarage_list[3]
            if float(color_cur[0] + color_cur[1] + color_cur[2]) != 0.0 and float(color_cur[0] + color_cur[1] + color_cur[2]) != 765.0:
                if comparsion(color_cur, color1)>comparsion(color_cur, color2):
                    my_board.paste(color_list[1], (offset_x, offset_y), color_list[1])
                else:
                    my_board.paste(color_list[0], (offset_x, offset_y), color_list[0])
            else:
                pic = colors[2][::-1][b_w%2]
                my_board.paste(pic, (offset_x, offset_y), pic)
            x_goast+=offset
            offset_x=int(x_goast)
            b_w+=1
    name = img_path.split('/')[-1].replace('frame', '').replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
    my_board = my_board.convert('RGB')
    my_board.save(f'board_frames\\{name}.jpg')

def convert_frame(name, remove_background, size, col, colors, avarage_list):
    crop(name)
    if remove_background:
        name = remove_bg(img_path=name)
    chessing(img_path=name, size=size, col=col, colors=colors, avarage_list=avarage_list)
def make_video(last_frame=1, fps=20, size=1024):
    out = cv2.VideoWriter('output_video.avi', cv2.VideoWriter_fourcc(*'DIVX'), fps, (size, size))
    for i in range(0, int(last_frame) + 1):
        path = f'.\\board_frames\\{i}.jpg'
        img = cv2.imread(path)
        out.write(img)
    out.release()
    my_clip = VideoFileClip('output_video.avi')
    audio_background = AudioFileClip('audio.mp3')
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile('output.mp4', fps=fps, logger=None)
def run(size=1024, col=128, fps=20, remove_background=False, black_cell_color = '#b38864', white_cell_color = '#b38864'):
    tprint('video-2-chess', font='tarty1')
    print('Cleaning...', end='')
    clear()
    try:
        print('\rCreating folders...', end='')
        if not os.path.exists('frames'): os.makedirs('frames')
        if not os.path.exists('board_frames'): os.makedirs('board_frames')
        print('\rCreating an image of shapes...', end='')
        colors = make_chess(size=size, col=col, black_cell_color = black_cell_color, white_cell_color = white_cell_color)
        print('\rConverting the original video...', end='')
        video_path = convert_video(video_input_path='video.mp4', video_output_path='work.mp4', fps=fps)
        print('\rConverting frames to a chessboard...', end='')
        last_frame = get_frames(video_path=video_path, remove_background=remove_background, size=size, col=col, colors=colors, fps=fps)
        time.sleep(7)
        print('\rVideo_assembly...', end='')
        make_video(last_frame=last_frame, fps=fps, size=size)
        print('\rCompleted successfully!')
    except Exception:
        print('\nError... Cleaning...')
        time.sleep(5)
    finally:
        clear()

def main():
    #size%col==0
    size = 2048
    col = 128
    fps = 20
    remove_background = False
    black_cell_color = '#b38864'
    white_cell_color = '#f2d5b2'
    run(size=size, col=col, fps=fps, remove_background=remove_background, black_cell_color=black_cell_color, white_cell_color=white_cell_color)

if __name__ == '__main__':
    main()