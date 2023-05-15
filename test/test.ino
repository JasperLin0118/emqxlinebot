#include <PubSubClient.h>
#include "Controller.h"
#include <WiFi.h>
#include <WiFiClient.h>

const char* ssid = "ICE CREAM DELIVERY";
const char* password = "ILOVENAKO";

// MQTT Broker
const char* mqtt_broker = "broker.emqx.io";
const char* topic = "esp32/smartstrip";
const char* result_topic = "esp32/result";
const char* mqtt_username = "emqx";
const char* mqtt_password = "public";
const int mqtt_port = 1883;

//smartstrip
IPAddress stripIP = {192, 168, 31, 9};
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
    // if(strcmp(first_arg, "getEmeter") == 0)
    // {  
    //     Serial.println("getEmeter");
    //     String response = strip.getEmeter();
    //     if (response == "")
    //         client.publish(result_topic, "No response from plug or not connected");
    //     else
    //         client.publish(result_topic, response.c_str());
    // }
    if(strcmp(first_arg, "getEmeter") == 0)
    {
        Serial.println("getEmeter");
        char* num = strtok(NULL, delim);
        int ind = atoi(num);
        String response = strip.getEmeter(ids[ind]);
        if (response == "")
            client.publish(result_topic, "No response from plug or not connected");
        else
            client.publish(result_topic, response.c_str());
    }
    else if(strcmp(first_arg, "getInfo") == 0)
    {
        Serial.println("getInfo");
        String response = strip.getInfo();
        if (response == "")
            client.publish(result_topic, "No response from plug or not connected");
        else
            client.publish(result_topic, response.c_str());
    }
    else if(strcmp(first_arg, "turnoff") == 0)
    {
        Serial.println("turnoff");
        char* num = strtok(NULL, delim);
        int ind = atoi(num);
        String response = strip.turn_off(ids[ind]);
        if (response == "")
            client.publish(result_topic, "No response from plug or not connected");
        else
            client.publish(result_topic, response.c_str());
    }
    else if(strcmp(first_arg, "turnon") == 0)
    {
        Serial.println("turnon");
        char* num = strtok(NULL, delim);
        int ind = atoi(num);
        String response = strip.turn_on(ids[ind]);
        if (response == "")
            client.publish(result_topic, "No response from plug or not connected");
        else
            client.publish(result_topic, response.c_str());
    }
    else if(strcmp(first_arg, "exit") == 0)
    {
          Serial.println("exit");
          client.publish(result_topic, (const uint8_t*)"exit", 4, false);
    }
    else
    {
          Serial.println("No such command");
          client.publish(result_topic, (const uint8_t*)"No such command", 15, false);
    }
      
}

void loop()
{
    client.loop();
    delay(1000);
}
