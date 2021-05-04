#!./venv/bin/python3
from PIL import Image, ImageDraw, ImageFont
import os

#set config variables
font = ImageFont.truetype('arial.ttf', 23)
path_gdt = './in'
path_image_in = './in/image'
path_image_out = './out'
path_ignore = './ignore'
file_gdt = 'mcsrparchiv23.gdt'
listOfJunkFiles = ["$RECYCLE.BIN", ".AppleDouble",'.com.apple.timemachine.donotpresent', '.com.apple.timemachine.supported', '.DocumentRevisions-V100', '.dropbox.cache', '.dropbox', '.DS_Store', '.fseventsd', '.LSOverride', '.Spotlight-V100', '.TemporaryItems', '.Trashes', 'Desktop.ini', 'ehthumbs.db', 'Thumbs.db']



def imprintImage(inpath, filename):
    #parse GDT file
    try:
        gdtfile = open(os.path.join(path_gdt, file_gdt), "r", encoding="windows-1252")
        for line in gdtfile:
            line = line.strip()
            if line.startswith('0153101'):
                surname = line.removeprefix('0153101')
            elif line.startswith('0143102'):
                firstname = line.removeprefix('0143102')
            elif line.startswith('0173103'):
                dob = line.removeprefix('0173103')
    except:
        print ('error reading GDT file, using standard values...')
        surname = 'Doe'
        name = 'John'
        dob = '01012000'

    # format strings according to Samsung naming convertion
    sono_name = (surname + ', ' + firstname)
    sono_dob = dob[:2] + '-' + dob[2:]
    sono_dob = sono_dob[:5] + '-' + sono_dob[5:]

    #create text overlay
    textoverlayImage = Image.new("RGBA", (1232, 924))
    overlayName = ImageDraw.Draw(textoverlayImage)
    overlayName.text((393, 27), sono_name, fill="#adadab", anchor="lb", font=font)
    overlayDob = ImageDraw.Draw(textoverlayImage)
    overlayDob.text((666, 52), sono_dob, fill="#adadab", anchor="lb", font=font)

    #combine images
    try:
        sonoImage = Image.open(os.path.join(inpath, filename))
        sonoImage.paste(textoverlayImage, (0, 0), textoverlayImage)
        sonoImage.save(os.path.join(path_image_out, filename),"TIFF")
        print ('Imprinted ' + filename + ': ' + sono_name + ' ' + sono_dob)
        return(True)
    except:
        print('Error imprinting image file...')
        return(False)

for subdir, dirs, files in os.walk(path_image_in):
    for imagefile in files:
        if (imagefile.endswith('.Tiff') or imagefile.endswith('.tiff')):
            if imprintImage(subdir, imagefile):
                try:
                    os.remove(os.path.join(subdir, imagefile))
                except OSError as e:
                    print("Error deleting file: %s : %s" % (imagefile, e.strerror))

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
            print ('Found antoher strange file, moving to IGNORE dir: ' + subdir + imagefile)
            try:
                os.rename(os.path.join(subdir, imagefile), os.path.join(path_ignore, imagefile))
            except OSError as e:
                print("Error moving file: %s : %s" % (imagefile, e.strerror))
                
            
                
            
        
        
