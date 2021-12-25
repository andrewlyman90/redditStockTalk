from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.carousel import Carousel
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from kivy.uix.popup import Popup

from kivy_garden.graph import Graph, LinePlot,MeshLinePlot,BarPlot
import requests
import threading

import datetime
from datetime import datetime, timedelta
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import StringProperty
from kivy.lang import Builder

import re

global firstCall
global graph3
firstCall=1



callMade=0
global r
r=''

global tickers_on_plot

tickers_on_plot = []

global numCommentsArr
numCommentsArr= []

global maxVal
maxVal=0
global minVal
minVal=999999999

global carousel
carousel = Carousel(direction='right')

#global currentCommentTicker
#currentCommentTicker='None'
#global previousCommentTicker
#previousCommentTicker='None'



class firstGraphTitle(Label):

    def __init__(self, **kwargs):
        super(firstGraphTitle, self).__init__(**kwargs)

        #self.iterations = int(score)
        timeNow=datetime.now()

        Clock.schedule_interval(self.set_label,60)

    def set_label(self,instance):
        timeNow=datetime.now()

        self.text = str(timeNow.month)+'/'+str(timeNow.day)+' '+str(timeNow.hour)+':'+str(timeNow.minute)+':'+str(timeNow.second)
        #if self.score >= self.iterations:
            #self.event.cancel()


class commentButton(Button):

    def __init__(self, **kwargs):
        super(commentButton, self).__init__(**kwargs)
        self.background_color=[1,1,1,1]
        self.bind(on_press=self.pressed)
    """
    def on_state(self, widget, value):
        if value == 'down':
            #if self.text==commentsHeader1.previousCommentTicker:
                #self.background_color=[1,1,1,1]
                #value='up'
            #else:
            #self.background_color=[1,0,1,1]
            #self.background_down= 'images/button_normal.png'  # A gray image gives a duller red.
            tickerPickedIndex=int(self.text[0:2])-1
            commentsHeader1.lbl1.text=str(commentsHeader1.commentsArr[tickerPickedIndex][0:200])
            value='up'
    """
    def pressed(self,instance):
        #commentsHeader1.previousCommentTicker=commentsHeader1.currentCommentTicker
        #commentsHeader1.currentCommentTicker=self.text
        #print('currentCommentTicker',commentsHeader1.currentCommentTicker)
        tickerPickedIndex=int(self.text[0:2])-1
        commentsHeader1.lbl1.text=str(commentsHeader1.commentsArr[tickerPickedIndex][0:1000])


class MyButton(ToggleButtonBehavior, Button):


    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.background_color=[1,1,1,1]

    def on_state(self, widget, value):
        plot_colors = [[1,0,1,1], [0.5,0.75,0.9,1], [1,1,0,1], [1,0,.5,1], [0,1,0.3,1], [1,0,0,1], [0.2,1,1,1], [1,0.5,0,1], [1,1,1,0.5], [0,0,1,1],[1,0,1,1], [0.5,0.75,0.9,1], [1,1,0,1], [1,0,.5,1], [0,1,0.3,1], [1,0,0,1], [0.2,1,1,1], [1,0.5,0,1], [1,1,1,0.5], [0,0,1,1]]
        self.plot_dates=graph3.plot_dates
        if value == 'down':
            self.background_color=plot_colors[int(self.text[0:2])-1]
            self.background_down= 'images/button_normal.png'  # A gray image gives a duller red.
            tickers_on_plot.append(self.text)
            #print('Tickers on Plot',tickers_on_plot)
            graph3.rightbox.remove_widget(graph3.latestGraph)

            graph3.latestGraph=self.make_plot(numCommentsArr, self.plot_dates, tickers_on_plot, plot_colors)
            graph3.rightbox.add_widget(graph3.latestGraph)
            #graph3.rightbox.remove_widget(graph3.latestGraph)





        else:
            spot = tickers_on_plot.index(self.text)

            del tickers_on_plot[spot]
            graph3.rightbox.remove_widget(graph3.latestGraph)

            graph3.latestGraph=self.make_plot(numCommentsArr, self.plot_dates, tickers_on_plot, plot_colors)
            graph3.rightbox.add_widget(graph3.latestGraph)

            self.background_color=[1,1,1,1]

    def make_plot(self,ratings_list, plot_dates, tickers_on_plot, plot_colors):
        # Prepare the data
        x = list(range(1, 169))
        plot = None

        # make the graph
        graph = Graph(ylabel='Number of Comments', x_ticks_major = 24, y_ticks_major = (((maxVal*1.1)/5)-(((maxVal*1.1)/5)%1)),
                      y_grid_label=True, x_grid_label=False, padding=5, x_grid=True, y_grid=True,
                      xmin=1, xmax=192, ymin=minVal*0.9, ymax=maxVal*1.01)
        graph.background_color=[0,0,0,1]

        if (len(tickers_on_plot) > 0):
            for i in (tickers_on_plot):
                #if i is 10 we have to get 2 digits from our array, not 1!
                i=int(i[0:2])-1
                plot = LinePlot(line_width=4,color = plot_colors[i])
                plot.points = [(i, j) for i, j in zip(x, numCommentsArr[i])]

                graph.add_plot(plot)

        return graph

