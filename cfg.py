##################################################
###### FACES SHIT ################################
##################################################
#FACE SHAPES
square_face = {
    "id" : "0",
    "name" :"Square",
    "good" : "Oval,Aviator,Cateye,Round,Browline,Wayfarer",
    "bad" : "Rectangle,Square,Geometric",
    "celb" : "Angelina Jolie,Jessica Simpson,Brad Pitt,Nick Lachey",
    "desc" : "A square face shape has a strong jaw and a broad forehead, and the width and length of the face have roughly the same proportions. To make a square face look longer and soften its angles, try narrow frame styles, frames that have more width than depth, and narrow ovals.",
    }
round_face = {
    "id" : "1",
   "name" :"Round",
    "good":"Rectangle,Geometric,Square,Aviator",
    "bad" :"Browline,Oval,Wayfarer,Cateye,Round",
    "celb" : "Chrissy Teigen,Mandy Moore,Justin Timberlake,Aaron Paul",
    "desc" : "A round face shape has curved lines with the width and length in the same proportions and no angles. To make a round face appear thinner and longer, try angular narrow eyeglass frames to lengthen the face. Frames with a clear bridge and rectangular frames that are wider than they are deep also can be good choices.",
}
oval_face = {
    "id" : "2",
   "name" :"Oval",
    "good":"Oval,Aviator,Cateye,Round,Browline,Wayfarer,Rectangle,Square,Geometric",
    "bad" : "",
    "celb" : "Jessica Biel,Lucy Liu, Adam Levine,Ben Affleck",
    "desc" : "An oval face shape is considered to be ideal because of its balanced proportions. To maintain the natural balance of an oval face shape, look for eyeglass frames that are as wide as (or wider than) the broadest part of the face. Walnut-shaped frames that are not too deep or narrow are a very good choice.",
    }
oblong_face = {
    "id" : "3",
    "name" :"Oblong",
    "good":"Rectangle,Square,Geometric",
    "bad" :"Wayfarer,Round",
    "celb" : "Gisele Bundchen,Victoria Beckham",
    "desc" : "An oblong face shape is longer than it is wide and has a long, straight cheek line. To make an oblong face appear shorter and more balanced, try frames that have more depth than width. Frames with decorative or contrasting temples also add width to the face.",
}
heart_face = {
    "id" : "4",
    "name" :"Heart",
    "good": "Rectangle,Browline,Cateye,Wayfarer,Oval",
    "bad" : "Round,Square,Aviator,Geometric",
    "celb" : "Kourtney Kardashian,Reese Witherspoon,Chris Hemsworth,Bradley Cooper",
    "desc" : "A heart-shaped face has a wide top third and a narrow bottom third. To reduce the apparent width of the top of the face, choose frame shapes that are wider at the bottom. Thin, light-colored frames and rimless frames that have a light, airy appearance also are good choices.",
}

def good_bad(faces):
    good = []
    bad = []
    for face in faces:
        g = face['good'].split(",")
        b = face['bad'].split(",") 
        good.append(g)
        bad.append(b)
    return good, bad

def get_paths(good, bad):
    good_paths = []
    bad_paths = []
    for g in good:
        good_path = []
        for _g in g:
            good_path.append('faceshape/'+str(_g)+'.png')
        good_paths.append(good_path)
    for b in bad:
        bad_path = []
        for _b in b:
            bad_path.append('faceshape/'+str(_b)+'.png')
        bad_paths.append(bad_path)
    return good_paths, bad_paths


celbs = [square_face['celb'],round_face['celb'],oval_face['celb'],oblong_face['celb'],heart_face['celb']]
descs = [square_face['desc'],round_face['desc'],oval_face['desc'],oblong_face['desc'],heart_face['desc']]
faces = [square_face,round_face,oval_face,oblong_face,heart_face]
faces_paths = ['/faceshape/square_face.png','/faceshape/round_face.png','/faceshape/oval_face.png','/faceshape/oblong_face.png','/faceshape/heart_face.png']
faces_names = ['SQUARE','ROUND','OVAL','OBLONG','HEART']
good_names, bad_names = good_bad(faces)
good_paths, bad_paths = get_paths(good_names,bad_names)


##################################################
############ RANDOM STRING SIZE N  ###############
##################################################

import string 
import random 
def randStr(n,chars = string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(n))