import openai
import argparse
import opencc
from pathlib import Path
converter = opencc.OpenCC('t2s')  # 繁体转简体

def transcribe_audio(base_url: str, model_id: str, audio_path: str):
    """使用OpenAI兼容API进行语音识别"""
    try:
        # 初始化客户端 (api_key可以是任意字符串，但不能为空)
        client = openai.Client(api_key="not empty", base_url=base_url)
        print(f"✅ 成功连接到语音识别服务: {base_url}")

        # 验证音频文件存在
        audio_file = Path(audio_path)
        if not audio_file.is_file():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        print(f"🔊 已加载音频文件: {audio_path} (大小: {audio_file.stat().st_size / 1024:.2f} KB)")

        # 执行语音识别
        print("🔄 正在识别音频...")

        with open(audio_file, "rb") as f:
            result = client.audio.transcriptions.create(
                model=model_id,
                file=f,
                language="chinese",
                prompt="用简体中文输出-simplified"
            )
        simplified_text = converter.convert(result.text)
        # 返回识别结果
        print("\n🎙️ 识别结果:")
        print(simplified_text)
        return simplified_text

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None


if __name__ == "__main__":
    # 设置默认参数（根据你的实际情况修改）
    DEFAULT_ENDPOINT = "http://192.168.10.196:9997/v1"  # 注意添加了/v1
    DEFAULT_MODEL_ID = "whisper-large-v3"
    DEFAULT_AUDIO = "part4.mp3"  # 默认音频文件路径

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="OpenAI兼容API语音识别客户端")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT,
                        help=f"API服务地址 (默认: {DEFAULT_ENDPOINT})")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID,
                        help=f"模型ID (默认: {DEFAULT_MODEL_ID})")
    parser.add_argument("--audio", default=DEFAULT_AUDIO,
                        help=f"音频文件路径 (默认: {DEFAULT_AUDIO})")

    args = parser.parse_args()

    # 打印启动信息
    print("\n" + "=" * 50)
    print(f"OpenAI兼容API语音识别客户端启动")
    print(f"服务地址: {args.endpoint}")
    print(f"使用模型: {args.model}")
    print(f"处理文件: {args.audio}")
    print("=" * 50 + "\n")

    # 执行语音识别
    transcribe_audio(args.endpoint, args.model, args.audio)