class GraphRotatedLabel(Label):
    angle = (45)

class Plot(RelativeLayout):

    def __init__(self, **kwargs):
        #print('Plot1 Called!')

    #*******#Pull Data from Our Google Drive CSV File and sort it using loops************************************
        r=requests.get(r'https://drive.google.com/uc?id=1Iv0N4S4rU1bnOxmSTldQ0AC_qQXOivwG')
        dataGrab=str(r.content)


        self.tickerIndex=[]
        self.tickerArr=[]
        self.numCommentsArr=[]
        timeNow=datetime.now()
        self.lastUpdate=str(timeNow.month)+'/'+str(timeNow.day)+' '+str(timeNow.hour)+':'+str(timeNow.minute)



        dataGrab=dataGrab.split('\\r\\n')
        i=0
        while i<(len(dataGrab)-1):
            newLine=dataGrab[i].split(',')
            self.tickerArr.append(str(newLine[1]))
            if i>0:
                self.numCommentsArr.append(float(newLine[2]))
            else:
                self.numCommentsArr.append(str(newLine[2]))

            self.tickerIndex.append(i)

            i+=1
        self.tickerArr=self.tickerArr[1:11]
        self.numCommentsArr=self.numCommentsArr[1:11]
        self.tickerIndex=self.tickerIndex[1:11]
#********************************************************************************************************************

        super(Plot, self).__init__(**kwargs)
        self.graph = Graph(xlabel='', ylabel="Number of Mentions on WSB", x_ticks_minor=1,
        x_ticks_major=1, y_ticks_major=(((self.numCommentsArr[0]*1.1)/5)-(((self.numCommentsArr[0]*1.1)/5)%1)),
        y_grid_label=True, x_grid_label=False,x_ticks_angle = 0, padding= 5,
        x_grid=True, y_grid=True, xmin=-0, xmax=10, ymin=0, ymax=self.numCommentsArr[0]*1.1)
        # graph.size = (1200, 400)
        # self.graph.pos = self.center


        self.plot_colors = [[1,0,1,1], [1,0,0,1], [1,1,0,1], [1,0,.5,1], [0,1,0.3,1], [0.5,0.75,0.9,1], [0,0,1,1], [0,1,0,1], [1,1,1,1], [0.2,1,1,1]]
        i=0
        while i < 10:
            self.plot = BarPlot(bar_width=50)
            self.plot.points = [[i,0],[i,self.numCommentsArr[i]]]
            self.plot.color=self.plot_colors[i]
            self.graph.add_plot(self.plot)
            i=i+1



        self.add_widget(self.graph)
        #label = Label(text="Wasup World!\n\n\n\n\n\n", size_hint_y=None)
        #self.add_widget(label)
        #self.add_widget(fakeXLabels)
