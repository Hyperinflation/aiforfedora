# COPR Build Rehberi

Bu paket Fedora istemcisi icindir: soru Fedora'dan gider, cevap Windows AI host'tan gelir.

## 1) Windows tarafi (AI host)

1. Sunucuyu disaridan erisilebilir calistir:
   ```bash
   set AI_BRIDGE_TOKEN=guclu_bir_token
   py -3 -m uvicorn server:app --host 0.0.0.0 --port 8000
   ```
2. Windows Firewall'da `8000/tcp` icin izin ver.
3. Fedora makineden su endpoint'e erisim olmali:
   - `ws://WINDOWS_IP:8000/ws/chat`

## 2) SRPM / COPR kaynak hazirlama

Git repository icine en az su dosyalar olmalı:
- `fedora_bridge_client.py`
- `fedora_bridge_chat_gui.py`
- `local-ai-bridge.desktop`
- `LICENSE`
- `README.md`
- `packaging/rpm/local-ai-bridge.spec`

`Source0` icin arsiv adi:
- `local-ai-bridge-0.1.0.tar.gz`

## 3) COPR build

```bash
copr-cli build <kullanici>/<proje> local-ai-bridge-0.1.0.src.rpm
```

veya SCM build:

```bash
copr-cli buildscm --clone-url <repo-url> --spec packaging/rpm/local-ai-bridge.spec <kullanici>/<proje>
```

## 4) Fedora istemcide kullanim

```bash
local-ai-bridge --server ws://WINDOWS_IP:8000/ws/chat --token guclu_bir_token "Merhaba"
local-ai-bridge --web --server ws://WINDOWS_IP:8000/ws/chat --token guclu_bir_token "Fedoranin en guncel surumu nedir"
```

