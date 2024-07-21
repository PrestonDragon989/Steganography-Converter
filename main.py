import os

import sys

import subprocess

from datetime import datetime

import logging
import logging.config

from PIL import Image

specific_file = False

script_dir = os.path.dirname(os.path.abspath(__file__))

def configure_logging() -> logging.RootLogger:
    with open(f"{script_dir}\\log.txt", "r") as log:
        log_length = len(log.read().replace(" ", ""))
    with open(f"{script_dir}\\log.txt", "a") as log:
        log.write(f"{"\n\n" if log_length != 0 else ""}-- LOG STARTED {datetime.now()} --\n")
    
    logging.config.fileConfig(f"{script_dir}\\temp.conf")
                        
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    logger.info("Started Steganography Converter Program")
    
    return logger
    

class Steganography:
    _image_files = {
        ".png",
        ".jpeg",
        ".jpg"
    }
    
    _byte_to_8bit = "08b"
    
    _output_file_extension = ".steg"
    
    def __init__(self, logger: logging.RootLogger):
        self._files = []
        self._opened_files = {}
        
        self._logger = logger
        
    def get_files(self, output=False):
        for file in os.listdir("Input" if not output else "Output"):
            if os.path.splitext(file)[1] in self._image_files:
                self._logger.info(f"Taken in file: {file}")
                self._files.append(file)
            else:
                self._logger.warning(f"The ile: {file} is not in the image format of {self._image_files}, file ignored")
        if len(self._files) <= 0:
            print("No valid files found in Input. Closing.")
            self._logger.critical("No valid files found in Input. Closing program")
            sys.exit()
                
    def open_files(self, output=False) -> None:
        close = False
        for file in self._files:
            try:
                self._opened_files[file] = Image.open("Input/" if not output else "Output/" + file, "r")
                self._logger.info("Opened file {}".format(file))
            except Exception as e:
                self._logger.warning(f"Failed to open file {file}, due to error {e}")
        if len(self._opened_files) <= 0:
            close = True
            
        self._logger.debug(f"Files: {self._files}")
        self._logger.debug(f"Opened Files: {self._opened_files}")
        if close:
            self._logger.critical("Unable to open any files. Ending program")
            sys.exit()
            
    def set_file_to_open(self, file):
        try:
            image = Image.open(file, "r")
            self._opened_files = {file: image}
        except Exception as e:
            self._logger.error(f"Failed to have a set opened {file}, error: {e}")
            
    @property
    def files(self):
        return self._files
        
    @files.setter
    def files(self, value):
        self._files = value
        
    def _gen_data(self, data) -> list[str]:
        # List of binary codes & given data
        newd = []
        
        for i in data:
            newd.append(format(ord(i), self._byte_to_8bit))
        return newd
        
    # Pixels are modified according to the 8-bit binary data and finally returned
    def _mod_pix(self, pix, data):
        datalist = self._gen_data(data)
        lendata = len(datalist)
        imdata = iter(pix)
        
        for i in range(lendata):
            # Extracting 3 pixels at a time
            pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]
                                
            # Pixel value should be made odd for 1 and even for 0
            for j in range(0, 8):
                if (datalist[i][j] == '0' and pix[j]% 2 != 0):
                    pix[j] -= 1
                elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                    if(pix[j] != 0):
                        pix[j] -= 1
                    else:
                        pix[j] += 1
                        
            # Eighth pixel of every set tells whether to stop ot read further.
            # 0 means keep reading; 1 means the message is over.
            if (i == lendata - 1):
                if (pix[-1] % 2 == 0):
                    if(pix[-1] != 0):
                        pix[-1] -= 1
                    else:
                        pix[-1] += 1
                        
            else:
                if (pix[-1] % 2 != 0):
                    pix[-1] -= 1
                    
            pix = tuple(pix)
            yield pix[0:3]
            yield pix[3:6]
            yield pix[6:9]
            
    def _encode_enc(self, newimg, data):
        w = newimg.size[0]
        (x, y) = (0, 0)
        
        for pixel in self._mod_pix(newimg.getdata(), data):
            # Putting modified pixels in the new image
            newimg.putpixel((x, y), pixel)
            if (x == w - 1):
                x = 0
                y += 1
            else:
                x += 1
                
    def main(self) -> None:
        type = input("Welcome to the steganography converter! \n\t1. Encrypt\n\t2. Decrypt\nPlease chose 1 or 2: ").replace(" ", "")
        if type not in ["1", "2"]:
            self._logger.error(f"Input {type} not valid. Must be 1 (encrypt) or 2 (decrypt). Ending Program")
            sys.exit()
            
        # Encryption
        if type == "1":
            data = input("What do you wish to encrypt into the file(s): ").strip()
            if data == "":
                self._logger.error(f"No inputed data to be put into file(s). Shutting down")
                sys.exit()
            
            for file in self._opened_files:
                newimg = self._opened_files[file].copy()
                self._encode_enc(newimg, data)
                
                new_image_name = script_dir + "/Output/" + os.path.splitext(os.path.basename(file))[0] + self._output_file_extension + os.path.splitext(file)[1]
                newimg.save(new_image_name)
                self._logger.info(f"Encryped into {file} | Saved to {new_image_name}")
                
        # Decode
        if type == "2":
            specific_file = False
            for file in self._opened_files:
                image = self._opened_files[file]
                
                data = ''
                imgdata = iter(image.getdata())
             
                while True:
                    pixels = [value for value in imgdata.__next__()[:3] +
                                            imgdata.__next__()[:3] +
                                            imgdata.__next__()[:3]]
                    # string of binary data
                    binstr = ""
                    for i in pixels[:8]:
                        if (i % 2 == 0):
                            binstr += '0'
                        else:
                            binstr += '1'
            
                    data += chr(int(binstr, 2))
                    if (pixels[-1] % 2 != 0):
                        print(f"{file} >> {data}")
                        self._logger.debug(f"Decrypt Data {file} >> {data}")
                        break
            
        self._logger.info("Task complete. Ending program")
        if specific_file:
            path = script_dir + "/Output/"
            os.startfile(path)
        
        
if __name__ == "__main__":
    logger = configure_logging()

    try:
        steganography = Steganography(logger)
        
        if len(sys.argv) <= 1:
            steganography.get_files()
            steganography.open_files()
        else:
            specific_file = True
            steganography.files = sys.argv[1]
            steganography.set_file_to_open(sys.argv[1])
        
        steganography.main()
        
    except Exception as e:
        logger.error(f"Closed program due to error {e}")    