#********************************************************************************************************************


        #self.plot = MeshLinePlot(color=[1, 1, 1, 1])
        #self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
        #self.plot2 = MeshLinePlot(color=[1, 0, 0, 1])
        #self.plot2.points = [(x, cos(x / 10.)) for x in range(0, 101)]
        #self.add_widget(self.graph)

        #self.graph.add_plot(self.plot)
        #self.graph.add_plot(self.plot2)


        #Calls Update Function Below Which Updates Plot 1
        Clock.schedule_interval(self.updateTime, 60)

    def updateTime(self,instance):
        print('Updating First Graph!')
        timeNow=datetime.now()
        self.lastUpdate=str(timeNow.month)+'/'+str(timeNow.day)+' '+str(timeNow.hour)+':'+str(timeNow.minute)
        #*******#Pull Data from Our Google Drive CSV File and sort it using loops************************************
        r=requests.get(r'https://drive.google.com/uc?id=1Iv0N4S4rU1bnOxmSTldQ0AC_qQXOivwG')

        #Enable to see if Google is blocking our request (usual case if we are not able to access data)

        self.tickerIndex=[]
        self.tickerArr=[]
        self.numCommentsArr=[]

        dataGrab=str(r.content)

        dataGrab=dataGrab.split('\\r\\n')
        i=0
        while i<(len(dataGrab)-1):
            newLine=dataGrab[i].split(',')
            self.tickerArr.append(str(newLine[1]))
            if i>0:
                self.numCommentsArr.append(float(newLine[2]))
            else:
                self.numCommentsArr.append(str(newLine[2]))

            self.tickerIndex.append(i)

            i+=1
        self.tickerArr=self.tickerArr[1:11]
        self.numCommentsArr=self.numCommentsArr[1:11]
        self.tickerIndex=self.tickerIndex[1:11]
#********************************************************************************************************************
        #Plot(size_hint_y=None, height=500)

        i=0
        while i < 10:
            self.plot = BarPlot(bar_width=50)
            self.plot.points = [[i,0],[i,self.numCommentsArr[i]]]
            self.plot.color=self.plot_colors[i]
            self.graph.add_plot(self.plot)
            i=i+1
        self.graph.y_ticks_major=(((self.numCommentsArr[0]*1.1)/5)-(((self.numCommentsArr[0]*1.1)/5)%1))
        self.graph.ymax=self.numCommentsArr[0]*1.1


