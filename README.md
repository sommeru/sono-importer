# 🩺 Sono-Importer - A GDT Image Imprinter & PDF Export Tool

A Python utility that overlays patient metadata from GDT (Gerätedatenträger) files onto medical images (e.g. ultrasound scans) and exports them as PDFs for archiving or further processing. Built with PIL (Pillow) and designed for integration with ISYNET or similar workflows.

---

## 🚀 Features

- 🖼️ Processes `.jpg` and `.tiff` image files
- 📄 Parses GDT files for name, DOB, and patient ID
- ✍️ Overlays patient data on images using configurable fonts
- 📤 Exports annotated images as PDFs into date-based output folders
- 🧹 Automatically deletes processed images, GDT files, and their subfolders
- 🔁 Runs continuously and monitors an input directory

---

## 📦 Installation Options

### Install with Poetry

1. **Install Poetry**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone the repository**:
   ```bash
   git clone git@github.com:sommeru/sono-importer.git
   cd sono-importer
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Run the tool**:
   ```bash
   poetry run python sono-importer.py
   ```

---

## ▶️ How It Works

1. GDT metadata is parsed (`3101`: surname, `3102`: firstname, `3103`: DOB, `3000`: patient ID)
2. Each incoming image is overlaid with patient info at specified coordinates
3. A PDF is created in `path_image_out/YYYY-MM-DD/`
4. The image file, its GDT file, and its parent folders are deleted if empty

---

## 🧪 Folder Structure Example

```
gdt-image-imprinter/
├── main.py
├── gdt-importer.conf
├── devices.conf
├── fonts/
│   └── Arial.ttf
├── inbox/
├── outbox/
├── ignored/
├── gdt/
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## 🍎 Packaging for macOS

You can create a standalone `.app` for macOS using **pyinstaller**:

1. Install:
   ```bash
   . .venv/bin/activate
   pip install pyinstaller
   ```

2. Build:
   ```bash   
   pyinstaller \
     --onefile \
     --add-data "gdt-importer.conf:." \
     --add-data "devices.conf:." \
     --add-data "arial.ttf:." \
     --add-data "arial-bold.ttf:." \
     sono-importer.py 
   ```

3. Run:
Just doubleclick!

---

## 🔐 Notes & Limitations

- Assumes single-use GDT file per image. If you reuse GDT for multiple files, handle deletion externally.
- Images must have correct dimensions or overlay may misalign.
- UTF-8 characters (e.g. umlauts) in names require compatible fonts.

---

## 📄 License

GNU License — free to use, modify, and redistribute.

---

## 🙋‍♀️ Contributing

Pull requests and feature suggestions are welcome! Areas to improve:

- Multi-language GDT field support
- DICOM compatibility
- GUI frontend for drag & drop

---

## 📬 Contact

For questions or support, feel free to reach out via GitHub Issues or email the maintainer.
