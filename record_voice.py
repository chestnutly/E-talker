import fastasr
import math
import numpy as np
import soundfile as sf
import time
from pypinyin import lazy_pinyin,Style
import Levenshtein
import pyaudio
import wave 
import gc
import os


def stream_key_text_detect(text): 
    pinyin_sequence = lazy_pinyin(text, style=Style.NORMAL) 
    pinyin_str = ' '.join(pinyin_sequence) 
    key_pinyin = "xiao bu" 
    start_positions = [] 
    for i in range(len(pinyin_sequence) - 1): 
        sub_sequence = ' '.join(pinyin_sequence[i:i+2]) 
        if Levenshtein.distance(sub_sequence, key_pinyin) <= 1: # 误差阈值 
            return 1 
    if not start_positions: 
         return 0 
    return 0


def stream_voice_detect(p): 
    have_words=0 
    p.reset()
    FORMAT = pyaudio.paInt16 
    CHANNELS = 1 
    RATE = 16000 
    CHUNK = 1360 
    SILENCE_THRESHOLD = 300 
    SILENCE_DURATION =3 
    audio = pyaudio.PyAudio() 
    print("audio") 
    param_path = "paddlespeech_stream/" #models dir 
    samplerate =RATEalign_size = 1360 
    start_time = time.time() #
    end_time = time.time() 
    print("Model initialization takes {:.2}s.".format(end_time - start_time)) 
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK) 
    print("开始录音，请说话。") 
    frames = [] 
    silent_chunks = 0 
    all_text = '' 
    recording = True 
    start_time = time.time() 
    recording_begin_flag=0 
    luyin_count=0 
    while recording: 
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16) 
        msg = p.forward_chunk(data, 1) 
        recording_begin_flag=stream_key_text_detect(msg)
        if len(msg)>1:have_words=1 
        print('Current Result: "{}".'.format(msg)) 
        #print("recording_begin_flag",recording_begin_flag)
        #print("silent_chunks",silent_chunks)
        if recording_begin_flag:
            frames.append(data.tobytes()) 
        volume_norm = np.linalg.norm(data) * 10 / CHUNK
        if volume_norm < SILENCE_THRESHOLD: 
            silent_chunks += 1 
        else: silent_chunks = 0 
        if silent_chunks >= (RATE / CHUNK * SILENCE_DURATION) and have_words and recording_begin_flag: 
            recording =False 
            recording_begin_flag=0

            
        luyin_count+=1 
        if luyin_count>100 and recording_begin_flag==0: 
            luyin_count=0 
            p.reset() 
            gc.collect() 
        elif len(msg)>30 and silent_chunks >= (RATE / CHUNK * 0.8): 
            p.reset() 
            gc.collect() 
    stream.stop_stream() 
    stream.close() 
    audio.terminate() 
    
    double_channel_frames = []
    for frame in frames:
        left_sample = frame
        right_sample = left_sample  # 复制到右声道
        double_channel_sample = left_sample + right_sample
        double_channel_frames.append(double_channel_sample)
    

    file_path = "save.wav"
    if os.path.exists(file_path):
        os.remove(file_path)
    with wave.open("save.wav", 'wb') as wf: 
        wf.setnchannels(CHANNELS) 
        wf.setsampwidth(audio.get_sample_size(FORMAT)) 
        wf.setframerate(RATE)
        wf.writeframes( b''.join(frames)) 
    frames=[] #del p 
    gc.collect() 
    #return wav_name

def recording_voice_init():
    param_path = "paddlespeech_stream"       #sys.argv[1]
    #audio_path ="zh.wav"      #sys.argv[2]
    #data, samplerate = sf.read(audio_path, dtype='int16')
    #align_size = 1360
    #speech_align_len = (math.ceil(data.size / align_size) * align_size)
    #data = np.pad(data, [0, speech_align_len - data.size],
    #            mode='constant', constant_values=0)
    p = fastasr.Model(param_path, 1)
    return p
