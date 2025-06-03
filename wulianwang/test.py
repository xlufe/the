import requests
import json
import serial
import wave  # 用于音频文件操作
import pyaudio  # 用于录音和播放
import pyogg  # 用于Opus压缩

# 阿里云百炼大模型API配置
API_URL = "https://api.aliyun.com/v1/models/chat"
API_KEY = "your_api_key_here"  # 替换为您的实际API密钥
MODEL_NAME = "qwen"  # 使用的模型名称，例如qwen

# 动作映射：将用户指令映射到小车动作
ACTION_MAPPING = {
    "前进": "forward",
    "后退": "backward",
    "左转": "left",
    "右转": "right",
    "停止": "stop"
}

# 串口配置
SERIAL_PORT = "COM9"  # 端口为9号端口
BAUD_RATE = 115200  # 波特率为115200

# 初始化串口
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"串口已打开: {SERIAL_PORT} @ {BAUD_RATE}")
except serial.SerialException as e:
    print(f"无法打开串口: {e}")
    ser = None

# Opus编码器配置
opus_encoder = pyogg.OpusEncoder(16000, 1, pyogg.OPUS_APPLICATION_AUDIO)

def chat_with_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# 录音并压缩音频数据
def record_and_compress_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束...")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # 压缩音频数据
    compressed_data = opus_encoder.encode(b''.join(frames))
    return compressed_data

def decompress_and_play_audio(compressed_data):
    opus_decoder = pyogg.OpusDecoder(16000, 1)
    decompressed_data = opus_decoder.decode(compressed_data)

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True)

    print("开始播放...")
    stream.write(decompressed_data)
    print("播放结束...")

    stream.stop_stream()
    stream.close()
    p.terminate()

# 通过串口控制STM32小车的动作
def execute_action(action):
    if ser and ser.is_open:
        try:
            ser.write(action.encode())  # 发送动作指令
            print(f"发送指令: {action}")
        except serial.SerialException as e:
            print(f"串口发送失败: {e}")
    else:
        print(f"串口未打开，无法发送指令: {action}")

if __name__ == "__main__":
    print("欢迎使用小天小车机器人！请输入指令（如：前进、后退、左转、右转、停止），输入'exit'退出。")
    while True:
        user_input = input("您: ")
        if user_input.lower() in ["exit", "quit"]:
            print("退出对话。")
            break
        
        # 录音并压缩音频数据
        compressed_audio = record_and_compress_audio()
        
        # 发送压缩后的音频数据到STM32
        if ser and ser.is_open:
            try:
                ser.write(compressed_audio)
                print("音频数据已发送到STM32")
            except serial.SerialException as e:
                print(f"音频数据发送失败: {e}")
        
        # 获取AI响应
        ai_response = chat_with_ai(user_input)
        print(f"AI: {ai_response}")
        
        # 解析用户指令并执行对应动作
        for keyword, action in ACTION_MAPPING.items():
            if keyword in user_input:
                execute_action(action)
                break