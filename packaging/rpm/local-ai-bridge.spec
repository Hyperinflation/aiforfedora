Name:           local-ai-bridge
Version:        0.1.0
Release:        1%{?dist}
Summary:        Fedora CLI bridge for remote Windows AI inference

License:        MIT
URL:            https://example.local/local-ai-bridge
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3
Requires:       python3dist(websocket-client)

%description
local-ai-bridge is a minimal Fedora CLI tool that forwards prompts to a
Windows-hosted AI WebSocket endpoint and prints responses in terminal.

%prep
%autosetup

%build
# no build step needed

%install
install -D -m 0755 fedora_bridge_client.py %{buildroot}%{_bindir}/local-ai-bridge

%files
%license LICENSE
%doc README.md
%{_bindir}/local-ai-bridge

%changelog
* Thu Apr 30 2026 Local AI Maintainer <maintainer@example.com> - 0.1.0-1
- Initial RPM for Fedora COPR client bridge.

