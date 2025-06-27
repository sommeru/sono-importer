#!.\venv\Scripts\python.exe
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import os
import datetime
import time
import configparser #for reading the configuration file
import json #for parsing lists in config file
from pathlib import Path
base_dir = Path(__file__).parent

config = configparser.ConfigParser()
config.read(base_dir / 'gdt-importer.conf')
#config.read('gdt-importer.conf')
config_devices = configparser.ConfigParser()

#config_devices.read('devices.conf')
config_devices.read(base_dir / 'devices.conf')

#set config variables
debug = config.getboolean('Main', 'debug')
device = config['Main']['device']

font = ImageFont.truetype(base_dir / config_devices[device]['font'], int(config_devices[device]['font_size']))
path_gdt = Path(config_devices['Main']['path_gdt'])
path_image_in = Path(config_devices['Main']['path_image_in'])
path_image_out = Path(config_devices['Main']['path_image_out'])
path_ignore = Path(config_devices['Main']['path_ignore'])
file_gdt = Path(config_devices['Main']['file_gdt'])
listOfJunkFiles = config_devices['Main']["listOfJunkFiles"].replace(" ", "").split(',')

def parseGDT():
    # Default values (placeholders)
    surname = 'Doe'
    firstname = 'John'
    dob = '01012000'
    patid = '000000'

    try:
        gdt_path = path_gdt / file_gdt
        if not gdt_path.exists():
            if debug:
                print(f"GDT file not found: {gdt_path}. Using placeholder values.")
            return [surname, firstname, dob, patid]

        with open(gdt_path, 'r', encoding='windows-1252') as gdtfile:
            for line in gdtfile:
                line = line.strip()
                if line.find('3101') == 3:
                    surname = line[7:]
                elif line.find('3102') == 3:
                    firstname = line[7:]
                elif line.find('3103') == 3:
                    dob = line[7:]
                elif line.find('3000') == 3:
                    patid = line[7:]
            if debug:
                print('Read from GDT file: Surname: ' + surname + ', firstname: ' + firstname + ', DOB: ' + dob + ', PatID: ' + patid)

    except Exception as e:
        print(f"Error reading GDT file: {e}. Using placeholder values.")

    return [surname, firstname, dob, patid]


def imprintImage(inpath, filename):
    #read GDT
    GDTreturn = parseGDT()
    surname = GDTreturn[0]
    firstname = GDTreturn[1] 
    dob = GDTreturn[2]
    patid = GDTreturn[3]
    outpath = os.path.join(path_image_out, datetime.date.today().strftime("%Y-%m-%d"))

    try:
        os.makedirs(outpath)
    except OSError:
        pass
           
    # format strings according to naming convention
    sono_name = (surname + ', ' + firstname)
    sono_dob = dob[:2] + '-' + dob[2:]
    sono_dob = sono_dob[:5] + '-' + sono_dob[5:]

    #create text overlay    
    textoverlayImage = Image.new("RGBA", (int(config_devices[device]['size_x']), int(config_devices[device]['size_y'])), (0, 0, 0, 0))
    overlayName = ImageDraw.Draw(textoverlayImage)
    overlayName.text((int(config_devices[device]['name_x']), int(config_devices[device]['name_y'])), sono_name, fill='#' + config_devices[device]['font_color'], anchor="lb", font=font)
    overlayDob = ImageDraw.Draw(textoverlayImage)
    overlayDob.text((int(config_devices[device]['dob_x']), int(config_devices[device]['dob_y'])), sono_dob, fill='#' + config_devices[device]['font_color'], anchor="lb", font=font)

    #combine images and save as PDF
    try:   
        sonoImage = Image.open(os.path.join(inpath, filename)).convert("RGBA")
        combined = Image.alpha_composite(sonoImage, textoverlayImage)

        # PDF requires RGB mode
        combined_rgb = combined.convert("RGB")

        pdf_filename = os.path.join(outpath, f"{patid}-{surname}_{firstname}.pdf")
        combined_rgb.save(pdf_filename, "PDF", resolution=100.0)

        print ('Created PDF: ' + pdf_filename + ': ' + sono_name + ' ' + sono_dob)

        #Delete GDT after successful imprint
        try:
            #os.remove(path_gdt / file_gdt)
            if debug:
                print(f"GDT-File deleted: {path_gdt / file_gdt}")
        except Exception as e:
            print(f"Error deleting GDT file: {e}")

    except Exception as e:
        print('Error creating PDF file:', e)
        return False
        
    return True

def delete_image_and_parent_folders(path, stop_at):
    """
    Recursively deletes empty directories up to (but not including) 'stop_at'.

    Parameters:
        path (str or Path): The starting folder path (usually where the image was).
        stop_at (str or Path): The root directory beyond which deletion should not proceed.
    """
    try:
        path = Path(path).resolve()
        stop_at = Path(stop_at).resolve()

        if not path.is_dir():
            if debug:
                print(f"Not a directory: {path}")
            return

        if not str(path).startswith(str(stop_at)):
            print(f"Safety check failed: {path} is not under {stop_at}. Aborting folder deletion.")
            return

        while path != stop_at and path != path.parent:
            try:
                path.rmdir()
                if debug:
                    print(f"Deleted empty folder: {path}")
                path = path.parent
            except OSError as e:
                if debug:
                    print(f"Stopping cleanup. Folder not empty or locked: {path} — {e.strerror}")
                break
            except Exception as e:
                print(f"Unexpected error deleting folder {path}: {e}")
                break

    except Exception as e:
        print(f"Critical error in delete_empty_parents(): {e}")


print ('Hello from the happy sono-importer daemon...')
print ('Running in ' + device + ' Mode.')
print ('Waiting for image file to appear in import dir.')

while True:
    for subdir, dirs, files in os.walk(path_image_in):
        for imagefile in files:
            if (imagefile.endswith('.Tiff') or imagefile.endswith('.tiff') or imagefile.endswith('.jpg')):
                if imprintImage(str(subdir), imagefile):
                    try:
                        os.remove(os.path.join(subdir, imagefile))
                    except OSError as e:
                        print("Error deleting file: %s : %s" % (imagefile, e.strerror))

                    delete_image_and_parent_folders(subdir, path_image_in)

            elif (imagefile in listOfJunkFiles):
                print('Identified junk file... Deleting ' + os.path.join(subdir, imagefile))
                try:
                    os.remove(os.path.join(subdir, imagefile))
                except OSError as e:
                    print("Error deleting file: %s : %s" % (imagefile, e.strerror))
            else:
                print ('Found anoher strange file, moving to IGNORE dir: ' + subdir + imagefile)
                try:
                    os.rename(os.path.join(subdir, imagefile), path_ignore / imagefile)
                except OSError as e:
                    print("Error moving file: %s : %s" % (imagefile, e.strerror))
    time.sleep(5)
