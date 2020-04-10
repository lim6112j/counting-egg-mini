#-*- coding: utf-8 -*-
# this is test version
import sqlite3
import psycopg2
import numpy as np
import cv2
import time
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer
# from matplotlib import pyplot as plt
import threading
class blob:
    tolerance = 15
    # false_tolerance =1
    def __init__(self):
        self.number=0
        self.Counted = False
        self.X=0
        self.Y=0
        self.Crossed_Line=False
        self.NoiseDetect = 0
    def setNoiseDetect(self, NoiseDetect):  # 크로스 라인을 두번 넘어야 카운트 되게 하는 변수, 노이즈를 감소시킴(계란 없이 컨베이어 운행시)
        self.NoiseDetect = NoiseDetect
    def setCounted(self, counted):
        self.Counted=counted
    def setNumber(self, number):
        self.number=number
    def setContour(self, cnt):
        self.contour=cnt
    def setCenter(self, x, y):
        self.X=x
        self.Y=y
    def matchContour(self, x,y):
        # 정지 화면에서 가짜 오브젝트가 세지는걸 막기위해 만들어짐.. 테스트 안됨.
        # if(x-blob.tolerance<self.X and self.X<x+blob.tolerance and y-blob.tolerance<self.Y and self.Y<y+blob.tolerance and not
        #         (x-blob.false_tolerance<self.X and self.X<x+blob.false_tolerance and y-blob.false_tolerance<self.Y and self.Y<y+blob.false_tolerance)):
        if(x-blob.tolerance<self.X and self.X<x+blob.tolerance and y-blob.tolerance<self.Y and self.Y<y+blob.tolerance ):
            return True
        else:
            return False
