#!.\venv\Scripts\python.exe
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
import datetime
import time
import configparser #for reading the configuration file
import json #for parsing lists in config file

config = configparser.ConfigParser()
config.read('gdt-importer.conf')
config_devices = configparser.ConfigParser()
config_devices.read('devices.conf')

#set config variables
debug = bool(config['Main']['debug'])
device = config['Main']['device']

font = ImageFont.truetype(config_devices[device]['font'], int(config_devices[device]['font_size']))
path_gdt = Path(config_devices[device]['path_gdt'])
path_image_in = Path(config_devices[device]['path_image_in'])
path_image_out = Path(config_devices[device]['path_image_out'])
path_ignore = Path(config_devices[device]['path_ignore'])
file_gdt = Path(config_devices[device]['file_gdt'])
filename_isynetImport = config_devices[device]['filename_isynetImport']
path_isynetImport = Path(config_devices[device]['path_isynetImport'])
listOfJunkFiles = config_devices[device]["listOfJunkFiles"].replace(" ", "").split(',')


def createIsynetImportFile(imagefile, patid):
    dateOfExam = datetime.date.today().strftime("%d.%m.%y")
    archivenumber = 0
    archiveExists = True
    while archiveExists:
        archivenumber = archivenumber + 1
        try:
           isynetimportfilehandler = open(os.path.join(path_isynetImport, filename_isynetImport + '.' + str(archivenumber).zfill(3)), 'x', encoding='windows-1252')
           archiveExists = False
        except (FileExistsError):
            archiveExists = True
    if debug:
        print('Writing to archive file: ' + os.path.join(path_isynetImport, filename_isynetImport + '.' + str(archivenumber).zfill(3)))
    try:
        isynetimportfilehandler.write('01380006100\n') # unknown purpose
        isynetimportfilehandler.write('014810000138\n') # unknown purpose
        isynetimportfilehandler.write('0176200' + dateOfExam + '\n') #Date of exam DD.MM.YY
        isynetimportfilehandler.write('0143600' + patid + '\n') # PatID
        isynetimportfilehandler.write('0136228SONO\n') # must be "SONO" for importing reasons
        isynetimportfilehandler.write('0676230' + imagefile) # filename of archived image file
        isynetimportfilehandler.close()
    except OSError as e:
        print("Error writing to Archive file: %s : %s" % (archivenumber, e.strerror))

def parseGDT():
        #parse GDT file
    try:
        gdtfile = open(path_gdt / file_gdt, 'r', encoding='windows-1252')
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

    except OSError as e:
        print (e + 'error reading GDT file, using standard values...')
        surname = 'Doe'
        firstname = 'John'
        dob = '01012000'
        patid = '000000'

    return([surname, firstname, dob, patid])


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

    if debug:
        print('Read from GDT file: Surname: ' + surname + ', firstname: ' + firstname + ', DOB: ' + dob + ', PatID: ' + patid)
        
    # format strings according to Samsung naming convertion
    sono_name = (surname + ', ' + firstname)
    sono_dob = dob[:2] + '-' + dob[2:]
    sono_dob = sono_dob[:5] + '-' + sono_dob[5:]

    #create text overlay
    textoverlayImage = Image.new("RGBA", (1232, 924))
    overlayName = ImageDraw.Draw(textoverlayImage)
    overlayName.text((int(config_devices[device]['name_x']), int(config_devices[device]['name_y'])), sono_name, fill='#' + config_devices[device]['font_color'], anchor="lb", font=font)
    overlayDob = ImageDraw.Draw(textoverlayImage)
    overlayDob.text((int(config_devices[device]['dob_x']), int(config_devices[device]['dob_y'])), sono_dob, fill='#' + config_devices[device]['font_color'], anchor="lb", font=font)

    #combine images
    try:   
        sonoImage = Image.open(os.path.join(inpath, filename))
        sonoImage.paste(textoverlayImage, (0, 0), textoverlayImage)
        sonoImage.save(os.path.join(outpath, patid + '-' + filename),"TIFF")
        print ('Imprinted ' + os.path.join(outpath, patid + '-' + filename) + ': ' + sono_name + ' ' + sono_dob)
    except:
        print('Error imprinting image file...')
        return(False)
    
    createIsynetImportFile(os.path.join(outpath, patid + '-' + filename), patid)
    return(True)

while True:
    for subdir, dirs, files in os.walk(path_image_in):
        for imagefile in files:
            if (imagefile.endswith('.Tiff') or imagefile.endswith('.tiff') or imagefile.endswith('.jpg')):
                if imprintImage(str(subdir), imagefile):
                    try:
                        os.remove(os.path.join(subdir, imagefile))
                    except OSError as e:
                        print("Error deleting file: %s : %s" % (imagefile, e.strerror))

                    if (Path(subdir) != path_image_in):
                        try:
                            os.rmdir(subdir)
                        except OSError as e:
                            pass
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
