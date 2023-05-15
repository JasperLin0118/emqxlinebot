#ifndef CONTROLLER_H
#define CONTROLLER_H

#include <Arduino.h>
#include <WiFiClient.h>

class Controller {

private:
    IPAddress targetIP;
    uint16_t targetPort;
    static void serializeUint32(char (&buf)[4], uint32_t val);
    static void encrypt(char* data, uint16_t length);
    static void encryptWithHeader(char* out, char* data, uint16_t length);
    static void decrypt(char* input, uint16_t length);
    uint16_t tcpConnect(char* out, const char* cmd, uint16_t length, unsigned long timeout_millis);

public:
    Controller(IPAddress ip, uint16_t port);
    String sendCmd(String cmd);
    String getEmeter(String id);
    String getInfo();
    String setLed(bool power);
    String turn_off(String id);
    String turn_on(String id);
};

#endif
