package com.example.mckunda.iot_controlpanel;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.EditText;

import com.example.mckunda.iot_controlpanel.R;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.MqttException;

import java.io.UnsupportedEncodingException;

public class MainActivity extends AppCompatActivity {
//    protected boolean isShowAlert = true;
//    private int oldOrientation;
    private WebView webv;
    private MqttAndroidClient client;
    private PahoMqttClient pahoMqttClient;

    private Button buttonTimeout, buttonSetTimeoutLength, buttonAlarm;

    private EditText editTimeoutLength;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        pahoMqttClient = new PahoMqttClient();

        buttonTimeout = (Button) findViewById(R.id.buttonTimeout);
        buttonSetTimeoutLength = (Button) findViewById(R.id.buttonSetTimeoutLength);
        buttonAlarm = (Button) findViewById(R.id.buttonAlarm);

        editTimeoutLength = (EditText) findViewById(R.id.editTimeoutLength);

        webv = (WebView) findViewById(R.id.webView);
        webv.getSettings().setLoadWithOverviewMode(true);
        webv.getSettings().setUseWideViewPort(true);
        webv.loadUrl(Constants.CAMERA_URL);

        client = pahoMqttClient.getMqttClient(getApplicationContext(), Constants.MQTT_BROKER_URL, Constants.CLIENT_ID);

        buttonTimeout.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    pahoMqttClient.publishMessage(client, new  String("Timeout"), 1, Constants.PUBLISH_TOPIC_CAMERA);
                } catch (MqttException e) {
                    e.printStackTrace();
                } catch (UnsupportedEncodingException e) {
                    e.printStackTrace();
                }
            }
        });

        buttonSetTimeoutLength.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String msg = editTimeoutLength.getText().toString().trim();
                try {
                    pahoMqttClient.publishMessage(client, new String("SetTimeoutLength=") + msg, 1, Constants.PUBLISH_TOPIC_CAMERA);
                } catch (MqttException e) {
                    e.printStackTrace();
                } catch (UnsupportedEncodingException e) {
                    e.printStackTrace();
                }
            }
        });

        buttonAlarm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    pahoMqttClient.publishMessage(client, new  String("Alarm"), 1, Constants.PUBLISH_TOPIC_ALARM);
                } catch (MqttException e) {
                    e.printStackTrace();
                } catch (UnsupportedEncodingException e) {
                    e.printStackTrace();
                }
            }
        });

        Intent intent = new Intent(MainActivity.this, MqttMessageService.class);
        startService(intent);

    }

    @Override
    protected void onStop() {
        super.onStop();
        AppHideHandler();
    }

    @Override
    protected void onResume() {
        super.onResume();
        webv.reload();
    }

    public void AppHideHandler() {
        webv.stopLoading();
    }
}
