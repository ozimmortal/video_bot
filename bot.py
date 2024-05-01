from TTS.api import TTS
import random,string
from seleniumbase import Driver
from bs4 import BeautifulSoup
import requests
import time,os
from moviepy.editor import *
from faster_whisper import WhisperModel
from moviepy.audio.fx import volumex

def get_quote()->list:
    res =  requests.get("https://api.quotable.io/quotes/random?tags=Success|minLength=50|maxLength=100").json()
    quote = res[0]["content"]
    print("found a quote")
    return quote
def text_to_speech(tts,txt:str) -> str:
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print("generating speech...")
    tts.tts_to_file(text=txt,
                file_path=f"{name}.wav",
                split_sentences=True,
                language="en",
                speaker="Damien Black",
                
         )
    
    name = f"{name}.wav"
    print("speech generated")
    return name
def tiktok_video_downloader(tk_url,path):
    
    try:
        driver = Driver(uc=True,headless=True)
   
        driver.default_get('https://snaptik.app/')
        driver.sleep(7)
        driver.type('input[name="url"]',tk_url)
        driver.click('button[type="submit"]')
        driver.sleep(3)
        html = driver.get_page_source()
        soup = BeautifulSoup(html, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
        div_element= soup.find('div',attrs={'class':'video-links'})
        url = div_element.find('a').get('href')
        print(url)
        res = requests.get(url)


        with open(path, "wb") as file:
            file.write(res.content)
    finally:
        driver.quit()

def background_tiktok_video(search_txt:str,amount:int) -> list:
    
    driver = Driver(uc=True,headless=True)
    url = "https://www.tiktok.com/"
    driver.default_get(url)
    driver.sleep(15)
    driver.click(".css-1gtmaw0-DivBoxContainer",by="css selector")
    driver.sleep(3)
    driver.type('input[name="q"]',search_txt)
    driver.click('button[type="submit"]')
    driver.sleep(30)
    html = driver.get_page_source()
    driver.quit()
    soup = BeautifulSoup(html, 'html5lib') # If this line causes an error, run 'pip install html5lib' .
    div_elements= soup.find_all('div',attrs={'class':'css-1as5cen-DivWrapper'})
    driver.sleep(5)
    urls = []
    video_paths = []
    for div in div_elements:
        a = div.find('a')
        urls.append(a.get("href"))
    time.sleep(3)
    
    
    if len(urls) > 0:  
        for i in range(amount):
            
            video_path = f"tiktok_video{i+1}.mp4"
            video_paths.append(video_path)
            tiktok_video_downloader(random.choice(urls),video_path)

    return video_paths

def transcribe(audio):
    model = WhisperModel("small")
    segments, info = model.transcribe(audio)
    language = info[0]
    print("Transcription language", info[0])
    segments = list(segments)
    for segment in segments:
        # print(segment)
        print("[%.2fs -> %.2fs] %s" %
              (segment.start, segment.end, segment.text))
    return (language, segments)

def create_subtitle_clips(subtitles, videosize,fontsize=22, font='Arial-Bold',stroke_color='black',stroke_width=1.25, color='white'):
    subtitle_clips = []

    for subtitle in subtitles[1]:
        start_time = float(subtitle.start)
        end_time = float(subtitle.end)
        duration = end_time - start_time

        video_width, video_height = videosize
        
        text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color,stroke_color=stroke_color,stroke_width=stroke_width, bg_color='transparent',size=(video_width * 0.88, None), method='caption').set_start(start_time).set_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = 'center'

        text_position = (subtitle_x_position, subtitle_y_position)                    
        subtitle_clips.append(text_clip.set_position(text_position))
    return subtitle_clips

def edit_video(audio,vid_clip)->None:
   
    sub = transcribe(audio)
    bg_song = random.choice(os.listdir(os.path.join('C://')))
    bg_song = "music/" + bg_song
    audio_clip = AudioFileClip(audio)
    audio_duration = audio_clip.duration
    audio_clip = afx.audio_fadeout(audio_clip,3)
    song = AudioFileClip(bg_song).subclip(0,audio_duration)
    song = song.fx( volumex.volumex, 0.35)
    clip = VideoFileClip(vid_clip).subclip(0,audio_duration)
    clip = clip.fx(vfx.colorx,0.3)
    t_sound = CompositeAudioClip([audio_clip,song])
    vid = clip.set_audio(t_sound)
    sub_clips = create_subtitle_clips(sub,vid.size)
    final_video = CompositeVideoClip([vid] + sub_clips)
    final_video.write_videofile(f"final_video.mp4")
    


def create_video(hashtag:str,quote:str,model:object)->None:
    audio = text_to_speech(model,quote)
    video_clip = background_tiktok_video(hashtag,1)
    edit_video(audio,random.choice(video_clip))
    

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
hashtag = "free motivational background videos"
quote = get_quote()
create_video(model=tts,hashtag=hashtag,quote=quote)


