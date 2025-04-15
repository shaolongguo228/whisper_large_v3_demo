from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import openai
import tempfile
import opencc
from fastapi.staticfiles import StaticFiles

# 创建FastAPI应用实例
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化本地Whisper API的OpenAI客户端
client = openai.Client(api_key="not empty", base_url="http://192.168.10.196:9997/v1")
# 设置使用的模型ID
model_id = "whisper-large-v3"

# 初始化OpenCC转换器（繁体中文转简体中文）
converter = opencc.OpenCC('t2s')

app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 定义WebSocket端点"/transcribe"
@app.websocket("/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    # 接受WebSocket连接
    await websocket.accept()
    try:
        while True:
            # 从前端接收音频数据块（二进制格式）
            data = await websocket.receive_bytes()

            # 将接收到的数据保存为临时WAV文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(data)
                f.flush()
                temp_path = f.name

            try:
                # 使用本地Whisper API进行语音转文字
                with open(temp_path, "rb") as audio_file:
                    result = client.audio.transcriptions.create(
                        model=model_id,
                        file=audio_file,
                        language="zh"
                    )

                # 将转写结果从繁体中文转换为简体中文
                simplified_text = converter.convert(result.text)

                # 通过WebSocket将简体中文结果发送回前端
                await websocket.send_text(simplified_text)

            finally:
                # 确保临时文件被清理
                import os
                os.remove(temp_path)
    except Exception as e:
        # 打印错误信息
        print(f"错误: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
