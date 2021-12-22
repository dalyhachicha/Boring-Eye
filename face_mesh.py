import cv2
import mediapipe as mp




mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=1,static_image_mode=False,min_detection_confidence=0.5, min_tracking_confidence=0.5)
drawSpec = mpDraw.DrawingSpec(thickness=1, circle_radius=1)


class FaceMeshDetector(object):

    def __init__(self):
        global cap
        cap = cv2.VideoCapture(0)
        
    def __del__(self):
        global cap
        cap.release()
        
        
    def get_frame(self):
        success, img = cap.read()
        # imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # results = faceMesh.process(imgRGB)
        # if results.multi_face_landmarks:
        #     for faceLms in results.multi_face_landmarks:
        #         mpDraw.draw_landmarks(img, faceLms, mpFaceMesh.FACE_CONNECTIONS, drawSpec,drawSpec)
        #         face = []
        #         for id,lm in enumerate(faceLms.landmark):
        #                 #print(lm)
        #                 ih, iw, ic = img.shape
        #                 x,y = int(lm.x*iw), int(lm.y*ih)
        #                 face.append([x,y])
                        
        #     ret, jpeg = cv2.imencode('.jpg', img)
        #     return  jpeg.tobytes()
        
        
        ret, jpeg = cv2.imencode('.jpg', img)
        return  jpeg.tobytes()
    
