#include <PubSubClient.h>
#include "Controller.h"
#include <WiFi.h>
#include <WiFiClient.h>

// const char* ssid = "JOY MART(2.4G)";
// const char* password = "0925218518";
// const char* ssid = "ICE CREAM DELIVERY";
// const char* password = "ILOVENAKO";
const char* ssid = "Jasper";
const char* password = "jasper53540759";

// MQTT Broker
const char* mqtt_broker = "broker.emqx.io";
const char* topic = "esp32/smartstrip";
const char* result_topic = "esp32/result";
const char* mqtt_username = "emqx";
const char* mqtt_password = "public";
const int mqtt_port = 1883;

//smartstrip
//IPAddress stripIP = {192, 168, 0, 105}; //at home
// IPAddress stripIP = {192, 168, 31, 9}; //at dorm
IPAddress stripIP = {192, 168, 73, 84}; //final
Controller strip(stripIP, 9999);
String ids[6] = {"8006DAF56A19C24578480586C08E65D01F0F716F00", "8006DAF56A19C24578480586C08E65D01F0F716F01",
                 "8006DAF56A19C24578480586C08E65D01F0F716F02", "8006DAF56A19C24578480586C08E65D01F0F716F03",
                 "8006DAF56A19C24578480586C08E65D01F0F716F04", "8006DAF56A19C24578480586C08E65D01F0F716F05"};

WiFiClient espClient;
PubSubClient client(espClient);

void setup()
{   //setup wifi connection
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    uint32_t notConnectedCounter = 0;
    while (WiFi.status() != WL_CONNECTED) 
    {
        Serial.print("Connecting to wifi:");
        Serial.println(ssid);
        delay(1000);
        notConnectedCounter++;
        if(notConnectedCounter > 5) 
        { // Reset if not connected after 5s
            Serial.println("Resetting due to Wifi not connecting...");
            ESP.restart();
            notConnectedCounter = 0;
        }
    }
    Serial.println("Connection successful");

    //connecting to a mqtt broker
     client.setServer(mqtt_broker, mqtt_port);
     client.setCallback(callback);
     client.setBufferSize(2048);
     while (!client.connected()) 
     {
         String client_id = "esp32-client-";
         client_id += String(WiFi.macAddress());
         Serial.printf("The client %s connects to the public mqtt broker\n", client_id.c_str());
         if (client.connect(client_id.c_str(), mqtt_username, mqtt_password))
             Serial.println("Public emqx mqtt broker connected");
         else 
         {
             Serial.print("failed with state ");
             Serial.println(client.state());
             delay(2000);
         }
     }    
     
    client.subscribe(topic);
}

void callback(char* Topic, byte* payload, unsigned int length)
{
    payload[length] = '\0';
    char* receive_msg = (char*)payload;
    const char* delim = " ";
    char* first_arg = strtok(receive_msg, delim);    
    String response = "";
    if(strcmp(first_arg, "getEmeter") == 0)
    {
        Serial.println("getEmeter");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        response = strip.getEmeter(ids[ind]);
    }
    else if(strcmp(first_arg, "getInfo") == 0)
    {
        Serial.println("getInfo");
        response = strip.getInfo();
    }
    else if(strcmp(first_arg, "turnoff") == 0)
    {
        Serial.println("turnoff");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        response = strip.turn_off(ids[ind]);
    }
    else if(strcmp(first_arg, "turnon") == 0)
    {
        Serial.println("turnon");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        response = strip.turn_on(ids[ind]);
    }
    else if(strcmp(first_arg, "setAlias") == 0)
    {
        Serial.println("setAlias");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        char* name = strtok(NULL, delim);
        String name_str = "";
        while(name != NULL)
        {
            name_str += String(name) + " ";         
            name = strtok(NULL, delim);
        }
        Serial.println(name_str);
        response = strip.set_alias(ids[ind], name_str);
    }
    else if(strcmp(first_arg, "reboot") == 0)
    {
        Serial.println("reboot");
        response = strip.reboot();      
    }
    else if(strcmp(first_arg, "scan") == 0)
    {
        Serial.println("scan wifi");
        response = strip.scan_wifi();
    }
    else if(strcmp(first_arg, "led") == 0)
    {
        Serial.println("turn on/off led");
        char* num = strtok(NULL, delim);
        bool power = true;
        if(atoi(num) == 0)
            power = false; 
        response = strip.setLed(power);
    }
    else if(strcmp(first_arg, "time") == 0)
    {
        Serial.println("time");
        response = strip.get_time();
    }    
    else if(strcmp(first_arg, "timezone") == 0)
    {
        Serial.println("timezone");
        response = strip.get_timezone();
    }
    else if(strcmp(first_arg, "reset") == 0)
    {
        Serial.println("reset");
        response = strip.reset_to_factory_settings();      
    }
    else if(strcmp(first_arg, "settimezone") == 0)
    {
        Serial.println("settimezone");
        char* num = strtok(NULL, delim);      
        response = strip.set_timezone(String(num));
    }
    else if(strcmp(first_arg, "getcountdown") == 0)
    {
        Serial.println("getcountdown");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        response = strip.get_countdown(ids[ind]);        
    }
    else if(strcmp(first_arg, "cancelcountdown") == 0)
    {
        Serial.println("cancelcountdown");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        response = strip.cancel_countdown(ids[ind]);        
    }
    else if(strcmp(first_arg, "setcountdown") == 0)
    {
        Serial.println("setcountdown");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        char* duration = strtok(NULL, delim);
        char* power = strtok(NULL, delim);
        if(strcmp(power, "on") == 0)
            response = strip.set_countdown(ids[ind], true, duration);   
        else
            response = strip.set_countdown(ids[ind], false, duration);
    }
    else if(strcmp(first_arg, "getEmeterGain") == 0)
    {
        Serial.println("getEmeterGain");
        char* num = strtok(NULL, delim);
        int ind = atoi(num)-1;
        response = strip.get_emeter_gain(ids[ind]);
    }
    else
    {
        response = "No such command";      
    }
    Serial.println(response);
    client.publish(result_topic, response.c_str());   
}

void loop()
{
    client.loop();
    delay(1000);
}
