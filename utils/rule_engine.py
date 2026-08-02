# =======================================
# rule_engine.py
# BUILD-39
# =======================================

def check_local_response(message):

    text = message.lower().strip()

    greetings = [
        "xin chào",
        "chào",
        "hello",
        "hi"
    ]

    if text in greetings:

        return (
            "Xin chào! Tôi là ThamAI. "
            "Rất vui được hỗ trợ anh."
        )

    return None


def memory_first(message, memory_context):

    """
    Nếu Memory đã đủ thông tin thì
    trả lời luôn, không gọi AI.
    """

    if not memory_context.strip():
        return None

    text = message.lower().strip()

    short_questions = [
        "vợ",
        "autoyoutube",
        "memoryai",
        "thamai",
        "memoryai_projectos",
        "thamai_projectos"
    
    ]

    if text in short_questions:

        return memory_context

    return None

def format_memory_reply(text):

    if not text:
        return text

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if "==========" in line:
            continue

        if line.startswith("🔍 Top"):
            continue

        if line.startswith("KẾT QUẢ"):
            continue

        lines.append(line)

    return "\n".join(lines)