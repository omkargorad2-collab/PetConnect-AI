PetConnect AI — Flask prototype
Features
Stylish responsive website for phone and desktop
Adoption, lost, found, and owner listings stored in SQLite
Three preloaded demo animals
Camera capture / photo upload (mobile browsers may show camera or gallery)
Real pretrained ViT image-classification model with top-five predictions
Run
Use Python 3.10–3.12 on a laptop or cloud Linux host. AI dependencies (Torch) can be difficult to install on Android/Pydroid3.
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
Open http://127.0.0.1:5000 in the browser on the computer running the server. To access from a phone on the same Wi-Fi, use http://COMPUTER_LAN_IP:5000 and ensure the firewall allows port 5000. Browser camera capture works most reliably on HTTPS or localhost; use gallery upload if camera access is blocked.
AI limitations
The google/vit-base-patch16-224 model predicts ImageNet visual labels, not verified animal species/breeds or ages. Some outputs may be inaccurate. It does not estimate exact age, health, vaccination status, or recognize an individual lost pet. The first scan downloads model files from Hugging Face and needs internet; later scans can use the local cache. It may require significant RAM/storage.
Prototype safety / production TODO
This is a classroom prototype, not a production service. No accounts, identity checks, seller verification, listing moderation, ownership verification, matching of lost and found animals, private contact relay, or adoption workflows are implemented. Listing contacts are publicly displayed. Use fictional data for demos. Before public deployment, add authentication, moderation, privacy controls, secure storage, abuse prevention, and appropriate animal welfare protections. Set SECRET_KEY in the environment. Do not run Flask's development server publicly in production.
