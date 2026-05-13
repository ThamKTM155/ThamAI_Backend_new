# Environment Guide

## Backend Production

Render Service:
ThamAI_Production_Backend

---

# Environment Variables

## OPENAI_API_KEY

Mô tả:
API key dùng cho OpenRouter AI.

Lưu ý:
- Không commit key thật lên GitHub
- Không chia sẻ công khai
- Chỉ lưu trên Render Environment Variables

---

# AI Provider

OpenRouter

Model:
openai/gpt-3.5-turbo

---

# Frontend Production

Vercel Project:
ThamAI_Production_Frontend

---

# Production Rules

- Không sửa production trực tiếp khi chưa test
- Luôn commit trước khi deploy
- Không xóa backend production đang hoạt động
- Backup trước khi refactor lớn

