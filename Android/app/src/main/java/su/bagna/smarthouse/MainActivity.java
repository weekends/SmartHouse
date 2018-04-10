package su.bagna.smarthouse;

import android.app.Activity;
import android.content.Intent;
import android.preference.Preference;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.Window;
import android.webkit.CookieManager;
import android.webkit.HttpAuthHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebViewDatabase;
import android.widget.Toast;

import java.util.Set;

public class MainActivity extends AppCompatActivity {
    //private final String HOST = "house.bagna.su:4433";
    private String HOST = "";
    private String USERNAME = "";
    private String PASSWORD = "";
    private String URL = "";

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setFeatureInt(Window.FEATURE_PROGRESS, Window.PROGRESS_VISIBILITY_ON);
        setContentView(R.layout.activity_main);

        webView = (WebView) findViewById(R.id.WebViewActivity);
        webView.getSettings().setJavaScriptEnabled(true);

        final Activity activity = this;
        webView.setWebChromeClient(new WebChromeClient() {
            public void onProgressChanged(WebView view, int progress) {
                activity.setTitle(getString(R.string.loading));
                activity.setProgress(progress * 1000);

                if (progress == 100) activity.setTitle(R.string.app_name);
            }
        });
        webView.setWebViewClient(new WebViewClient() {
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                Toast.makeText(activity, "Oh no! " + description, Toast.LENGTH_SHORT).show();
            }
        });
    }

    protected void setBasicAuth() {
        USERNAME = SettingsActivity.getUserName(this);
        PASSWORD = SettingsActivity.getUserPassword(this);

        WebViewDatabase.getInstance(this).clearHttpAuthUsernamePassword();
        webView.setHttpAuthUsernamePassword(HOST, HOST, USERNAME, PASSWORD);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedHttpAuthRequest(WebView view, HttpAuthHandler handler, String host, String realm) {
                String[] up = view.getHttpAuthUsernamePassword(host, realm);
                handler.proceed(USERNAME, PASSWORD);
                if (up != null && up.length == 2) {
                    handler.proceed(up[0], up[1]);
                } else {
                    Log.d("", "Could not find username/password for domain: " + host + ", with realm = " + realm);
                }
            }
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        super.onCreateOptionsMenu(menu);
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.host_settings:
                startActivity(new Intent(this, SettingsActivity.class));
                return true;

            case R.id.exit:
                finish();
                return true;

            default:
                return super.onOptionsItemSelected(item);

        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        webView.clearCache(true);
        HOST = SettingsActivity.getHostName(this);
        URL = "http://" + HOST + "/";

        setBasicAuth();
        webView.loadUrl(URL);
    }
}