class Plot3(RelativeLayout):


    def __init__(self,**kwargs):
        super(Plot3, self).__init__(**kwargs)      # this is only for if kivy code goes in the py file

    #*******#Pull Data from Our Google Drive CSV File and sort it using loops************************************
        global r
        if(firstCall==1):
            r=requests.get(r'https://drive.google.com/uc?id=1VDRcmRiRLAohbet4cjdi59Hwon9md1FB')
        else:
            print('skipping reloading Data!')
        #Enable to see if Google is blocking our request (usual case if we are not able to access data)
        #print('Google Response:',r.content)

        self.tickerIndex=[]
        self.tickerArr=[]
        self.numCommentsArr=[]
        self.plot_dates=[]
        self.plot_colors = [[1,0,1,1], [0.5,0.75,0.9,1], [1,1,0,1], [1,0,.5,1], [0,1,0.3,1], [1,0,0,1], [0.2,1,1,1], [1,0.5,0,1], [1,1,1,0.5], [0,0,1,1],[1,0,1,1], [0.5,0.75,0.9,1], [1,1,0,1], [1,0,.5,1], [0,1,0.3,1], [1,0,0,1], [0.2,1,1,1], [1,0.5,0,1], [1,1,1,0.5], [0,0,1,1]]

        dataGrab=str(r.content)

        dataGrab=dataGrab.split('\\r\\n')
        datesRow=dataGrab[0].split(',')
        i=1
        k=0
        global maxVal
        global minVal

        while k< (len(datesRow)-1):

            while i<(len(dataGrab)-1):
                newLine=dataGrab[i].split(',')
                tickerCommentsArr=newLine[2:170]
                self.tickerArr.append(str(i+0)+' '+str(newLine[1]))
                #Convert all Comment Counts from Strings to Floats, find Max and Min Values also*****

                f=0
                while f<len(tickerCommentsArr):
                    try:
                        tickerCommentsArr[f]=float(tickerCommentsArr[f])
                    except: #if a ticker was recently added, it may have empty cells that can't be converted to float, so we assign 0
                        tickerCommentsArr[f]=0
                    if tickerCommentsArr[f]>maxVal:
                        maxVal=tickerCommentsArr[f]
                    if tickerCommentsArr[f]<minVal:
                        minVal=tickerCommentsArr[f]
                    f=f+1


                #******************************************************
                if (i>0):
                    numCommentsArr.append(tickerCommentsArr)

                self.tickerIndex.append(i)

                i+=1
            k=k+1

        #self.tickerArr=self.tickerArr[1:11]
        #numCommentsArr=numCommentsArr[1:11]
        #self.tickerIndex=self.tickerIndex[1:11]
        self.plot_dates=datesRow[2:]



        self.mainview = ModalView(size_hint = (1, 1),background_color=[0,0,0,1])
        self.box = BoxLayout(orientation = "horizontal", padding = [0,0,0,0])   # left, top, right, bot

        # make a the left side (will contain a 2 other layouts)
        self.leftbox = BoxLayout(orientation = "vertical", size_hint_x = 2)

        # will contain the ticker gridlayout (top left)
        self.scroll = ScrollView(do_scroll_x = False, do_scroll_y = True)

        # holds tickers (top left that will be scrollable)

        self.ticker_grid = GridLayout(rows = len(self.tickerArr), cols = 1, size_hint_x = 1,size_hint_y = 2)

        # makes the gridlayout scrollabel (top left)
        self.ticker_grid.bind(minimum_height = self.ticker_grid.setter("height"))

        # populate the top left scrollable gridlayout (area that shows what tickers are shown)
        # will be marked X or + depending on if it's being shown

        # combine everything
        self.scroll.add_widget(self.ticker_grid)
        self.leftbox.add_widget(self.scroll)

        # right side that will be graph - recall I make my own x-axis
        self.rightbox = BoxLayout(orientation = "vertical",size_hint_x = 10)

        self.good_handle_plot(None)

        for i in range(0, len(self.tickerArr)):
            #ticker_grid.add_widget(Label(text = self.tickerArr[i],size_hint_y = 0.6, size_hint_x = 0.6))
            self.ticker_grid.add_widget(MyButton(text = self.tickerArr[i], size_hint_y = 10, size_hint_x = 1))

    def good_handle_plot(self, instance):
        global firstCall

        print('STARTING GOOD HANDLE PLOT************************')


        # populate the top left scrollable gridlayout (area that shows what tickers are shown)
        # will be marked X or + depending on if it's being shown



        # right side that will be graph - recall I make my own x-axis
        self.rightbox = BoxLayout(orientation = "vertical",size_hint_x = 10)

        # x-axis for graph (right side of modalview)
        self.rightbotgrid = GridLayout(rows = 1, cols = 24, size_hint_y = 0.05)

        # make invisible labels for formatting
        # this is an invsible widget just to make things fit
        self.rightbotgrid.add_widget(Label(size_hint_x = 1/13))

        for i in range(1, 168):

            # make actual labels - 1/13 is just what fit
            if i%167==1:
                self.rightbotgrid.add_widget(Label(text = self.plot_dates[i], size_hint_x = 1/13))

        # combine everything


        # the graph doesn't have legend functionality, so make one
        #leftbox.add_widget(self.plot_make_legend())

        plot_ratings=numCommentsArr

        # make the actual plot
        #if(firstCall!=1):
            #self.rightbox.remove_widget(self.latestGraph)
        self.latestGraph=self.make_plot(plot_ratings, self.plot_dates, tickers_on_plot, self.plot_colors)
        self.rightbox.add_widget(self.latestGraph)

        # add the x-axis
        if(firstCall==1):
            self.box.add_widget(self.leftbox)
        else:
            self.box.remove_widget(self.rightbox)
        self.box.add_widget(self.rightbox)
        if(firstCall==1):
            self.mainview.add_widget(self.box)
            self.add_widget(self.mainview)
        firstCall=0
        #self.self.mainview.open()


    def make_plot(self,ratings_list, plot_dates, tickers_on_plot, plot_colors):
        # Prepare the data
        print('Make Plot being called again and again??')
        x = list(range(1, 24))
        plot = None

        # make the graph
        graph = Graph(ylabel='Number of Comments', x_ticks_major = 24, y_ticks_major = (((maxVal*1.1)/5)-(((maxVal*1.1)/5)%1)),
                      y_grid_label=True, x_grid_label=False, padding=5, x_grid=True, y_grid=True,
                      xmin=1, xmax=26, ymin=minVal*0.9, ymax=maxVal*1.01)
        graph.background_color=[0,0,0,1]

        if (len(tickers_on_plot) > 0):
            for i in (tickers_on_plot):
                #if i is 10 we have to get 2 digits from our array, not 1!
                i=int(i[0:2])-1
                plot = LinePlot(line_width=4,color = self.plot_colors[i])
                hours24=numCommentsArr[i][-24:]
                print(len(numCommentsArr[i][-24:]),hours24[0],hours24[-1])
                plot.points = [(i, j) for i, j in zip(x, hours24)]

                graph.add_plot(plot)

        return graph