class CountingEggs(threading.Thread):
    def __init__(self, threadID, name,video_url):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.video_url=video_url
        self.doRun = True
    def setDoRun(self):
        self.doRun = False
    def radial_distortion(self,img):
        # try:
        #     print 'testing'
        # except Exception as e:
        #     print e
        K = np.array([[  400,     0.  ,  img.shape[1]/2],
                      [    0.  ,  300,   img.shape[0]/2],
                      [    0.  ,     0.  ,     1.  ]])

        # zero distortion coefficients work well for this image
        D = np.array([0., 0., 0., 0.])
        #2592.1944
        # use Knew to scale the output
        Knew = K.copy()
        Knew[(0,1), (0,1)] = 0.8 * Knew[(0,1), (0,1)]


        # img_original = cv2.imread(img)
        img_undistorted = cv2.fisheye.undistortImage(img, K, D=D, Knew=Knew)
        return img_undistorted
    def run(self):
        # cap=cv2.VideoCapture('images/eggs3.mp4')
        # cap=cv2.VideoCapture('rtsp://admin:cctv9233!@rainboweggs.iptime.org:552/Streaming/Channels/101')
        cap=cv2.VideoCapture(self.video_url)
        capret,frame = cap.read()
        previous_frame = frame
        contour_prev=[]
        contour_cur=[]
        centerlineX=0
        centerlineY=0
        egg_count=0
        crossing_count=0
        crossing_tolerrance=15
        checkLightDelay =100
        initThresholdLightLow=160
        threaholdLightLow=initThresholdLightLow
        Brightness =120
        BrightnessModifier = 20
        diffvaluelist=[]
        difflistmean=0
        difflistmeandefault=40
        elapsed_starttime=0
        elapsed_stoppedtime=0
        start_delta=0
        stop_delta=0
        beforetime=time.time()
        starttime =time.time()
        writeDB=60
        writeDBRemote=120
        crop_img_x = 0
        crop_img_y=0
        crop_img_w=0
        crop_img_h=0
        window_moved = False
        conn = sqlite3.connect("RainbowFarm.db")
        dsn_database = "rainbowDB"           
        dsn_hostname = "someRDS.amazonaws.com" 
        dsn_port = "5432"             
        dsn_uid = "eggcounter"    
        dsn_pwd = "P@ssword"    
        conn_string = "host="+dsn_hostname+" port="+dsn_port+" dbname="+dsn_database+" user="+dsn_uid+" password="+dsn_pwd
        try:
            conn2=psycopg2.connect(conn_string)
        except Exception:
            print "Unable to connect to the database."
        while(cap.isOpened() and self.doRun == True):
            checkLightDelay-=1
            meanvalue=120
            # time.sleep(0.0)
            if(capret):
                img=cv2.resize(frame,None,fx=1,fy=0.75,interpolation=cv2.INTER_AREA)
                # img=frame

                image=img
                # cv2.imshow('original',img)
                # print img.shape[:2]

                crop_img_x = img.shape[1]*0/40
                crop_img_y = img.shape[0]*2/6
                # if(self.name == '7-Dong'):
                #     crop_img_w = img.shape[1]*19/20
                # else:
                #     crop_img_w = img.shape[1]*20/20
                crop_img_w = img.shape[1]*20/20
                crop_img_h = img.shape[0]*3/6
                img = img[crop_img_y:crop_img_h, crop_img_x:crop_img_w] # Crop from x, y, w, h -> 100, 200, 300, 400
                if( self.name == '1-Dong'):
                    img = self.radial_distortion(img)

                #  its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
                # cv2.imshow('img',img)
                # img=crop_img
                centerlineY=img.shape[0]/2
                cv2.line(img, (0,centerlineY), (img.shape[1],centerlineY), (0,255,0), 5)
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                diffvalue=0

                if (previous_frame is not None) & (frame is not None):
                    diffframe=cv2.absdiff(frame,previous_frame)
                    diffimgmean=cv2.mean(diffframe)
                    diffvalue=diffimgmean[0]+diffimgmean[1]+diffimgmean[2]
                    try:
                        # print len(diffvaluelist)
                        # print 'moving?? :',difflistmean
                        if(len(diffvaluelist)==10):
                            diffvaluelist.pop()
                        diffvaluelist.insert(0,diffvalue)
                        difflistmean = sum(diffvaluelist)/len(diffvaluelist)
                    except IOError as e:
                        print e
                if checkLightDelay<0:
                    meanvalue=cv2.mean(gray)
                    if meanvalue is not None:
                        Brightness=int(round( meanvalue[0],1))
                        if(Brightness < 50):
                            crossing_count = 0
                            egg_count_num_dic[self.name]=0
                            elapsed_starttime = 0
                            elapsed_stoppedtime = 0
                            # try:
                            #     print 'resetting counting'
                            # except Exception as e:
                            #     print e
                        # try:
                        #     print meanvalue[0]
                        # except IOError as e:
                        #     print e.errno

                    checkLightDelay=100
                if(difflistmean<=difflistmeandefault):
                    start_delta=0
                    stop_delta = time.time()-beforetime
                else:
                    stop_delta=0
                    start_delta = time.time()-beforetime
                elapsed_starttime += start_delta
                elapsed_stoppedtime += stop_delta
                beforetime=time.time()
                if(self.name =='1-Dong'):
                    BrightnessModifier = 0
                ret, thresh = cv2.threshold(gray,Brightness+BrightnessModifier,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #화면의 평균 밝기 Brightness+10 이상을 필터링
                # cv2.imshow('thresh',thresh)

                # noise removal
                kernel = np.ones((3,3),np.uint8)
                opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
                # cv2.imshow('open',opening)

                # sure background area
                sure_bg = cv2.dilate(opening,kernel,iterations=3)
                # cv2.imshow('dialte',sure_bg)

                # Finding sure foreground area
                dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,3)
                ret, sure_fg = cv2.threshold(dist_transform,0.5*dist_transform.max(),255,0)
                # cv2.imshow('dist_transform',sure_fg)

                # Finding unknown region
                sure_fg = np.uint8(sure_fg)
                _,contours,_= cv2.findContours(sure_fg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                contour_list = []
                for contour in contours:
                    approx = cv2.approxPolyDP(contour,0.009*cv2.arcLength(contour,True),True)
                    area = cv2.contourArea(contour)
                    arcLength=cv2.arcLength(contour,True)
                    if ((len(approx) > 4) & (area>160) & (arcLength<160)):   #길다란 노이즈 삭제를 위해 arcLength 도입
                        currentBlob=blob() # 신규 object 생성
                        matched=False
                        M = cv2.moments(contour)
                        if M['m00']!=0:
                            cy = int(M['m01']/M['m00'])
                            cx = int(M['m10']/M['m00'])
                        for prev_blob in contour_prev:
                            if(prev_blob.matchContour(cx,cy)): # 현재 컨투어가 이전  컨투어 리스트에 존재하는가?
                                currentBlob=prev_blob
                                currentBlob.setCenter(cx,cy)
                                matched=True
                                # print 'matched'
                                break
                            # else:
                                # print "not matched"
                        if(matched==False):
                            currentBlob.setContour(contour)
                            currentBlob.setCenter(cx,cy)
                        contour_list.append(currentBlob)
                        ellipse = cv2.fitEllipse(contour)
                        cv2.ellipse(img,ellipse,(0,255,0),2)
                        # print 'current contour\'s Area :'+str(area)
                # print 'number of contours'+str(len(contour_list))
                # for cnt in contour_prev:
                # print 'controur_prev number ; '+ str(len(contour_prev))
                # print 'contour_list number :'+str(len(contour_list))
                for blb in contour_list:

                    if ((difflistmean>difflistmeandefault)&(blb.Y<centerlineY+crossing_tolerrance) & (blb.Y>centerlineY-crossing_tolerrance) & (blb.Crossed_Line == False)):
                        blb.NoiseDetect +=1
                        if(blb.NoiseDetect ==3):
                            crossing_count += 1
                            blb.Crossed_Line=True
                            if(blb.Counted == False):
                                egg_count += 1
                                blb.setNumber(egg_count)
                                blb.Counted=True
                    # print 'egg crossed line'
                    # cv2.putText(img, str(blb.number),(blb.X-7,blb.Y+5),cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,255), 2)
                    if(blb.number != 0):
                        cv2.putText(img, 'R',(blb.X-7,blb.Y+5),cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,255), 2)
                cv2.putText(image, str(crossing_count), (0,img.shape[0]/2+10), cv2.FONT_HERSHEY_COMPLEX, 2, (100,170,0), 3)
                cv2.putText(image, str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),(20,image.shape[0]/30*28), cv2.FONT_HERSHEY_COMPLEX, 1, (100,170,0), 3)
                m, s = divmod(elapsed_starttime, 60)
                h, m = divmod(m, 60)
                cv2.putText(image, "Running Time :"+"%d:%02d:%02d" % (h, m, s),(20,image.shape[0]/30*23), cv2.FONT_HERSHEY_COMPLEX, 0.5, (100,170,0), 1)
                m, s = divmod(elapsed_stoppedtime, 60)
                h, m = divmod(m, 60)
                cv2.putText(image, "Stopped Time :"+"%d:%02d:%02d" % (h, m, s),(20,image.shape[0]/30*25), cv2.FONT_HERSHEY_COMPLEX, 0.5, (100,170,0), 1)
                # cv2.drawContours(image, contour_list, -1, (0,255,0),3)
                # cv2.imshow('contour',img)


                unknown = cv2.subtract(sure_bg,sure_fg)
                # Marker labelling
                ret, markers = cv2.connectedComponents(sure_fg)
                # print np.amax(markers)
                # Add one to all labels so that sure background is not 0, but 1
                markers = markers+1

                # Now, mark the region of unknown with zero
                markers[unknown==255] = 0
                markers = cv2.watershed(img,markers)
                img[markers == -1] = [255,0,0]
                # cv2.imshow('crop_image',img)
                # cv2.imshow('unknown',unknown)
                cv2.namedWindow(self.name)
                if(window_moved == False):
                    # cv2.resizeWindow(self.name, 400,300)
                    window_moved = True
                    if(self.name == '1-Dong'):
                        cv2.moveWindow(self.name, 0,0)
                    elif(self.name == '2-Dong'):
                        cv2.moveWindow(self.name, 640,0)
                    elif(self.name == '3-Dong'):
                        cv2.moveWindow(self.name, 1280,0)
                    elif(self.name == '4-Dong'):
                        cv2.moveWindow(self.name, 0,360)
                    elif(self.name == '5-Dong'):
                        cv2.moveWindow(self.name, 640,360)
                    elif(self.name == '6-Dong'):
                        cv2.moveWindow(self.name, 1280, 360)
                    elif(self.name == '7-Dong'):
                        cv2.moveWindow(self.name, 0,720)
                if(  self.name == '1-Dong'):
                    image[crop_img_y:crop_img_h, crop_img_x:crop_img_w] = img
                # image = cv2.resize(image,None,fx=.5,fy=0.5,interpolation=cv2.INTER_AREA)
                cv2.imshow(self.name,image)
                contour_prev=contour_list
                k = cv2.waitKey(25) & 0xFF
                if k == 27:
                    break
                if(frame is not None):
                    previous_frame=frame.copy()
            capret=cap.grab()
            # db update
            if(capret):
                if(egg_count_num_dic[self.name] >= crossing_count):
                    crossing_count= egg_count_num_dic[self.name]
                else:
                    egg_count_num_dic[self.name]=crossing_count
                m, s = divmod(time.time()-starttime, 60)

                if( int(s) % 10 == int(self.name[0])):
                    writeDBRemote -= 1
                    if(writeDBRemote == 0):
                        writeDBRemote = 120
                        with conn2:
                            cur = conn2.cursor()
                            sql = """insert into eggcnt (c_dong,c_count) values (%s, %s)"""
                            cur.execute(sql,(self.name, crossing_count))
                if( int(s) % 10 == int(self.name[0])):
                    writeDB -= 1
                    if(writeDB == 0):
                        writeDB = 60
                        # try:
                        #     print '\n',self.name,' count: ',crossing_count
                        # except Exception as e:
                        #     print 'print error',e
                        #reset at 23:59:59
                        now = datetime.now()
                        nowTime = now.strftime('%H:%M')
                        if(nowTime == '00:00'):
                            egg_count_num_dic[self.name]=0
                            crossing_count=0
                            
                        with conn:
                            cur = conn.cursor()
                            sql = """insert into eggcount (name,eggnum) values (?, ?)"""
                            cur.execute(sql,(self.name, crossing_count))
                            # end of db update
                ret, frame = cap.retrieve()
            else:
                print "\nolost frame :",self.name
                cap.release()
                cv2.destroyWindow(self.name)
                break
        cap.release()
        cv2.destroyWindow(self.name)
