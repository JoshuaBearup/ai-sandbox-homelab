# Development Helper Scripts

Easy commands to manage your local development environment.

## Quick Reference

### Windows
```cmd
dev.bat start    # Start PostgreSQL
dev.bat app1     # Run app1
dev.bat stop     # Stop PostgreSQL
```

### Mac/Linux
```bash
./dev.sh start   # Start PostgreSQL
./dev.sh app1    # Run app1
./dev.sh stop    # Stop PostgreSQL
```

---

## Main Development Script

Located at project root: `dev.bat` (Windows) or `dev.sh` (Mac/Linux)

### Commands

| Command | Description |
|---------|-------------|
| `start` | Start PostgreSQL database |
| `stop` | Stop PostgreSQL database |
| `restart` | Restart PostgreSQL database |
| `status` | Check what's running |
| `logs` | View PostgreSQL logs (live) |
| `clean` | Stop and **DELETE ALL DATA** |
| `app1` | Run app1 (localhost only) |

### Examples

**Start Development Environment:**
```bash
# Windows
dev.bat start

# Mac/Linux
./dev.sh start
```

**Run App1:**
```bash
# Windows
dev.bat app1

# Mac/Linux
./dev.sh app1
```

Then open: http://localhost:8501

**Check Status:**
```bash
# Windows
dev.bat status

# Mac/Linux
./dev.sh status
```

**View Database Logs:**
```bash
# Windows
dev.bat logs

# Mac/Linux
./dev.sh logs
```

**Stop Everything:**
```bash
# Windows
dev.bat stop

# Mac/Linux
./dev.sh stop
```

**Clean (Delete All Data):**
```bash
# Windows
dev.bat clean

# Mac/Linux
./dev.sh clean
```

---

## Per-App Scripts

Each app has its own run scripts in `streamlit_apps/appN/`:

### Windows: `run.bat`
```cmd
cd streamlit_apps\app1
run.bat
```

### Mac/Linux: `run.sh`
```bash
cd streamlit_apps/app1
./run.sh
```

Both run the app on **localhost only** (not publicly accessible).

---

## Typical Workflow

### First Time Setup

1. **Start database:**
   ```bash
   dev.bat start        # Windows
   ./dev.sh start       # Mac/Linux
   ```

2. **Wait 10 seconds** for PostgreSQL to initialize

3. **Run app:**
   ```bash
   dev.bat app1         # Windows
   ./dev.sh app1        # Mac/Linux
   ```

4. **Open browser:** http://localhost:8501

### Daily Development

Database stays running across sessions:

```bash
# Just run the app
dev.bat app1         # Windows
./dev.sh app1        # Mac/Linux
```

Press `Ctrl+C` to stop the app when done.

### Shutting Down

```bash
# Stop database (optional - can leave running)
dev.bat stop         # Windows
./dev.sh stop        # Mac/Linux
```

---

## Troubleshooting

### Port Already in Use

**Symptom:** "Port 8501 already in use"

**Solution:**
```bash
# Windows
taskkill //F //IM python.exe

# Mac/Linux
pkill -f streamlit
```

### Database Connection Failed

**Check if running:**
```bash
dev.bat status       # Windows
./dev.sh status      # Mac/Linux
```

**Restart:**
```bash
dev.bat restart      # Windows
./dev.sh restart     # Mac/Linux
```

### Fresh Start (Nuclear Option)

**WARNING: Deletes all data!**
```bash
# Stop everything and delete data
dev.bat clean        # Windows
./dev.sh clean       # Mac/Linux

# Start fresh
dev.bat start        # Windows
./dev.sh start       # Mac/Linux
```

---

## Advanced Usage

### Run Multiple Apps

Each app runs on the same port (8501), so you can only run one at a time.

To run different apps:
```bash
# Stop current app (Ctrl+C)

# Run different app
cd streamlit_apps/app2
./run.sh            # or run.bat on Windows
```

### Custom Streamlit Options

Edit `run.bat` or `run.sh` in the app directory:

```bash
# Example: Change port
python -m streamlit run streamlit_main.py \
    --server.address=localhost \
    --server.port=8502 \
    --server.headless=true
```

### PostgreSQL with pgAdmin

Start with web UI:
```bash
# Windows
docker-compose -f docker-compose.local.yml --profile tools up -d

# Mac/Linux
docker-compose -f docker-compose.local.yml --profile tools up -d
```

Access pgAdmin at: http://localhost:5050
- Email: `admin@localhost.com`
- Password: `admin`

---

## What These Scripts Do

### Security
- ✅ Apps run on **localhost only** (not publicly accessible)
- ✅ Database is containerized (isolated)
- ✅ Safe for local development

### Convenience
- ✅ No need to remember long commands
- ✅ Consistent across Windows/Mac/Linux
- ✅ Clear error messages
- ✅ Confirmation before destructive operations

---

## Quick Command Cheat Sheet

```bash
# === START DEVELOPMENT ===
dev start              # Start PostgreSQL
dev app1               # Run app1 → http://localhost:8501

# === CHECK STATUS ===
dev status             # What's running?
dev logs               # View database logs

# === STOP ===
Ctrl+C                 # Stop app
dev stop               # Stop database

# === CLEAN UP ===
dev clean              # Delete everything (asks for confirmation)
```

---

## See Also

- [QUICKSTART.md](QUICKSTART.md) - First-time setup guide
- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Complete development guide
- [CURRENT_STATUS.md](CURRENT_STATUS.md) - Project status
