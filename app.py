import streamlit as st
from record_voice import stream_voice_detect,recording_voice_init
import time
from qwen_audio import simple_multimodal_conversation_call
import os
import asyncio
import edge_tts


async def text_to_speech(text: str):
    file_path = "out.wav"
    if os.path.exists(file_path):
        os.remove(file_path)
    communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
    await communicate.save(file_path)
    os.system(f'start out.wav')

def text2voice(text: str):
    asyncio.run(text_to_speech(text))


#假设你是英语老师，正在与学生练习口语，语音中是学生提的问题，请重复学生问题并回答,请严格按照下面格式进行回复：   [提问:[],   对问题回答:[]]   ，例如：[提问:Have you ever gone to some place for driving or playing?], [对问题的回答:Yes, I have.]
def chat(filename):
    text=simple_multimodal_conversation_call("假设你正在与人用英语交谈，语音中是对方提的问题，请将语音准确地转换为英文文字并回答语音问题,请以字典的方式进行回复,例如：{'提问':[""],'回答':[""]}")
    print("back result",text)
    question=text.split("['")[1].split("']")[0]
    print("question",question)
    anwer=text.split("['")[2].split("']")[0]
    print("anwer",anwer)
    return [question,anwer]

# Streamlit应用
def main():
    st.title("语音口语练习")

    if 'texts' not in st.session_state:
        st.session_state.texts = []

    if 'recording' not in st.session_state:
        st.session_state.recording = False

    if 'button_key' not in st.session_state:
        st.session_state.button_key = str(time.time())
    p=recording_voice_init()
   
    def on_record_click():
        empty_placeholder = st.empty()
        while 1:
            stream_voice_detect(p)
            result = chat("output.wav")
            print(result)
            
            with empty_placeholder.container():
                st.markdown(f"**问题:** {result[0]}")
                st.markdown(f"**回答:** {result[1]}")
                st.markdown("---")
            #st.session_state.texts.clear()
            st.session_state.texts.insert(0, result)  # 插入到列表的开始位置
            st.session_state.button_key = str(time.time())  # 更新按钮键
            to_voice_text=result[1]
            print("to_voice_text",to_voice_text)
            text2voice(to_voice_text)
            for text in st.session_state.texts[1:]:
                st.markdown(f"**问题:** {text[0]}")
                st.markdown(f"**回答:** {text[1]}")
                st.markdown("---")
            
    if st.button("开始交谈", key=st.session_state.button_key):
        on_record_click()

if __name__ == "__main__":
    main()