#*******Comments Section****************************************************************
Builder.load_string('''
<ScrolllabelLabel>:
    Label:
        text: root.text
        font_size: 50
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]
''')

class ScrolllabelLabel(ScrollView):
    text = StringProperty('')

class commentsHeader(GridLayout):

    def __init__(self, **kwargs):



        super(commentsHeader, self).__init__(**kwargs)
        self.rows = 1
        self.cols = 2
        #self.size_hint_y = 1
        #self.size_hint_x = 1
        #self.width="600dp"
        self.mainview = ModalView(size_hint = (1, 1),background_color=[0,0,0,1])

        global initComments
        initComments=1
        Clock.schedule_once(self.loadComments, 3)



        #self.add_widget(self.commentLabel)
    def loadComments(self,instance):
        global initComments
        print("The current slide is:",carousel.index,'initComments is',initComments)

        if (initComments==1) | (carousel.index==1 & initComments==0):
            initComments=0

            print("START!~!!!The current slide is:",carousel.index,'initComments is',initComments)

            #comments=Label(text =graph.tickerArr[0],font_size='20sp',size_hint_x = 1/13)
            r=requests.get(r'https://drive.google.com/uc?id=1Ihub-g054Kbhp4HlaNfblwm9XhhZV5WT')

            self.commentsArr=[]
            self.tickerArr=[]

            dataGrab=str(r.text)

            dataGrab=dataGrab.split('\r')
            print('Comments Start!',len(dataGrab)-1)

            skipFirst=0
            for line in dataGrab:
                skipFirst+=1
                if skipFirst==1:
                    continue
                try:
                    line=line.split('{')
                    ticker=(line[0].split(','))[0]
                    self.tickerArr.append(str(ticker))

                    tempSuperString=ticker+"\n_______________________________\n"
                    commCount=0
                    for i in range(len(line)):
                        commCount+=1
                        comment=line[i*-1-1].split('}')
                        comment[0]=comment[0].replace('\\n','\n')
                        #print('Comment caught is',comment[0],'Length',len(line))
                        tempSuperString=tempSuperString+str(commCount)+':  '+str(comment[0])+'\n'
                except:
                    print('No comments')

                self.commentsArr.append(tempSuperString)
                    #except:
                        #print(str(newLine[0]),' No Recent Comments!')
                        #self.commentsArr.append('No Recent Comments!')
                i+=1

            self.box = BoxLayout(orientation = "horizontal", padding = [0,0,0,0])   # left, top, right, bot

            # make a the left side (will contain a 2 other layouts)
            self.leftbox = BoxLayout(orientation = "vertical", size_hint_x = 10)
            self.rightbox = BoxLayout(orientation = "vertical", size_hint_x = 10)

    #**************Create Comment Ticker Button Scroll Wheel - Left Side ********************************************************************************
            self.scroll = ScrollView(do_scroll_x = False, do_scroll_y = True)

            # holds tickers (top left that will be scrollable)

            self.ticker_grid = GridLayout(rows = len(self.tickerArr), cols = 1, size_hint_x = 1,size_hint_y = 2)

            # makes the gridlayout scrollabel (top left)
            self.ticker_grid.bind(minimum_height = self.ticker_grid.setter("height"))
            self.scroll.add_widget(self.ticker_grid)

            self.currentCommentTicker=str(0+1)+' '+self.tickerArr[0]
            self.previousCommentTicker='None'

            #Assign TICKER names to each of the 20 buttons on our left button scroll
            for i in range(0, 20):
                self.ticker_grid.add_widget(commentButton(text = str(i+1)+' '+self.tickerArr[i], size_hint_y = 10, size_hint_x = 1))

            #global currentCommentTicker


    #********Text Scroll Work - Right Side ********************************************************************************************************************
            #print('First Ticker Comments',self.commentsArr[0][0:2000])
            self.lbl1 = ScrolllabelLabel(text=str(self.commentsArr[0][0:2000])) # create a label instance
            #self.lbl1 = ScrolllabelLabel(text='DisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplay777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777')
    #**************************************************************************************************************************************

            self.leftbox.add_widget(self.scroll)
            self.box.add_widget(self.leftbox)

            #self.rightbox.add_widget(self.scrollComms)
            self.rightbox.add_widget(self.lbl1)

            self.box.add_widget(self.rightbox)
            self.mainview.add_widget(self.box)

            self.add_widget(self.mainview)


            Clock.schedule_interval(self.set_label,60)

    def set_label(self,instance):
        print('Updating Comment Box!')
