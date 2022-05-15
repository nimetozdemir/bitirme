import subprocess
import cv2
rtmp_url = "rtmp://213.226.117.171:1935/hypegenai/CAM1"

# In my mac webcamera is 0, also you can set a video file name instead, for example "/home/user/demo.mp4"
# path = rtmp://213.226.117.171:1935/hypegenai/CAM1
cap = cv2.VideoCapture(rtmp_url)

# fps = int(cap.get(cv2.CAP_PROP_FPS))
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# command = ['./ffmpeg.exe',
#            '-y',
#            '-f', 'rawvideo',
#            '-vcodec', 'rawvideo',
#            '-pix_fmt', 'bgr24',
#            '-s', "{}x{}".format(width, height),
#            '-r', str(fps),
#            '-i', '-',
#            '-c:v', 'libx264',
#            '-pix_fmt', 'yuv420p',
#            '-preset', 'ultrafast',
#            '-f', 'flv',
#            rtmp_url]

# # using subprocess and pipe to fetch frame data
# p = subprocess.Popen(command, stdin=subprocess.PIPE)


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("frame read failed")
        break


    cv2.imshow('camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # p.stdin.write(frame.tobytes())