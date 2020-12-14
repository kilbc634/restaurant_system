import subprocess
import os
import time

def set_camera():
  print("geting wlan0 IP address.......")

  #subprocess.getoutput("sudo rm -rf /home/pi/Desktop/test_Log.txt")
  #file_t = open("/home/pi/Desktop/test_Log.txt" ,'w+')
  #file_t.write("test strat")
  #file_t.close()

  ip_str = subprocess.getoutput("ifconfig wlan0 | grep 'inet ' | awk -F ' ' '{print $2}' | awk '{print $1}'")  #取得ip
  failed_count = 0
  while(failed_count < 10):
    if(len(ip_str) >= 7):
      print("geting complete , your wlan0 IP address is '%s'" % ip_str)
      failed_count = 10
    else:
      print("Error: IP address geting failed")
      failed_count += 1
      time.sleep(5)
    
  print("replace idnex.html.......")

  path = '/usr/local/nginx/html/rtmp_app/'
  file_name = 'camera.html'

  subprocess.getoutput("sudo rm -rf " + path + file_name) #刪除原本的檔案

  file = open(path + file_name,'w+')
  text_code = '''
  <!DOCTYPE html>
  <html lang="en">
  <head>

      <title>Video.js | HTML5 Video Player</title>
      <!-- <link href="video-js-6.2.0/video-js.css" rel="stylesheet">
      <script src="video-js-6.2.0/videojs-ie8.min.js"></script> -->

      <link href="http://vjs.zencdn.net/5.20.1/video-js.css" rel="stylesheet">
      <script src="http://vjs.zencdn.net/5.20.1/video.js"></script>
      
  </head>
  <body>

    <video id="example_video_1" class="video-js vjs-default-skin" controls preload="auto" width="1280" height="720" poster="http://vjs.zencdn.net/v/oceans.png" data-setup="{}">
      <!-- <source src="1.mp4" type="video/mp4"> -->
      <source src="rtmp://''' + ip_str + '''/live/test" type="rtmp/flv">
      
      <p class="vjs-no-js">To view this video please enable JavaScript, and consider upgrading to a web browser that <a href="http://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a></p>
    </video>
    
    <script src="http://vjs.zencdn.net/5.20.1/video.js"></script>
  </body>

  </html>
  '''
  file.write(text_code)
  file.close()
  print("replace complete , creat new file '%s' in '%s'" % (file_name , path + file_name))

  print("nginx server restart in /usr/local/nginx/sbin/nginx")
  subprocess.getoutput("sudo /usr/local/nginx/sbin/nginx -s stop")
  subprocess.getoutput("sudo /usr/local/nginx/sbin/nginx")

  print("RTMP Streaming ready......")
  subprocess.getoutput("gst-launch-1.0 -v v4l2src ! 'video/x-raw, width=640, height=480, framerate=30/1' ! queue ! videoconvert ! omxh264enc !  h264parse ! flvmux ! rtmpsink location='rtmp://" + ip_str + "/live/test live=1'")
	
