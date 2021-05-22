import json
import paho.mqtt.client as mqtt
from tkinter import *
from tkinter import ttk

_SUB = ""
_PUB = ""
class MqttClient(object):

  def __init__(self):
    self.client = mqtt.Client()
    self.subscription_topic_name = None
    self.publish_topic_name = None
    self.callback = None

  def connect(self, subscription_topic_name, publish_topic_name,mqtt_broker_ip_address="broker.emqx.io",use_off_campus_broker=False):
    
    # mqtt_broker_ip_address = "test.mosquitto.org"
    # mqtt_broker_ip_address = "broker.hivemq.com"
    mqtt_broker_ip_address = "broker.emqx.io"
    self.subscription_topic_name = subscription_topic_name
    self.publish_topic_name = publish_topic_name

    # Callback for when the connection to the broker is complete.
    self.client.on_connect = self._on_connect
    self.client.message_callback_add(self.subscription_topic_name, self._on_message)

    print("Connecting to mqtt broker {}".format(mqtt_broker_ip_address), end="")
    self.client.connect(mqtt_broker_ip_address)
    # self.client.connect(mqtt_broker_ip_address, 1883, 60)
    self.client.loop_start()

  def send_message(self, type_name, payload=None):
    message_dict = {"type": type_name}
    if payload is not None:
      message_dict["payload"] = payload
    message = json.dumps(message_dict)
    self.client.publish(self.publish_topic_name, message)

  def _on_connect(self, client, userdata, flags, rc): # called when broker responds to our connection request 
    if rc == 0:
        print(" ... Connected!")
    else:
        print(" ... Error!!!")
        exit()

    print("Publishing to topic:", self.publish_topic_name)
    self.client.on_subscribe = self._on_subscribe

    # Subscribe to topic(s)
    self.client.subscribe(self.subscription_topic_name)

  
  def _on_subscribe(self, client, userdata, mid, granted_qos): # called when broker responds to clients subscribe request
    print("Subscribed to topic:", self.subscription_topic_name)

  def _on_message(self, client, userdata, msg): # called when a message has been recieved on a topic that the client has subscribed to.
    message = msg.payload.decode()
    if not self.callback:
        print("Missing a callback")
        return

    # Attempt to parse the message and call the appropriate function.
    try:
        message_dict = json.loads(message)
    except ValueError:
        return
    if "type" not in message_dict:
      return
    message_type = message_dict["type"]
    message_payload = None
    if "payload" in message_dict:
        message_payload = message_dict["payload"]        

    self.callback(message_type, message_payload)

  def close(self):
    self.callback = None
    self.client.loop_stop()
    self.client.disconnect()




def Page2():

  # global _PUB,_SUB
  publisher = player1_entry.get()
  subscriber = player2_entry.get()
  # print(publisher,subscriber)
  window.destroy()
  # MQTT on_message callback (use via a lambda function below)
  def example_mqtt_callback(type_name, payload, chat_window):
    print("Received message payload: ", payload)
    chat_window["text"] += "\nFrom "+ str(type_name)  + " : " + payload

  # Tkinter callbacks
  def send_message(mqtt_client, chat_window, msg_entry,publisher="chat"):
    msg = msg_entry.get()
    msg_entry.delete(0, 'end')
    chat_window["text"] += "\nMe: " + msg
    mqtt_client.send_message(publisher, msg) # Sending MQTT message

  def quit_program(mqtt_client):
    mqtt_client.close()
    exit()

  
  
  root = Tk()
  root.title("Chat App using paho Python(MQTT protocol)")

  s = ttk.Style()
  s.configure('My.TFrame', background='cyan',foreground='green')
  s.configure('My.TButton', font=('Helvetica', 12))
  s.configure('My.TLabel', font=('Helvetica', 18))
  
  main_frame = ttk.Frame(root, padding=50, relief='raised',style='My.TFrame')
  main_frame.grid()


  label = ttk.Label(main_frame,foreground="white",background="black", justify=LEFT, text="Send a message",style='My.TLabel')
  label.grid(columnspan=10,padx=10,pady=10)

  msg_entry = ttk.Entry(main_frame, width=60,style='My.TLabel',font=('Arial', 18, 'bold'))
  msg_entry.grid(row=10, column=0,padx=10,pady=10,ipadx=10,ipady=10)

  msg_button = ttk.Button(main_frame, text="Send",style='My.TButton')
  msg_button.grid(row=10, column=20,padx=10,pady=10)
  msg_button['command'] = lambda: send_message(mqtt_client, chat_window, msg_entry,publisher)

  label = ttk.Label(main_frame,foreground="white",background="black", justify=LEFT, text="HISTORY",style='My.TLabel')
  label.grid(columnspan=10,padx=10,pady=10)

  chat_window = ttk.Label(main_frame,padding=20, justify=LEFT, text="", width=60, wraplength="500p",style='My.TLabel')
  chat_window.grid(columnspan=10,padx=10,pady=10)

  q_button = ttk.Button(main_frame, text="Quit",style='My.TButton')
  q_button.grid(row=20, column=20,padx=10,pady=10)
  q_button['command'] = (lambda: quit_program(mqtt_client))




  mqtt_client = MqttClient() 
  mqtt_client.callback = lambda type, payload: example_mqtt_callback(type, payload, chat_window)
  mqtt_client.connect(publisher, subscriber, use_off_campus_broker=True)  # "Send to" and "listen to" the same topic

  root.mainloop()



  



if __name__ == "__main__":
  print("MQTT Application Window 1")
  # Driver Code
  window = Tk()
  window.title("PY - MQTT")
  Label(window,text = 'Welcome To Chat App',font=('sans sherif bold', 25),bg = 'black' , fg = 'white').place(x = 220 , y = 20)
  Label(window, text='Topic 1',font=('sans sherifbold', 19),bg = 'black' , fg = 'red').place(x=180, y=180)
  player1_entry = Entry(window,width=20,font=('Courier New bold italic' , 14) , fg = 'red',	highlightthickness = '1' , highlightcolor = 'red')
  player1_entry.focus_set()
  player1_entry.place(x=350, y=185)
  #player1 = player1_entry.get()
  Label(window, text='Topic 2', font=('sans sherif', 19),bg = 'black' , fg = 'green').place(x=180, y=250)
  player2_entry = Entry(window, width=20 ,font=('Courier New bold italic' , 14),	highlightthickness = '1' , highlightcolor = 'green' , fg = 'green')
  player1_entry.bind('<Return>', lambda event :player2_entry.focus_set())

  player2_entry.place(x=350, y=255)
  Button(window, text='Submit', command= Page2,font=('sans sherif', 16),bg = 'black' , fg = 'white').place(x=350, y=325)
  window.geometry('700x500+150+100')
  window.mainloop()
  
