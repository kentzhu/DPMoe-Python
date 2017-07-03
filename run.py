# -*- coding: utf8 -*-
import sys
import time
import random
import webbrowser
from PyQt4 import  QtGui, QtCore  
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL as signal
from win32gui import *
from xml.etree import ElementTree

codec = QTextCodec.codecForName("utf8") 
QTextCodec.setCodecForLocale(codec)
QTextCodec.setCodecForCStrings(codec) 
QTextCodec.setCodecForTr(codec)


#-----------------------------------------------------------------------------------------------------------------------------------

class myMain(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
    
        #系统托盘图标
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        icon = QtGui.QIcon('img/icon.png')
        self.trayIcon.setIcon(icon)
        self.trayIcon.show()
        #单击图标事件
        #trayIcon.activated.connect(trayIconClick)

        #添加系统托盘菜单
        trayIcon_Action_AddOne = QtGui.QAction(self.tr("再来一发(&A)"), self,triggered=trayIcon_AddOne)
        trayIcon_Action_JustOne = QtGui.QAction(self.tr("只留一只(&O)"), self,triggered=trayIcon_JustOne)
        trayIcon_Action_ClearAll = QtGui.QAction(self.tr("统统不见(&C)"), self,triggered=trayIcon_ClearAll)
        trayIcon_Action_About = QtGui.QAction(self.tr("关于"), self,triggered=self.showAbout)
        trayIcon_Action_Site = QtGui.QAction(self.tr("更新/官方网站"), self,triggered=self.showSite)
        trayIcon_Action_Quit = QtGui.QAction(self.tr("退出程序(&Q)"), self,triggered=QtGui.qApp.quit)
        
        trayIconMenu = QtGui.QMenu()
        trayIconMenu.addAction(trayIcon_Action_AddOne)
        trayIconMenu.addAction(trayIcon_Action_JustOne)
        trayIconMenu.addAction(trayIcon_Action_ClearAll)
        trayIconMenu.addSeparator()
        trayIconMenu.addAction(trayIcon_Action_About)
        trayIconMenu.addAction(trayIcon_Action_Site)
        trayIconMenu.addSeparator()
        trayIconMenu.addAction(trayIcon_Action_Quit)
        
        self.trayIcon.setContextMenu(trayIconMenu)

    def showAbout(self):
        self.trayIcon.showMessage(self.tr('关于 DP桌宠'),self.tr("版本:beta 2(公测版) / 提意见:suom@qq.com"))

    def showSite(self):
        webbrowser.open_new_tab('http://www.dpmoe.com/')

#-----------------------------------------------------------------------------------------------------------------------------------

class myDesktopPet(QtGui.QWidget):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        #加载剧本
        self.loadScript()

        #临时对象
        self.image=QImage()

        
        #设置状态
        self.petStatus={'Status':0,'Script':0,'Step':-1,'Vx':0,'Vy':0,'ToRepeat':0,'NowPic':'','Mirror-X':False,'Mirror-Y':False}
        self.geometryLog={'old':{'left':0,'top':0},'new':{'left':0,'top':0}}
        self.workArea={'x':{'a':0,'b':0},'y':{'a':0,'b':0}}
        self.workAreaOld={'x':{'a':0,'b':0},'y':{'a':0,'b':0}}
        self.updateWorkArea()
        
        #调用initUI加载控件
        self.initUI()

        #定时器
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        #设置定时器间隔
        self.timerInterval=20
        #启动定时器
        self.timer.start(self.timerInterval, self)

    #设置外观设置
    def initUI(self):

        #永远置顶、消除边框
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow )
        #窗体透明
        self.trans=True
        self.set_transparency(True)
        
        #显示图片
        
        self.lbl = QtGui.QLabel(self)
        self.lbl.move(0, 0)

        self.setPic('falling','up-left')
        
        #不许动功能标记
        self.doNotMove=False

        #设置菜单
        self.setPopMenu()


        
        #窗体图标
        self.setWindowIcon(QtGui.QIcon('img\icon.png'))
        #设置大小
        self.resize(128, 128)
        #显示窗体
        self.show()
        self.randomSit()


    #自定义：右键菜单
    def setPopMenu(self):
        #菜单变量
        self.rightButton=False
        #右键菜单
        self.popMenu= QtGui.QMenu()
        if not self.doNotMove:
            #-不许动
            doNotMoveAction=QtGui.QAction(self.tr("不许动(&Z)"), self,triggered=self.setDoNotMove)
            self.popMenu.addAction(doNotMoveAction)
        else:
            #-可以动
            doNotMoveAction=QtGui.QAction(self.tr("自己一边儿玩去吧(&Z)"), self,triggered=self.setDoNotMove)
            self.popMenu.addAction(doNotMoveAction)
            
        #-退出
        quitFAction=QtGui.QAction(self.tr("关闭我(&Q)"), self,triggered=self.close)
        self.popMenu.addAction(quitFAction)

    #自定义：不许动切换
    def setDoNotMove(self):
        if self.doNotMove:
            self.doNotMove=False
        else:
            self.doNotMove=True
        self.setPopMenu()
        self.setPetStatus('falling','up-left')

    #自定义：加载配置文件
    def loadScript(self):
        try:
            self.scriptXML=open("img\setting.xml").read()
        except:
            self.scriptXML=self.loadDefaultScript()
            
        self.root=ElementTree.fromstring(self.scriptXML)

    #自定义：返回默认配置
    def loadDefaultScript(self):
        return """<?xml version="1.0" encoding="utf-8"?><root version='2'><status name='catch'><script name='general-left' type='static'><action pic='shime5.png'></action></script><script name='throw-left' type='static'><action pic='shime7.png'></action></script><script name='general-right' type='static'><action pic='shime5.png' Mirror-X='True'></action></script><script name='throw-right' type='static'><action pic='shime7.png' Mirror-X='True'></action></script></status><status name='falling'><script name='up-left' type='static'><action pic='shime5.png'></action></script><script name='down-left' type='static'><action pic='shime4.png'></action></script><script name='up-right' type='static'><action pic='shime5.png' Mirror-X='True'></action></script><script name='down-right' type='static'><action pic='shime4.png' Mirror-X='True'></action></script></status><status name='floor'><script name='general-left' type='static' pOut='100'><action pic='shime1.png'></action></script><script name='general-right' type='static' pOut='100'><action pic='shime1.png' Mirror-X='True'></action></script><script name='toFloor-left' type='dynamic'><action pic='shime20.png' useTime='400'></action><action pic='shime18.png' useTime='200'></action></script><script name='toFloor-right' type='dynamic'><action pic='shime20.png' useTime='400' Mirror-X='True'></action><action pic='shime18.png' useTime='200' Mirror-X='True'></action></script><script name='walk-left' type='dynamic' repeatTimeMax='20' repeatTimeMin='1' p='20'><action pic='shime2.png' useTime='300' XMoveMax='-1' XMoveMin='-1'></action><action pic='shime3.png' useTime='300' XMoveMax='-1' XMoveMin='-1'></action></script><script name='walk-right' type='dynamic' repeatTimeMax='20' repeatTimeMin='1' p='20'><action pic='shime2.png' useTime='300' XMoveMax='1' XMoveMin='1' Mirror-X='True'></action><action pic='shime3.png' useTime='300' XMoveMax='1' XMoveMin='1' Mirror-X='True'></action></script><script name='Sit' type='dynamic' p='10'><action pic='shime18.png' useTime='300'></action><action pic='shime11.png' useTime='3000'></action></script><script name='sleeplySit' type='dynamic' p='10'><action pic='shime18.png' useTime='300'></action><action pic='shime20.png' useTime='1000'></action><action pic='shime30.png' useTime='1500'></action><action pic='shime31.png' useTime='500'></action><action pic='shime32.png' useTime='500'></action><action pic='shime30.png' useTime='1500'></action><action pic='shime31.png' useTime='500'></action><action pic='shime32.png' useTime='500'></action><action pic='shime32.png' useTime='3000'></action><action pic='shime33.png' useTime='3000'></action><action pic='shime32.png' useTime='3000'></action><action pic='shime33.png' useTime='3000'></action><action pic='shime20.png' useTime='1000'></action><action pic='shime18.png' useTime='300'></action></script><script name='jump' type='dynamic' p='10' repeatTimeMax='3' repeatTimeMin='1'><action pic='shime49.png' useTime='300'></action><action pic='shime47.png' useTime='100' XMoveMax='-2' XMoveMin='-2' YMoveMax='-1' YMoveMin='-1'></action><action pic='shime47.png' useTime='50' XMoveMax='-2' XMoveMin='-2' YMoveMax='-0.5' YMoveMin='-0.5'></action><action pic='shime47.png' useTime='50' XMoveMax='-2' XMoveMin='-2' YMoveMax='0.5' YMoveMin='0.5'></action><action pic='shime47.png' useTime='100' XMoveMax='-2' XMoveMin='-2' YMoveMax='1' YMoveMin='1'></action><action pic='shime48.png' useTime='300'></action></script><script name='fly-left' type='dynamic' p='2'><action pic='shime49.png' useTime='1000'></action><action pic='shime47.png' useTime='200' XMoveMax='-2' XMoveMin='-2' YMoveMax='-1' YMoveMin='-1'></action><action pic='shime22.png' useTime='1000000' XMoveMax='-5' XMoveMin='-5' YMoveMax='-2' YMoveMin='-2'></action></script><script name='fly-right' type='dynamic' p='2'><action pic='shime49.png' useTime='1000' Mirror-X='True'></action><action pic='shime47.png' useTime='200' XMoveMax='2' XMoveMin='2' YMoveMax='-1' YMoveMin='-1' Mirror-X='True'></action><action pic='shime22.png' useTime='1000000' XMoveMax='5' XMoveMin='5' YMoveMax='-2' YMoveMin='-2' Mirror-X='True'></action></script></status><status name='wall-left'><script name='general' type='static' pOut='300'><action pic='shime12.png'></action></script><script name='up' type='dynamic' p='30' repeatTimeMax='6' repeatTimeMin='1' ><action pic='shime13.png' useTime='300' YMoveMax='-1' YMoveMin='-1'></action><action pic='shime14.png' useTime='300' YMoveMax='-1' YMoveMin='-1'></action></script><script name='down' type='dynamic' p='30' repeatTimeMax='5' repeatTimeMin='1' ><action pic='shime13.png' useTime='300' YMoveMax='1' YMoveMin='1'></action><action pic='shime14.png' useTime='300' YMoveMax='1' YMoveMin='1'></action></script><script name='jump' type='dynamic' p='5' toStatus='falling' toScript='down-left' toVx='True'><action pic='shime13.png' useTime='100' XMoveMax='5' XMoveMin='2'></action></script></status><status name='wall-right'><script name='general' type='static' pOut='300'><action pic='shime12.png' Mirror-X='True'></action></script><script name='up' type='dynamic' p='30' repeatTimeMax='6' repeatTimeMin='1' ><action pic='shime13.png' useTime='300' YMoveMax='-1' YMoveMin='-1' Mirror-X='True'></action><action pic='shime14.png' useTime='300' YMoveMax='-1' YMoveMin='-1' Mirror-X='True'></action></script><script name='down' type='dynamic' p='30' repeatTimeMax='5' repeatTimeMin='1' ><action pic='shime13.png' useTime='300' YMoveMax='1' YMoveMin='1' Mirror-X='True'></action><action pic='shime14.png' useTime='300' YMoveMax='1' YMoveMin='1' Mirror-X='True'></action></script><script name='jump' type='dynamic' p='5' toStatus='falling' toScript='down-right' toVx='True'><action pic='shime13.png' useTime='100' XMoveMax='-5' XMoveMin='-2'></action></script></status></root>"""
    
    
    #自定义：实现窗体透明    
    def set_transparency(self, enabled):
        if enabled:
            self.setAutoFillBackground(False)
        else:
            self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, enabled)
        self.repaint()

    #自定义：按钮点击    
    def buttonClicked(self):
        sender = self.sender()
        self.setWindowTitle(sender.text() + ' was pressed')

    #自定义：初始在屏幕中心
    def randomSit(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())*random.random(), (screen.height()-size.height())*random.random())

    #自定义：改变状态
    def setPetStatus(self,status,script,Vx=0,Vy=0):
        self.petStatus['Status']=status
        self.petStatus['Script']=script
        self.petStatus['Step']=-1
        self.petStatus['ToRepeat']=0
        self.petStatus['Vx']=Vx
        self.petStatus['Vy']=Vy
        
    #自定义：改变状态速度
    def setPetStatusV(self):
        self.petStatus['Vx']=(self.geometryLog['new']['left']-self.geometryLog['old']['left'])/1.5
        self.petStatus['Vy']=(self.geometryLog['new']['top']-self.geometryLog['old']['top'])/1.5
        
    #自定义：记录位置
    def setGeometryLog(self):  
        size=self.geometry()
        self.geometryLog['old']['left']=self.geometryLog['new']['left']
        self.geometryLog['old']['top']=self.geometryLog['new']['top']
        self.geometryLog['new']['left']=size.left()
        self.geometryLog['new']['top']=size.top()

    #自定义：更新工作区大小
    def updateWorkArea(self):
        h=FindWindow("Shell_TrayWnd","")
        r=GetWindowRect(h)
        screen=QtGui.QDesktopWidget().screenGeometry()

        self.workArea['x']['a']=0
        self.workArea['x']['b']=screen.width()
        self.workArea['y']['a']=0
        self.workArea['y']['b']=screen.height()
        
        #判断 横竖
        if (r[2]-r[0]) > ((self.workArea['x']['b']-self.workArea['x']['a'])/2) :
            #任务栏宽度 大于 屏幕宽度一半
            #横
            if (r[1])> ((self.workArea['y']['b']-self.workArea['y']['a'])/2):
                #任务栏上界 大于 屏幕高度一半
                #下
                self.workArea['y']['b']=r[1]
            else:
                #上
                self.workArea['y']['a']=r[3]
        else:
            #竖
            if (r[0])> ((self.workArea['x']['b']-self.workArea['x']['a'])/2):
                #任务栏左界 大于 屏幕宽度一半
                #右
                self.workArea['x']['b']=r[0]
            else:
                #左
                self.workArea['x']['a']=r[2]

        #屏幕改变，重置
        if not (self.workAreaOld['x']['a']==self.workArea['x']['a']\
           and self.workAreaOld['x']['b']==self.workArea['x']['b']\
           and self.workAreaOld['y']['a']==self.workArea['y']['a']\
           and self.workAreaOld['y']['b']==self.workArea['y']['b']):
            self.setPetStatus('falling','up-left')
        
        self.workAreaOld['x']['a']=self.workArea['x']['a']
        self.workAreaOld['x']['b']=self.workArea['x']['b']
        self.workAreaOld['y']['a']=self.workArea['y']['a']
        self.workAreaOld['y']['b']=self.workArea['y']['b']


    #自定义：根据场景等更新图片
    def setPic(self,status,script,i=0):
        tmp_node=self.root.findall("status[@name='"+status+"']/script[@name='"+script+"']/action")[i]
        #print tmp_node.attrib['pic']
        
        Mx=False
        My=False
        if tmp_node.attrib.has_key('Mirror-X'):
            if tmp_node.attrib['Mirror-X']=='True':
                Mx=True
        if tmp_node.attrib.has_key('Mirror-Y'):
            if tmp_node.attrib['Mirror-Y']=='True':
                My=True

        if self.petStatus['NowPic']==tmp_node.attrib['pic'] and self.petStatus['Mirror-X']==Mx and self.petStatus['Mirror-Y']==My:
            #不必换图
            pass
        else:
            img=QImage()
            img.load('img/'+tmp_node.attrib['pic'])                       
            img=img.mirrored(Mx,My)
            self.lbl.setPixmap(QPixmap.fromImage(img))

            self.petStatus['NowPic']=tmp_node.attrib['pic']
            self.petStatus['Mirror-X']=Mx
            self.petStatus['Mirror-Y']=My


            
    #鼠标释放
    def mouseReleaseEvent(self,e):   
        #重新设置状态
        self.setPetStatus('falling','up-left')
        self.setPetStatusV()
        #重新开始计时器
        self.timer.start(self.timerInterval, self)
        
        if self.rightButton == True:
            self.rightButton=False
            self.popMenu.popup(e.globalPos())
        
    #鼠标移动
    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.move(e.globalPos()-self.dragPos)
            e.accept()

            #记录位置
            self.setGeometryLog()
            self.setPetStatusV()
            if abs(self.petStatus['Vx'])<2:
                if self.petStatus['Vx']<0:
                    self.setPic('catch','general-left')
                else:
                    self.setPic('catch','general-right')
            else:
                if self.petStatus['Vx']<0:
                    self.setPic('catch','throw-left')
                else:
                    self.setPic('catch','throw-right')
            
        
            
    #鼠标点击        
    def mousePressEvent(self, e):
        #暂停计时器
        self.timer.stop()
        
        if e.button() == Qt.LeftButton:
            #加载图片
            self.setPic('catch','general-left')
            
            self.dragPos=e.globalPos()-self.frameGeometry().topLeft() 
            e.accept()
        if e.button() == Qt.RightButton and self.rightButton == False:
            self.rightButton=True
        #记录位置
        #self.setGeometryLog()   


    #定时器事件
    def timerEvent(self,e):

        #调试
        #print self.petStatus['Status']\
        #      +' '+self.petStatus['Script']\
        #      +' STEP:'+str(self.petStatus['Step'])
        
        #判断状态
        self.updateWorkArea()
        
        size =  self.geometry()
        if (size.top()<self.workArea['y']['b']) and (size.left>self.workArea['x']['a']-64) and (size.left<(self.workArea['x']['b']-64)):
            #尼玛忘了为什么要写这个
            if self.petStatus['Status']!='falling' and self.petStatus['Status']!='floor':
                #self.move(size.left(),self.workArea['y']['b'])
                if self.petStatus['Vx']>0:
                    self.setPetStatus('falling','down-left')
                else:
                    self.setPetStatus('falling','down-right')

        elif size.left()<self.workArea['x']['a']-64:
            #侧-左
            if self.petStatus['Status']!='falling':
                self.move(self.workArea['x']['a']-64,size.top())
                self.setPetStatus('wall-left','general')

        elif size.left()>self.workArea['x']['b']-64 :
            #侧-左
            if self.petStatus['Status']!='falling':
                self.move(self.workArea['x']['b']-64,size.top())
                self.setPetStatus('wall-right','general')


        #执行状态
        xPathStr="status[@name='"+self.petStatus['Status']+"']/script[@name='"+self.petStatus['Script']+"']"
        node=self.root.find(xPathStr)

        #掉落------------------------------------------------------------------------            
        if self.petStatus['Status']=='falling':
            #此处size是折中之策
            size =  self.geometry()
            
            #施加重力加速度
            self.petStatus['Vy']=self.petStatus['Vy']+0.3
            
            #判断出上界-清空Vx
            if size.top()<self.workArea['x']['a']-64:
                self.petStatus['Vx']=0
                
            #判断上升or下降
            if self.petStatus['Vy']>=0:
                #下降
                if self.petStatus['Vx']<0:
                    self.setPic('falling','down-left')
                else:
                    self.setPic('falling','down-right')
            else:
                #上升
                if self.petStatus['Vx']<0:
                    self.setPic('falling','up-left')
                else:
                    self.setPic('falling','up-right')

            #边缘判断
            if size.top()+self.petStatus['Vy']>self.workArea['y']['b']-128:
                #触地
                self.move(size.left(),self.workArea['y']['b']-128)
                
                if self.petStatus['Vx']<0:
                    self.setPetStatus('floor','toFloor-left')
                else:
                    self.setPetStatus('floor','toFloor-right') 
            elif size.left()<=self.workArea['x']['a']-64:
                #左侧
                self.move(self.workArea['x']['a']-64,size.top())
                self.setPetStatus('wall-left','general')
            elif size.left()>=self.workArea['x']['b']-64:
                #右侧
                self.move(self.workArea['x']['b']-64,size.top())
                self.setPetStatus('wall-right','general')
            else:
                #下降
                self.move(size.left()+self.petStatus['Vx'],size.top()+self.petStatus['Vy'])

        #地板------------------------------------------------------------------------
        elif self.petStatus['Status']=='floor' or self.petStatus['Status']=='wall-left' or self.petStatus['Status']=='wall-right':

            if node.attrib['type']=='dynamic':
                #动态脚本
                self.dynamicPlayer()
            elif node.attrib['type']=='static':
                #静态脚本
                
                #载入图片
                self.setPic(self.petStatus['Status'],self.petStatus['Script'])
                #随机进入其他脚本
                if self.doNotMove==False and random.random()<0.001*int(node.attrib['pOut'])/(1000/self.timerInterval):
                    allP=0
                    for i in self.root.findall("status[@name='"+self.petStatus['Status']+"']/script[@p]"):
                        allP=allP+int(i.attrib['p'])
                        
                    allP=random.random()*allP

                    for i in self.root.findall("status[@name='"+self.petStatus['Status']+"']/script[@p]"):
                        allP=allP-int(i.attrib['p'])
                        if allP<=0:
                            
                            self.setPetStatus(self.petStatus['Status'],i.attrib['name'])
                            break
 
        
        #推进帧数
        self.petStatus['Step']=self.petStatus['Step']+1

    #动态脚本-推进
    def dynamicPlayer(self):
        
        size=self.geometry()

        xPathStr="status[@name='"+self.petStatus['Status']+"']/script[@name='"+self.petStatus['Script']+"']"
        node=self.root.find(xPathStr)

        #推进action
        nowTime=self.petStatus['Step']*self.timerInterval
        actionTime=0
        flag=False

        iPic=0
        for i in node.getchildren():
            
            if nowTime<=actionTime and nowTime>=actionTime-self.timerInterval:
                #达到某一新action
                #更新图片
                self.setPic(self.petStatus['Status'],self.petStatus['Script'],iPic)
                #初始化移动Vx Vy
                if i.attrib.has_key('XMoveMax') and i.attrib.has_key('XMoveMin'):
                    tmp_Vx=(float(i.attrib['XMoveMin'])+random.random()*(float(i.attrib['XMoveMax'])-float(i.attrib['XMoveMin'])))
                    self.petStatus['Vx']=tmp_Vx
                if i.attrib.has_key('YMoveMax') and i.attrib.has_key('YMoveMin'):
                    tmp_Vy=(float(i.attrib['YMoveMin'])+random.random()*(float(i.attrib['YMoveMax'])-float(i.attrib['YMoveMin'])))
                    self.petStatus['Vy']=tmp_Vy
                    
            iPic=iPic+1
            actionTime=actionTime+int(i.attrib['useTime'])

	#执行位移
        toXY=False
        
        toX=size.left()+self.petStatus['Vx']
        #if toX<self.workArea['x']['a']-64:
        #    toX=self.workArea['x']['a']-64
        #    toXY=True
        #if toX>self.workArea['x']['b']-64:
        #    toX=self.workArea['x']['b']-64
        #    toXY=True
            
        toY=size.top()+self.petStatus['Vy']
        if toY<self.workArea['y']['a']:
            toY=self.workArea['y']['a']
            toXY=True
        if toY>self.workArea['y']['b']-128:
            toY=self.workArea['y']['b']-128
            toXY=True
            
        self.move(toX,toY)
        
        #print str(nowTime)+"/"+str(actionTime)
        
	#判断一次Script执行完毕
        if nowTime>actionTime:
            if node.attrib.has_key('repeatTimeMax') and node.attrib.has_key('repeatTimeMin'):
                if self.petStatus['ToRepeat']==0:
                    self.petStatus['ToRepeat']=round(int(node.attrib['repeatTimeMin'])\
                                                    +random.random()*(int(node.attrib['repeatTimeMax'])-int(node.attrib['repeatTimeMin'])))
                elif self.petStatus['ToRepeat']==1:
                    #重复完毕，切换状态
                    self.chgStatueFromDynamic()
                else:
                    self.petStatus['ToRepeat']=self.petStatus['ToRepeat']-1
                    self.petStatus['Step']=-1
                    self.setPic(self.petStatus['Status'],self.petStatus['Script'])
                
            else:
                #切换状态
                self.chgStatueFromDynamic()

        if toXY:
            self.chgStatueFromDynamic()


    def chgStatueFromDynamic(self):
        xPathStr="status[@name='"+self.petStatus['Status']+"']/script[@name='"+self.petStatus['Script']+"']"
        node=self.root.find(xPathStr)

        #是否指向状态及脚本
        if node.attrib.has_key('toStatus') and node.attrib.has_key('toScript'):
            #速度继承
            if node.attrib.has_key('toVx') and node.attrib.has_key('toVy'):
                self.setPetStatus(node.attrib['toStatus'],node.attrib['toScript'],self.petStatus['Vx'],self.petStatus['Vy'])
            elif node.attrib.has_key('toVx'):
                self.setPetStatus(node.attrib['toStatus'],node.attrib['toScript'],self.petStatus['Vx'],0)
            elif node.attrib.has_key('toVy'):
                self.setPetStatus(node.attrib['toStatus'],node.attrib['toScript'],0,self.petStatus['Vy'])
            else:  
                self.setPetStatus(node.attrib['toStatus'],node.attrib['toScript'])
        else:
            allP=round(random.random()*len(self.root.findall("status[@name='"+self.petStatus['Status']+"']/script[@type='static']")))
            for i in self.root.findall("status[@name='"+self.petStatus['Status']+"']/script[@type='static']"):
                allP=allP-1
                if allP<=0:
                    self.setPetStatus(self.petStatus['Status'],i.attrib['name'])
                    #print 'TO:'+self.petStatus['Status']+' '+i.attrib['name']
                    break
                
    
    #退出一个    
    def closeEvent(self, event):
        pass


#添加一个桌宠
def trayIcon_AddOne():
    petList.append(myDesktopPet())
    
#只留一个
def trayIcon_JustOne():
    f=True
    for i in range(len(petList)):
        if f:
            f=False
        else:
            petList[i]="";


#清空所有
def trayIcon_ClearAll():
    for i in range(len(petList)):
        petList[i]=""
    while len(petList)>0:
        del petList[0]
    

def main():
    
    global petList
    petList=[]
    
    app = QtGui.QApplication(sys.argv)

    #总控制模块
    x=myMain()
    #添加桌宠
    petList.append(myDesktopPet())
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



