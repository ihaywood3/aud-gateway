# -*- encoding: utf-8 -*-

def text_to_number(text):
    if type(text) is not bytes:
        text = bytes(text,'ascii')
    return "".join("{:02}".format(i-32) for i in text)

def number_to_text(num):
     return "".join(chr(int(num[i:i+2])+32) for i in range(0, len(num), 2))

print(text_to_number("ℵℶℷ"))


