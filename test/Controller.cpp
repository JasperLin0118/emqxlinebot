#include "Controller.h"

Controller::Controller(IPAddress ip, uint16_t port)
{
    targetIP = ip;
    targetPort = port;
}

void Controller::serializeUint32(char (&buf)[4], uint32_t val)
{
    buf[0] = (val >> 24) & 0xff;
    buf[1] = (val >> 16) & 0xff;
    buf[2] = (val >> 8) & 0xff;
    buf[3] = val & 0xff;
}

void Controller::decrypt(char* input, uint16_t length)
{
    uint8_t key = 171;
    uint8_t next_key;
    for (uint16_t i = 0; i < length; i++) {
        next_key = input[i];
        input[i] = key ^ input[i];
        key = next_key;
    }
}

void Controller::encrypt(char* data, uint16_t length)
{
    uint8_t key = 171;
    for (uint16_t i = 0; i < length + 1; i++) {
        data[i] = key ^ data[i];
        key = data[i];
    }
}

void Controller::encryptWithHeader(char* out, char* data, uint16_t length)
{
    char serialized[4];
    serializeUint32(serialized, length);
    encrypt(data, length);
    memcpy(out, &serialized, 4);
    memcpy(out + 4, data, length);
}

String Controller::getInfo()
{
    const String cmd = "{\"system\":{\"get_sysinfo\":{}}}";
    return sendCmd(cmd);
}

String Controller::getEmeter(String id)
{
    const String cmd = "{\"context\":{\"child_ids\":[\"" + id + "\"]},\"emeter\":{\"get_realtime\":{}}}";
    //const String cmd = "{\"emeter\":{\"get_realtime\":{}}}";
    return sendCmd(cmd);
}

String Controller::setLed(bool power)
{
    String cmd = "{\"system\":{\"set_led_off\":{\"off\":1}}}";
    if (power) 
        cmd = "{\"system\":{\"set_led_off\":{\"off\":0}}}";
    return sendCmd(cmd);
}

String Controller::turn_off(String id)
{
    String cmd = "{\"context\":{\"child_ids\":[\"" + id + "\"]},\"system\":{\"set_relay_state\":{\"state\":0}}}}";
    return sendCmd(cmd);
}

String Controller::turn_on(String id)
{
    String cmd = "{\"context\":{\"child_ids\":[\"" + id + "\"]},\"system\":{\"set_relay_state\":{\"state\":1}}}}";
    return sendCmd(cmd);
}

String Controller::sendCmd(String cmd)
{
    char encrypted[cmd.length() + 4];
    encryptWithHeader(encrypted, const_cast<char*>(cmd.c_str()), cmd.length());
    char response[2048] = { 0 };
    uint16_t length = this->tcpConnect(response, encrypted, cmd.length() + 4, 5000);
    if (length > 0)
        decrypt(response, length - 4);
    else
        return String("failed");
    return String(response);
}

uint16_t Controller::tcpConnect(char* out, const char* cmd, uint16_t length, unsigned long timeout_millis)
{
    WiFiClient plug_client;
    if (plug_client.connect(targetIP, targetPort)) 
    {
        delay(10);
        plug_client.write(cmd, length); //send message
        delay(500);// give the device some time to response
        uint16_t start = millis();
        char buf[2048] = { 0 };
        while(plug_client.connected()) 
        {
            if(plug_client.available()) // if there's message unread
            {
                delay(10);
                int len = plug_client.read((uint8_t*)buf, 2048);
                // necessary for decryption
                // buf + 4 strips 4 byte header
                // valread - 3 leaves 1 byte for terminating null character
                strncpy(out, buf + 4, len - 3);
                delay(10);
                plug_client.flush();
                return len;
            }
            if (millis() - start >= timeout_millis)// connection timeout
                break;
        }
        // timeout/not connected
        delay(10);
        plug_client.flush();
    }
    return 0;
}