def getInput(L):
    input = raw_input("Enter to close")
    L.append(input)
if __name__ == "__main__":
    # rtspList=[
    # 'rtsp://admin:p@assword.168.0.101:554/Streaming/Channels/102',
    # 'rtsp://admin:p@assword.168.0.102:552/Streaming/Channels/102',
    # 'rtsp://admin:p@assword.168.0.103:553/Streaming/Channels/102',
    # 'rtsp://admin:p@assword.168.0.104:550/Streaming/Channels/102',
    # 'rtsp://admin:p@assword.168.0.105:555/Streaming/Channels/102',
    # 'rtsp://admin:p@assword.168.0.106:556/Streaming/Channels/102',
    # 'rtsp://admin:p@assword.168.0.107:557/Streaming/Channels/102'
    # ]

    rtspList=[
    'http://admin:p@assword.168.0.101:80/Streaming/Channels/102/httppreview',
    'http://admin:p@assword.168.0.102:82/Streaming/Channels/102/httppreview',
    'http://admin:p@assword.168.0.103:83/Streaming/Channels/102/httppreview',
    'http://admin:p@assword.168.0.104:84/Streaming/Channels/102/httppreview',
    'http://admin:p@assword.168.0.105:85/Streaming/Channels/102/httppreview',
    'http://admin:p@assword.168.0.106:86/Streaming/Channels/102/httppreview',
    'http://admin:p@assword.168.0.107:87/Streaming/Channels/102/httppreview'
    ]
    i=0
    threads={}
    egg_count_num_dic = {}
    rows=[]
    hasmember=False
    conn = sqlite3.connect("RainbowFarm.db")
    with conn:
        cur = conn.cursor()
        cur.execute("select name, eggnum,max(dt) from eggcount  where dt > datetime('now','-5 minutes') group by name")
        # cur.execute("INSERT INTO eggcount (name, eggnum) VALUES ('TEST2', 11)")
        rows = cur.fetchall()
    if len(rows) ==0:
        print 'rows has 0 member'
    else:
        print 'rows has members'
        hasmember=True

    for rtspStr in rtspList:
        dongname=''
        # for 로켤 아이피
        # portnum = rtspStr[37:40]
        # for 외부 rtsp 아이피, 주소
        # portnum = rtspStr[47:50]
        # for 내부 http 아이피, 주소
        portnum = rtspStr[37:39]
        # for 외부 http 아이피, 주소
        # portnum = rtspStr[47:49]
        # print portnum
        if(portnum == '554' or portnum == '80'):
            dongname = '1-Dong'
        elif(portnum == '552'  or portnum == '82'):
            dongname = '2-Dong'
        elif(portnum =='553'  or portnum == '83'):
            dongname = '3-Dong'
        elif(portnum == '550'  or portnum == '84'):
            dongname = '4-Dong'
        elif(portnum == '555' or portnum == '85'):
            dongname = '5-Dong'
        elif(portnum =='556'  or portnum == '86'):
            dongname = '6-Dong'
        elif(portnum =='557' or portnum == '87'):
            dongname = '7-Dong'
        else:
            dongname = 'unknown'

        egg_count_num_dic[dongname]=0
        if(hasmember == True):
            for row in rows:
                if(row[0]==dongname):
                    egg_count_num_dic[dongname]=row[1]
        try:
            print 'Starting : ',dongname
        except Exception:
            print 'starting string error'

        threads["Thread{0}{1}{2}{3}{4}".format(i,':', dongname,':', rtspStr)] = CountingEggs(i,dongname, rtspStr)
        # threads["Thread{0}".format(portnum)].daemon = True
        threads["Thread{0}{1}{2}{3}{4}".format(i,':', dongname,':', rtspStr)].start()
        i+=1
        time.sleep(5)
        # thread bug로 맥에서는 에러가 발생한다. 패치가 있을때 까지 실행 안됨.
    L=[]
    t = threading.Thread(target=getInput, args=(L,))
    t.start()
    start =timer()
    while True:    # infinite loop
        if int(timer() - start) == 10:
            i=0
            # print egg_count_num_dic
            for value in threads.keys():
                # print "thread key : ",value[6:7],",",value[8:14],",",value[15:]
                if(threads[value].is_alive() == False):
                    print value, ' is dead.'
                    threads[value] = CountingEggs(value[6:7], value[8:14],value[15:])
                    threads[value].start()
                i+=1
            start = timer()

        if L:
            for item in threads.keys():
                threads[item].setDoRun()
                threads[item].join()
                t.join()
            break  # stops the loop
