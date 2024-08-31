import dashscope
#export DASHSCOPE_API_KEY="sk-4f2065538c624436b571156515d816e4"
dashscope.api_key="sk-4f2065538c624436b571156515d816e4"

from http import HTTPStatus



def simple_multimodal_conversation_call(input_conmand):  #input_conmand
    """Simple single round multimodal conversation call.
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"audio": "save.wav"},
                {"text": input_conmand}
            ]
        }
    ]
    response = dashscope.MultiModalConversation.call(model='qwen2-audio-instruct',
                                                     messages=messages)
    # The response status_code is HTTPStatus.OK indicate success,
    # otherwise indicate request is failed, you can get error code
    # and message from code and message.
    if response.status_code == HTTPStatus.OK:
        print(response["output"]["choices"][0]["message"]["content"][0]["text"])
        return response["output"]["choices"][0]["message"]["content"][0]["text"]
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.


if __name__ == '__main__':  #假设你正在与人用英语交谈，语音中是对方提的问题，请将语音准确地转换为英文文字并回答语音问题,请严格按照下面格式回复：[提问:[], 回答:[]]]
    text=simple_multimodal_conversation_call("假设你正在与人用英语交谈，语音中是对方提的问题，请将语音准确地转换为英文文字并用英语回答语音问题,请严格按照以下方式进行回复：{'提问':[],'回答':[]}")
    print(text)
    exit()
    if ":" in text:
        question=text.split(":")[1].split('"')[0]
        print("question",question)
        anwer=text.split(":")[2][:-1]
        print("anwer",anwer)
    elif "：" in text:
        question=text.split("：")[1].split('"')[1]
        print("question",question)
        anwer=text.split("：")[2][:-1]
        print("anwer",anwer)
