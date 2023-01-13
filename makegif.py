#images/の画像でgifを作成

from PIL import Image
pictures=[]
for i in range(100):
    pic_name='images/image' +str(i+1)+ '.png'
    img = Image.open(pic_name)
    pictures.append(img)
#gifアニメを出力する
pictures[0].save('anime.gif',save_all=True, append_images=pictures[1:],
optimize=True, duration=100, loop=0)