"""
class slide3(GridLayout):

    def __init__(self,**kwargs):
        super(slide3, self).__init__(**kwargs)      # this is only for if kivy code goes in the py file


        self.latestGraph=self.make_plot(plot_ratings, self.plot_dates, tickers_on_plot, self.plot_colors)
        self.rightbox.add_widget(self.latestGraph)

    def make_plot(self,ratings_list, plot_dates, tickers_on_plot, plot_colors):
        # Prepare the data
        print('Make Plot being called again and again??')
        x = list(range(1, 168))
        plot = None

        # make the graph
        graph = Graph(ylabel='Number of Comments', x_ticks_major = 24, y_ticks_major = (((maxVal*1.1)/5)-(((maxVal*1.1)/5)%1)),
                      y_grid_label=True, x_grid_label=False, padding=5, x_grid=True, y_grid=True,
                      xmin=1, xmax=192, ymin=minVal*0.9, ymax=maxVal*1.01)
        graph.background_color=[0,0,0,1]

        if (len(tickers_on_plot) > 0):
            for i in (tickers_on_plot):
                #if i is 10 we have to get 2 digits from our array, not 1!
                i=int(i[0:2])-1
                plot = LinePlot(line_width=4,color = self.plot_colors[i])
                plot.points = [(i, j) for i, j in zip(x, numCommentsArr[i])]

                graph.add_plot(plot)

        return graph
"""
class GraphLayoutApp(App):

    def build(self):
#********************************************************************************************************************
        graph = Plot(size_hint_y=None, height=500)

        self.tickerArr=graph.tickerArr
        self.numCommentsArr=graph.numCommentsArr
        self.tickerIndex=graph.tickerIndex


        class fakeXLabelsClass(GridLayout):



            def __init__(self, **kwargs):
                super(fakeXLabelsClass, self).__init__(**kwargs)
                self.rows = 1
                self.cols = 13
                self.size_hint_y = 0.05
                self.add_widget(Label(size_hint_x = 1/13))
                print('First X Labels')


                tick0=GraphRotatedLabel(text =graph.tickerArr[0],font_size='20sp',size_hint_x = 1/13)
                tick1=GraphRotatedLabel(text =graph.tickerArr[1],font_size='20sp',size_hint_x = 1/13)
                tick2=GraphRotatedLabel(text =graph.tickerArr[2],font_size='20sp',size_hint_x = 1/13)
                tick3=GraphRotatedLabel(text =graph.tickerArr[3],font_size='20sp',size_hint_x = 1/13)
                tick4=GraphRotatedLabel(text =graph.tickerArr[4],font_size='20sp',size_hint_x = 1/13)
                tick5=GraphRotatedLabel(text =graph.tickerArr[5],font_size='20sp',size_hint_x = 1/13)
                tick6=GraphRotatedLabel(text =graph.tickerArr[6],font_size='20sp',size_hint_x = 1/13)
                tick7=GraphRotatedLabel(text =graph.tickerArr[7],font_size='20sp',size_hint_x = 1/13)
                tick8=GraphRotatedLabel(text =graph.tickerArr[8],font_size='20sp',size_hint_x = 1/13)
                tick9=GraphRotatedLabel(text =graph.tickerArr[9],font_size='20sp',size_hint_x = 1/13)

                self.ticks=[tick0,tick1,tick2,tick3,tick4,tick5,tick6,tick7,tick8,tick9]

                for i in range(0, 10):
                    # make actual labels - 1/13 is just what fit
                    #fakeXLabels.add_widget(Label(text = self.tickerArr[i],font_size='20sp',size_hint_x = 1/13))
                    #print('iteration is ', i,graph.tickerArr[i])
                    #self.ticks[i]=GraphRotatedLabel(text =graph.tickerArr[i],font_size='20sp',size_hint_x = 1/13)
                    self.add_widget(self.ticks[i])
                Clock.schedule_interval(self.set_label,60)

            def set_label(self,instance):
                print('Updating X Labels')
                for i in range(0, 10):
                    # make actual labels - 1/13 is just what fit
                    #fakeXLabels.add_widget(Label(text = self.tickerArr[i],font_size='20sp',size_hint_x = 1/13))
                    #print('iteration is ', i,graph.tickerArr[i])
                    self.ticks[i].text=graph.tickerArr[i]
                #print("Carousel index is:",carousel.index)

        # x-axis for graph (right side of modalview)
        fakeXLabels = fakeXLabelsClass()


        # x-axis for graph (right side of modalview)
        global commentsHeader1
        commentsHeader1 = commentsHeader()
        commentsHeader2 = commentsHeader()
