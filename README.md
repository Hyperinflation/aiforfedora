# Local Qwen-7B CLI Assistant

Minimal, moduler bir yerel AI asistan sistemi.

## Ozellikler

- CLI tabanli sohbet
- LLM tabanli tool routing
- Terminal tool (whitelist + tehlikeli komut engelleme)
- Web arama ve ozet
- Python coding assistant
- Chat memory (JSON)
- Basit local-file RAG (`data/knowledge`)

## Kurulum

1. Python 3.10+
2. Ollama kur:
   - https://ollama.com/download
3. Model cek:
   - `ollama pull qwen2.5:7b-instruct`
4. Bagimlilik:
   - `pip install -r requirements.txt`

## Calistirma

```bash
python main.py
```

## WebSocket Sunucu (Opsiyonel)

1. Bagimliliklari kur:
   - `pip install -r requirements.txt`
2. WS sunucuyu baslat:
   - `uvicorn server:app --host 127.0.0.1 --port 8000`
3. `websocket_client.html` dosyasini tarayicida ac.

Not:
- `🌐 Web` aktifse sunucu `force_web=True` ile internet aramasini zorlar.
- Kapaliysa `disable_web=True` ile yerel modda kalir.

## Fedora Uzak Istemci (RPM hedefi)

- Fedora makinede calisacak istemci: `fedora_bridge_client.py`
- Amaç: Fedora'dan soru gonder, Windows AI host'tan cevap al.
- COPR/RPM dosyalari: `packaging/rpm/`

## Dizin

```text
.
├── main.py
├── agent.py
├── config.py
├── llm.py
├── memory.py
├── rag.py
├── requirements.txt
├── data/
│   ├── chat_history.json  (runtime)
│   └── knowledge/         (RAG icin dokumanlar)
└── tools/
    ├── __init__.py
    ├── terminal_tool.py
    ├── web_tool.py
    └── coding_tool.py
```

## Qwen-7B Performans Notlari (dusuk VRAM)

- `config.py` icinde:
  - `num_ctx = 2048`
  - `num_batch = 64`
  - `temperature = 0.2`
- Gerekirse daha da dusur:
  - `num_ctx = 1024`
  - `num_batch = 32`

