Name:           local-ai-bridge
Version:        0.1.0
Release:        4%{?dist}
Summary:        Fedora bridge with CLI and desktop chat

License:        MIT
URL:            https://example.local/local-ai-bridge
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3
Requires:       python3dist(websocket-client)
Requires:       python3-tkinter

%description
local-ai-bridge provides both a CLI client and a desktop chat app for Fedora.
It forwards prompts to a Windows-hosted AI WebSocket endpoint and shows replies.

%prep
%autosetup

%build
# no build step needed

%install
install -D -m 0755 fedora_bridge_client.py %{buildroot}%{_bindir}/local-ai-bridge
install -D -m 0755 fedora_bridge_chat_gui.py %{buildroot}%{_bindir}/local-ai-bridge-chat
install -D -m 0644 local-ai-bridge.desktop %{buildroot}%{_datadir}/applications/local-ai-bridge.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/local-ai-bridge
%{_bindir}/local-ai-bridge-chat
%{_datadir}/applications/local-ai-bridge.desktop

%changelog
* Thu Apr 30 2026 Local AI Maintainer <maintainer@example.com> - 0.1.0-4
- Make local-ai-bridge launch GUI by default on desktop sessions.

* Thu Apr 30 2026 Local AI Maintainer <maintainer@example.com> - 0.1.0-3
- Fix SRPM builds by installing .desktop from source root.

* Thu Apr 30 2026 Local AI Maintainer <maintainer@example.com> - 0.1.0-2
- Add desktop GUI chat app and launcher for menu-based chat usage.

* Thu Apr 30 2026 Local AI Maintainer <maintainer@example.com> - 0.1.0-1
- Initial RPM for Fedora COPR client bridge.

