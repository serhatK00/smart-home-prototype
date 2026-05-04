# smart-home-prototype
Smart home project with web and desktop control panels at prototype level
A three-layer home automation prototype I built to control household devices
from a single interface. At its core are two independent control panels that
stay in sync at all times: a local Python desktop panel and a browser-based
C# web panel. Any change made on one is immediately reflected on the other.
 Two panels, one source of truth

The main design decision behind this project was simple: the system should
work regardless of network availability.
**Python Panel (local desktop)**
Runs directly on the host machine alongside the Python server. No network
required — if the machine is on, the panel is accessible.

**C# Web Panel (browser-based)**
Accessible from any device on the same network — phone, tablet, another
computer — without installing anything. Protected by a login screen with
username and password authentication.

Both panels read from and write to the same central state managed by the
Python service. Turning off a device from one panel is instantly visible
on the other.
```
┌─────────────────────┐        ┌─────────────────────┐
│   Python Panel      │        │    C# Web Panel     │
│  (local · offline)  │        │  (browser · LAN)    │
│                     │        │   [login screen 🔒] │
└────────┬────────────┘        └──────────┬──────────┘
         │  read / write                  │  read / write
         └──────────────┬─────────────────┘
                        ▼
              ┌─────────────────┐
              │  Python API     │
              │  Central State  │
              └────────┬────────┘
                       │  serial (COM11)
                       ▼
              ┌─────────────────┐
              │    Arduino      │
              │ Hardware layer  │
              └─────────────────┘
```

---
## Quick start

Connect the Arduino to COM11, then run:

```bash
RunHomeSystem.bat
```

This single command starts both the Python server and the C# web server
simultaneously. The Python panel launches automatically. For the web panel,
enter the IP address shown in the console output into any browser and log in
with your credentials.

---

## Architecture

| Layer           | Technology                      | Role                           |
|-----------------|---------------------------------|--------------------------------|
| Hardware        | Arduino (C++), UART serial      | Sensor reading, command output |
| Orchestration   | Python, REST API                | State management, core logic   |
| Local panel     | Python (desktop UI)             | Offline control                |
| Web panel       | C# · .NET 10 · ASP.NET Core MVC | Authenticated browser access   |
| Automation      | Windows Batch (.bat)            | One-click startup              |

---

## Security

The web panel is protected by username and password authentication —
knowing the URL alone is not enough to gain access.

The Python panel runs only on the host machine and is not exposed over
the network, so no additional access control is needed on that side.

---

## Known limitations / to-do

- [ ] Dynamic COM port configuration
- [ ] HTTPS support
- [ ] Cross-platform support (currently Windows only)