#********************************************************************************************************************

        scroll_view = ScrollView()
        grid_layout = GridLayout(cols=1, padding=5, spacing=60, size_hint_y=None)
        grid_layout.bind(minimum_size=grid_layout.setter('size'))
        global graph3
        graph3=Plot3(size_hint_y=None, height=1000)



        #Create a Title for first Graph, store inside box
        #firstTitle=str()
        #label = Label(text=graph.lastUpdate,font_size='20sp', size_hint_y=55)
        box = BoxLayout(orientation = "vertical", padding = [0,20,0,0])   # left, top, right, bot
        #Created a Dummy Box to use as spacer above first graph Title
        box2 = BoxLayout(orientation = "vertical", padding = [0,20,0,0])   # left, top, right, bot
        boxTest = BoxLayout(orientation = "horizontal", padding = [0,0,0,0])   # left, top, right, bot

        firstTitle=firstGraphTitle()
        box.add_widget(firstTitle)


        grid_layout.add_widget(box2)
        grid_layout.add_widget(box)


        grid_layout.add_widget(graph)
        grid_layout.add_widget(fakeXLabels)


        #Create a Title for Second Graph, store inside box
        label2 = Label(text="    Current Top 20 7 Day History",font_size='50sp', size_hint_y=55)
        box3 = BoxLayout(orientation = "vertical", padding = [0,20,0,0])   # left, top, right, bot
        box3.add_widget(label2)
        #Created a Dummy Box to use as spacer above Second graph Title
        box4 = BoxLayout(orientation = "vertical", padding = [20,20,20,20], size_hint_y=55)   # left, top, right, bot
        box5 = BoxLayout(orientation = "vertical", padding = [20,20,20,20], size_hint_y=55)   # left, top, right, bot
        grid_layout.add_widget(box5)
        grid_layout.add_widget(box4)
        grid_layout.add_widget(box3)

        grid_layout.add_widget(graph3)
        scroll_view.add_widget(grid_layout)


        #carousel = Carousel(direction='right')
        carousel.add_widget(scroll_view)

        print("The current slide is:",carousel._curr_slide)
        scroll_view2 = ScrollView()
        box6 = BoxLayout(orientation = "vertical", padding = [0,0,0,0])   # left, top, right, bot
        grid_layout2 = GridLayout(cols=1, padding=5, spacing=60, size_hint_y=None)
        grid_layout2.bind(minimum_size=grid_layout.setter('size'))
        #grid_layout2.add_widget(commentsHeader1)
        box6.add_widget(commentsHeader1)
        #scroll_view2.add_widget(commentsHeader1)
        carousel.add_widget(box6)






        print('End of main thread!!!!!!!!!!!!!!!!!!!!!')




        return carousel


if __name__ == '__main__':
    GraphLayoutApp().run()
